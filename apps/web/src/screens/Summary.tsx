import { useCallback, useEffect, useState } from "react";
import {
  adjustWorkout,
  getWorkout,
  overrideDecision,
  type Adjustment,
  type Reward,
  type Workout,
} from "../api";
import { planPercent, repTarget } from "../cycle/progress";
import type { Session } from "../cycle/session";
import { t } from "../i18n";
import { targetLine } from "../messages";
import { Button, Card, Skeleton, Stepper, Tag } from "../ui/ui";
import { RatingBar } from "./AdjustmentView";
import { RewardSummary } from "./RewardSummary";

type Props = { session: Session; reward: Reward; onDone: () => void };

const kg = (value: number | null) => (value === null ? "—" : String(value).replace(".", ","));

const ACTION_LABEL: Record<string, string> = {
  increase: t.cycle.summary.actions.increase,
  hold: t.cycle.summary.actions.hold,
  reduce: t.cycle.summary.actions.reduce,
  reset: t.cycle.summary.actions.reduce,
  deload: t.cycle.summary.actions.deload,
};

/** Итог тренировки: план против факта, решения движка с причинами, «Принять» или «Изменить». */
export function Summary({ session, reward, onDone }: Props) {
  const c = t.cycle.summary;
  const { workoutId, items } = session;
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [adjustment, setAdjustment] = useState<Adjustment | null>(null);
  const [failed, setFailed] = useState(false);
  const [accepted, setAccepted] = useState<Set<number>>(new Set());
  const [editing, setEditing] = useState<number | null>(null);
  const [newWeight, setNewWeight] = useState(0);
  const [reason, setReason] = useState("");
  const [changed, setChanged] = useState<Set<number>>(new Set());

  const load = useCallback(() => {
    setFailed(false);
    getWorkout(workoutId)
      .then(setWorkout)
      .catch(() => undefined);
    adjustWorkout(workoutId, items)
      .then(setAdjustment)
      .catch(() => setFailed(true));
  }, [workoutId, items]);

  useEffect(load, [load]);

  const factByExercise: Record<number, number[]> = {};
  for (const s of workout?.sets ?? []) {
    if (s.reps !== null) (factByExercise[s.exercise_id] ??= []).push(s.reps);
  }
  const percent = planPercent(items, factByExercise);
  const setsCount = workout?.sets.length ?? 0;
  const minutes = workout?.duration_min ? ` · ${workout.duration_min} мин` : "";

  async function saveChange(exerciseId: number) {
    try {
      const updated = await overrideDecision(workoutId, exerciseId, newWeight, reason);
      setAdjustment(updated);
      setChanged((prev) => new Set(prev).add(exerciseId));
      setAccepted((prev) => new Set(prev).add(exerciseId));
      setEditing(null);
      setReason("");
    } catch {
      setFailed(true);
    }
  }

  return (
    <main className="summary">
      <p className="kicker">{c.kicker(session.title, minutes, setsCount, percent)}</p>
      <h1>{c.title}</h1>

      <Card>
        <table className="result-table">
          <thead>
            <tr>
              <th>{c.table.exercise}</th>
              <th>{c.table.plan}</th>
              <th>{c.table.fact}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const fact = factByExercise[item.exercise_id] ?? [];
              const plan = Array.from({ length: item.sets }, (_, i) => repTarget(item, i));
              const below = fact.some((reps, i) => reps < (plan[i] ?? 0)) || fact.length < item.sets;
              return (
                <tr key={item.exercise_id}>
                  <td>
                    {item.name}
                    {item.target_weight_kg !== null && ` · ${kg(item.target_weight_kg)}`}
                  </td>
                  <td className="num">{plan.join("/")}</td>
                  <td className={`num ${below ? "below" : "above"}`}>{fact.length ? fact.join("/") : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>

      <h3>
        {c.decisions}
        {adjustment ? ` · ${adjustment.engine.length}` : ""}
      </h3>

      {!adjustment && !failed && (
        <>
          <p role="status">{c.loading}</p>
          <Skeleton height={120} />
        </>
      )}
      {failed && (
        <Card>
          <p role="alert">{c.error}</p>
          <Button variant="secondary" onClick={load}>
            {c.retry}
          </Button>
        </Card>
      )}

      {adjustment?.engine.map((d) => {
        const next = adjustment.next_workout.find((n) => n.exercise_id === d.exercise_id);
        const isAccepted = accepted.has(d.exercise_id);
        return (
          <Card key={d.exercise_id} accent={d.action === "increase"}>
            <div className="row">
              <b>{d.name}</b>
              <Tag tone={d.action === "increase" ? "fit" : "info"}>{ACTION_LABEL[d.action] ?? d.action}</Tag>
            </div>
            {next && <p className="big-line num">{targetLine(next)}</p>}
            <p>
              <b>{c.why}:</b> {d.reason}
            </p>
            {changed.has(d.exercise_id) && <p className="muted">{c.changed}</p>}

            {editing === d.exercise_id ? (
              <div className="custom">
                <Stepper
                  label={c.newWeight}
                  value={newWeight}
                  min={0}
                  max={500}
                  step={2.5}
                  format={kg}
                  onChange={setNewWeight}
                />
                <input
                  value={reason}
                  maxLength={200}
                  placeholder={c.reason}
                  onChange={(e) => setReason(e.target.value)}
                />
                <div className="two">
                  <Button onClick={() => void saveChange(d.exercise_id)}>{c.saveChange}</Button>
                  <Button variant="secondary" onClick={() => setEditing(null)}>
                    {c.cancel}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="two">
                <Button
                  variant={isAccepted ? "secondary" : "primary"}
                  disabled={isAccepted}
                  onClick={() => setAccepted((prev) => new Set(prev).add(d.exercise_id))}
                >
                  {isAccepted ? c.accepted : c.accept}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setNewWeight(next?.target_weight_kg ?? d.next_weight_kg ?? 0);
                    setEditing(d.exercise_id);
                  }}
                >
                  {c.change}
                </Button>
              </div>
            )}
          </Card>
        );
      })}

      {adjustment && (
        <Card>
          <h3>{c.why}</h3>
          <p>{adjustment.rationale}</p>
          <small className="muted">
            {adjustment.explained_by === "llm" ? t.adjust.byLlm : t.adjust.byTemplate}
          </small>
          {adjustment.health_flag && <p className="levelup">{t.adjust.pain}</p>}
          <small>{t.adjust.disclaimer}</small>
        </Card>
      )}

      <RewardSummary reward={reward} />
      {adjustment && <RatingBar workoutId={workoutId} />}
      <Button onClick={onDone}>{c.done}</Button>
    </main>
  );
}
