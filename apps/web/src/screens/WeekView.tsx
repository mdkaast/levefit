import { useCallback, useEffect, useState } from "react";
import {
  getDirections,
  getWeek,
  putDirections,
  type DirectionsState,
  type WeekPlan,
  type WeekSession,
} from "../api";
import { t } from "../i18n";
import { Button, Card, Chip, ListRow, Skeleton, Tag } from "../ui/ui";
import { warningText } from "./WeekChanges";

type Props = { onCustomize: () => void };

const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

function sessionHint(session: WeekSession): string {
  const w = t.directions.week;
  if (session.kind === "strength") {
    const sets = session.exercises.reduce((sum, e) => sum + e.sets, 0);
    return `${w.exercises(session.exercises.length)} · ${w.sets(sets)}`;
  }
  return session.minutes ? w.minutes(session.minutes) : "";
}

/** Неделя: что и когда тренируем, подробности по касанию; здесь же переход на программу. */
export function WeekView({ onCustomize }: Props) {
  const w = t.directions.week;
  const [offset, setOffset] = useState<0 | 1>(0);
  const [plan, setPlan] = useState<WeekPlan | null>(null);
  const [state, setState] = useState<DirectionsState | null>(null);
  const [open, setOpen] = useState<number | null>(null);
  const [failed, setFailed] = useState(false);

  const load = useCallback(() => {
    setFailed(false);
    setPlan(null);
    getWeek(offset)
      .then(setPlan)
      .catch(() => setFailed(true));
    getDirections()
      .then(setState)
      .catch(() => undefined);
  }, [offset]);

  useEffect(load, [load]);

  async function goProgram() {
    if (!state) return;
    await putDirections(state.mine).catch(() => undefined);
    load();
  }

  if (failed) return <p className="muted">{t.directions.loadError}</p>;
  if (!plan) return <Skeleton height={160} />;

  const names = Object.fromEntries(
    (state?.catalog ?? []).flatMap((c) => c.options.map((o) => [o.key, o.name] as const)),
  );
  return (
    <>
      <div className="chip-row">
        <Chip selected={offset === 0} onClick={() => setOffset(0)}>
          {w.current}
        </Chip>
        <Chip selected={offset === 1} onClick={() => setOffset(1)}>
          {w.next}
        </Chip>
      </div>

      {!plan.follows_week && state && (
        <Card accent>
          <h3>{w.goProgram}</h3>
          <p className="muted">{w.goProgramHint}</p>
          <Button onClick={goProgram}>{w.goProgram}</Button>
        </Card>
      )}

      <div className="stack">
        {plan.days.map((day) => {
          const session = day.session;
          const isToday = plan.offset === 0 && day.date === plan.today;
          const accents = session?.exercises.filter((e) => e.accent) ?? [];
          return (
            <div key={day.date}>
              <ListRow
                title={`${WEEKDAYS[day.weekday]} · ${session ? session.title : w.rest}`}
                hint={session ? sessionHint(session) : undefined}
                trailing={
                  <>
                    {isToday && <Tag tone="fit">{t.cycle.today.title}</Tag>}
                    {accents.length > 0 && <Tag tone="info">{w.accentBadge}</Tag>}
                  </>
                }
                onClick={session ? () => setOpen(open === day.weekday ? null : day.weekday) : undefined}
              />
              {session && open === day.weekday && (
                <div className="week-detail">
                  {session.exercises.map((e) => (
                    <div key={e.slug} className="row">
                      <span>{e.accent ? `${e.name} · ${w.accentBadge}` : e.name}</span>
                      <b className="num">
                        {e.sets} × {e.reps[0] === e.reps[1] ? e.reps[0] : `${e.reps[0]}–${e.reps[1]}`}
                        {e.unit === "sec" ? " с" : ""}
                      </b>
                    </div>
                  ))}
                  {session.blocks.map((block) => (
                    <small key={block} className="muted">
                      {block}
                    </small>
                  ))}
                  {!session.verified && session.kind === "session" && (
                    <small className="muted">{w.draft}</small>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {plan.warnings.map((code) => (
        <p key={code} className="warn">
          {warningText(code, names)}
        </p>
      ))}
      <Button variant="secondary" onClick={onCustomize}>
        {w.customize}
      </Button>
    </>
  );
}
