import { useEffect, useRef, useState } from "react";
import {
  finishWorkout,
  getLastSession,
  getWorkout,
  listRatings,
  type ExerciseRatingValue,
  type LastSession,
  type Reward,
} from "../api";
import { DEFAULT_REST_S, clock, deltaLabel, locate, repTarget, repsLine } from "../cycle/progress";
import { clearSession, saveSession, type Session } from "../cycle/session";
import { t } from "../i18n";
import { targetLine } from "../messages";
import { newId } from "../offline";
import { haptic } from "../prefs";
import { queue } from "../queue";
import { Button, Chip, ProgressRing, Stepper } from "../ui/ui";

type Logged = { id: string; weight: number | null; reps: number; pending: boolean };

type Props = {
  session: Session;
  onFinished: (reward: Reward) => void;
  onExit: () => void;
};

const kg = (value: number | null) => (value === null ? "—" : String(value).replace(".", ","));

/** Активная тренировка: подходы, отдых и оценка упражнения. Записи идут через офлайн-очередь. */
export function ActiveWorkout({ session: initial, onFinished, onExit }: Props) {
  const c = t.cycle;
  const [session, setSession] = useState(initial);
  const { items, workoutId } = session;
  const [logged, setLogged] = useState<Record<number, Logged[]>>({});
  const [rated, setRated] = useState<Set<number>>(new Set());
  const [ready, setReady] = useState(false);
  const [weights, setWeights] = useState<Record<number, number>>({});
  const [custom, setCustom] = useState(false);
  const [customReps, setCustomReps] = useState(1);
  const [lastSessions, setLastSessions] = useState<Record<number, LastSession | null>>({});
  const [now, setNow] = useState(Date.now());
  const [pendingCount, setPendingCount] = useState(queue.pending(workoutId).length);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastNote, setLastNote] = useState<string | null>(null);
  const finishing = useRef(false);

  // Восстановление после запуска или сворачивания: подходы с сервера плюс то, что ещё в очереди.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const byExercise: Record<number, Logged[]> = {};
      const ratedIds = new Set<number>();
      try {
        const workout = await getWorkout(workoutId);
        for (const s of workout.sets) {
          if (s.reps === null) continue;
          (byExercise[s.exercise_id] ??= []).push({
            id: `srv-${s.id}`,
            weight: s.weight_kg,
            reps: s.reps,
            pending: false,
          });
        }
        (await listRatings(workoutId)).forEach((r) => ratedIds.add(r.exercise_id));
      } catch {
        // нет связи: показываем то, что есть на устройстве
      }
      for (const op of queue.pending(workoutId)) {
        if (op.kind === "set") {
          const p = op.payload as { exercise_id: number; weight_kg?: number; reps?: number };
          (byExercise[p.exercise_id] ??= []).push({
            id: op.id,
            weight: p.weight_kg ?? null,
            reps: p.reps ?? 0,
            pending: true,
          });
        } else {
          ratedIds.add(op.exerciseId);
        }
      }
      if (!cancelled) {
        setLogged(byExercise);
        setRated(ratedIds);
        setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [workoutId]);

  // Очередь сообщает, что что-то отправилось: снимаем пометку «в очереди».
  useEffect(
    () =>
      queue.subscribe(() => {
        const waiting = new Set(queue.pending(workoutId).map((op) => op.id));
        setPendingCount(waiting.size);
        setLogged((prev) =>
          Object.fromEntries(
            Object.entries(prev).map(([id, rows]) => [
              id,
              rows.map((row) => ({ ...row, pending: waiting.has(row.id) })),
            ]),
          ),
        );
      }),
    [workoutId],
  );

  const counts = Object.fromEntries(items.map((i) => [i.exercise_id, (logged[i.exercise_id] ?? []).length]));
  const pos = locate(items, counts);
  const current = items[pos.exercise];
  const allDone = ready && items.length > 0 && items.every((i) => counts[i.exercise_id] >= i.sets);
  const unrated = items.find((i) => counts[i.exercise_id] >= i.sets && !rated.has(i.exercise_id));
  const resting = Boolean(session.restEnd && session.restEnd > now);
  const restLeft = session.restEnd ? Math.max(0, Math.ceil((session.restEnd - now) / 1000)) : 0;

  // Часы: раз в секунду, а во время отдыха чаще, чтобы тики шли ровно.
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), resting ? 250 : 1000);
    return () => clearInterval(timer);
  }, [resting]);

  // Конец отдыха и тактильные тики последних пяти секунд.
  useEffect(() => {
    if (!session.restEnd) return;
    if (session.restEnd <= now) {
      haptic("success");
      persist({ ...session, restEnd: undefined, restTotal: undefined });
    } else if (restLeft <= 5) {
      haptic("light");
    }
  }, [restLeft, session.restEnd]);

  // «Призрак» прошлой попытки для текущего упражнения.
  useEffect(() => {
    if (!current || current.exercise_id in lastSessions) return;
    const id = current.exercise_id;
    getLastSession(id)
      .then((value) => setLastSessions((prev) => ({ ...prev, [id]: value })))
      .catch(() => setLastSessions((prev) => ({ ...prev, [id]: null })));
  }, [current, lastSessions]);

  // Все упражнения выполнены и оценены (или оценка пропущена): завершаем тренировку.
  useEffect(() => {
    if (allDone && !unrated && !finishing.current) void finish();
  }, [allDone, unrated]);

  function persist(next: Session) {
    setSession(next);
    saveSession(next);
  }

  function startRest(seconds: number) {
    persist({ ...session, restEnd: Date.now() + seconds * 1000, restTotal: seconds });
  }

  function changeRest(delta: number) {
    if (!session.restEnd || !session.restTotal) return;
    const total = Math.max(15, session.restTotal + delta);
    persist({ ...session, restEnd: session.restEnd + (total - session.restTotal) * 1000, restTotal: total });
  }

  const lastOfCurrent = current ? lastSessions[current.exercise_id] : null;
  const loggedRows = current ? (logged[current.exercise_id] ?? []) : [];
  const weight = current ? weights[current.exercise_id] : undefined;
  const shownWeight =
    weight ??
    loggedRows[loggedRows.length - 1]?.weight ??
    current?.target_weight_kg ??
    lastOfCurrent?.top_weight_kg ??
    20;

  async function record(reps: number) {
    if (!current || reps < 1) return;
    const w = shownWeight > 0 ? shownWeight : null;
    const id = newId();
    const target = repTarget(current, pos.set);
    setLogged((prev) => ({
      ...prev,
      [current.exercise_id]: [...(prev[current.exercise_id] ?? []), { id, weight: w, reps, pending: true }],
    }));
    setLastNote(`${kg(w)} × ${reps} · ${deltaLabel(reps, target)}`);
    setCustom(false);
    haptic("medium");
    if (pos.set + 1 < current.sets) startRest(DEFAULT_REST_S);
    const result = await queue.submit({
      id,
      kind: "set",
      workoutId,
      payload: {
        exercise_id: current.exercise_id,
        ...(w !== null ? { weight_kg: w } : {}),
        reps,
        client_id: id,
      },
    });
    if (result === "sent") {
      setLogged((prev) => ({
        ...prev,
        [current.exercise_id]: (prev[current.exercise_id] ?? []).map((row) =>
          row.id === id ? { ...row, pending: false } : row,
        ),
      }));
    }
  }

  function saveRating(exerciseId: number, rating: ExerciseRatingValue, pain: boolean) {
    setRated((prev) => new Set(prev).add(exerciseId));
    void queue.submit({ id: newId(), kind: "rating", workoutId, exerciseId, rating, pain });
  }

  async function finish() {
    finishing.current = true;
    setBusy(true);
    setError(null);
    await queue.flush();
    if (queue.pending(workoutId).length > 0) {
      setError(c.workout.syncLeft);
      setBusy(false);
      finishing.current = false;
      return;
    }
    try {
      const result = await finishWorkout(workoutId);
      clearSession();
      haptic("success");
      onFinished(result.reward);
    } catch {
      setError(c.workout.finishError);
      setBusy(false);
      finishing.current = false;
    }
  }

  if (!ready) return <p className="status-screen">{t.loading}</p>;

  // ---------- оценка упражнения (шторка) ----------
  const sheet = unrated && (
    <RateSheet
      key={unrated.exercise_id}
      name={unrated.name}
      line={`${kg(
        (logged[unrated.exercise_id] ?? []).at(-1)?.weight ?? unrated.target_weight_kg,
      )} × ${repsLine(logged[unrated.exercise_id] ?? [])}`}
      last={items.indexOf(unrated) === items.length - 1}
      onSave={(rating, pain) => saveRating(unrated.exercise_id, rating, pain)}
      onSkip={() => setRated((prev) => new Set(prev).add(unrated.exercise_id))}
    />
  );

  // ---------- отдых ----------
  if (resting && current && !unrated) {
    const total = session.restTotal ?? DEFAULT_REST_S;
    return (
      <main className="rest">
        <p className="kicker">{c.rest.kicker(current.name, pos.set)}</p>
        {lastNote && <p className="note">{lastNote}</p>}
        <ProgressRing value={restLeft / total} size={260} label={c.rest.over}>
          <span className="rest-clock">{clock(restLeft)}</span>
          <small>{c.rest.of(clock(total))}</small>
        </ProgressRing>
        <div className="two">
          <Button variant="secondary" onClick={() => changeRest(-15)}>
            {c.rest.minus}
          </Button>
          <Button variant="secondary" onClick={() => changeRest(15)}>
            {c.rest.plus}
          </Button>
        </div>
        <div className="effect">
          <small>{c.rest.nextTitle}</small>
          <div className="row">
            <b>{c.rest.nextSet(pos.set + 1, current.sets)}</b>
            <b className="num">
              {kg(shownWeight)} × {repTarget(current, pos.set)}
            </b>
          </div>
          <p className="muted">{c.rest.hint}</p>
        </div>
        <Button onClick={() => persist({ ...session, restEnd: undefined, restTotal: undefined })}>
          {c.rest.early}
        </Button>
      </main>
    );
  }

  const elapsed = Math.floor((now - session.startedAt) / 1000);
  const upcoming = items.slice(pos.exercise + 1, pos.exercise + 3);
  const totalLogged = Object.values(counts).reduce((a, b) => a + b, 0);
  const offline = pendingCount > 0 || (typeof navigator !== "undefined" && !navigator.onLine);

  if (!current) return <p className="status-screen">{c.workout.notFound}</p>;

  return (
    <main className="workout">
      <div className="top-bar">
        <div>
          <small className="kicker">{c.workout.kicker(session.title, pos.exercise + 1, items.length)}</small>
          <b className="num">
            {clock(elapsed)} · {c.workout.setOf(Math.min(pos.set + 1, current.sets), current.sets)}
          </b>
        </div>
        <Button variant="secondary" onClick={onExit}>
          {c.workout.back}
        </Button>
      </div>

      {offline && (
        <div className="offline-bar" role="status">
          {c.workout.offline(pendingCount)}
        </div>
      )}

      <h1 className="ex-title">{current.name}</h1>
      <div className="chips">
        <Chip fit>
          {lastOfCurrent?.top_weight_kg != null &&
          current.target_weight_kg != null &&
          current.target_weight_kg > lastOfCurrent.top_weight_kg
            ? "↑ "
            : ""}
          {targetLine(current)}
        </Chip>
        {lastOfCurrent && (
          <Chip>
            {c.workout.last(`${kg(lastOfCurrent.top_weight_kg)} × ${repsLine(lastOfCurrent.sets)}`)}
          </Chip>
        )}
      </div>

      <div className="sets">
        {Array.from({ length: current.sets }, (_, j) => {
          const row = loggedRows[j];
          const target = repTarget(current, j);
          if (row) {
            return (
              <div key={j} className="set-row done">
                <span>{j + 1}</span>
                <b className="num">
                  {kg(row.weight)} × {row.reps}
                </b>
                <em>{row.pending ? c.workout.pending : deltaLabel(row.reps, target)}</em>
              </div>
            );
          }
          if (j !== pos.set || pos.finished) {
            return (
              <div key={j} className="set-row future">
                <span>{j + 1}</span>
                <b className="num">
                  {kg(shownWeight)} × {target}
                </b>
              </div>
            );
          }
          return (
            <div key={j} className="set-row current">
              <div className="row">
                <span>{j + 1}</span>
                <small>{c.workout.target}</small>
                <b className="num big">
                  {kg(shownWeight)} × {target}
                </b>
              </div>
              <Stepper
                label={c.workout.weight}
                value={shownWeight}
                min={0}
                max={500}
                step={2.5}
                format={kg}
                onChange={(v) => setWeights((prev) => ({ ...prev, [current.exercise_id]: v }))}
              />
              <Button onClick={() => record(target)}>✓ {c.workout.asPlan(target)}</Button>
              <div className="three">
                <Button variant="secondary" disabled={target - 1 < 1} onClick={() => record(target - 1)}>
                  −1
                </Button>
                <Button variant="secondary" disabled={target - 2 < 1} onClick={() => record(target - 2)}>
                  −2
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setCustomReps(target);
                    setCustom((v) => !v);
                  }}
                >
                  {c.workout.other}
                </Button>
              </div>
              {custom && (
                <div className="custom">
                  <Stepper label={c.workout.reps} value={customReps} min={1} max={100} onChange={setCustomReps} />
                  <Button onClick={() => record(customReps)}>{c.workout.record}</Button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {upcoming.length > 0 && (
        <div className="upcoming">
          <small>{c.workout.later}</small>
          {upcoming.map((item) => (
            <div key={item.exercise_id} className="row">
              <span>{item.name}</span>
              <span className="num muted">{targetLine(item)}</span>
            </div>
          ))}
        </div>
      )}

      {error && <p role="alert">{error}</p>}
      <p className="muted small">{c.workout.exitHint}</p>
      <div className="bottom-bar">
        <Button variant="secondary" loading={busy} disabled={totalLogged === 0} onClick={() => void finish()}>
          {busy ? c.workout.finishing : c.workout.finish}
        </Button>
      </div>
      {sheet}
    </main>
  );
}

type SheetProps = {
  name: string;
  line: string;
  last: boolean;
  onSave: (rating: ExerciseRatingValue, pain: boolean) => void;
  onSkip: () => void;
};

/** Оценка упражнения: одна на всё упражнение; «Тяжело» не позволит поднять вес, «Легко» ускорит. */
function RateSheet({ name, line, last, onSave, onSkip }: SheetProps) {
  const r = t.cycle.rate;
  const [rating, setRating] = useState<ExerciseRatingValue>("normal");
  const [pain, setPain] = useState(false);
  const options: ExerciseRatingValue[] = ["easy", "normal", "hard"];
  return (
    <div className="sheet-backdrop">
      <div className="sheet" role="dialog" aria-modal="true" aria-label={r.title}>
        <i className="grip" aria-hidden="true" />
        <small className="kicker">{r.kicker(name, line)}</small>
        <h2>{r.title}</h2>
        <p className="muted">{r.hint}</p>
        {options.map((key) => (
          <button
            key={key}
            type="button"
            className="rate-option"
            aria-pressed={rating === key}
            onClick={() => {
              haptic("select");
              setRating(key);
            }}
          >
            <span className="badge num">{r[key].badge}</span>
            <span>
              <b>{r[key].title}</b>
              <small>{r[key].text}</small>
            </span>
          </button>
        ))}
        <button type="button" className="pain-toggle" aria-pressed={pain} onClick={() => setPain((v) => !v)}>
          {r.pain}
        </button>
        {pain && <p className="muted small">{r.painNote}</p>}
        <Button
          onClick={() => {
            haptic("success");
            onSave(rating, pain);
          }}
        >
          {last ? r.saveLast : r.save}
        </Button>
        <Button variant="text" onClick={onSkip}>
          {t.cycle.rate.skip}
        </Button>
      </div>
    </div>
  );
}
