import { useCallback, useEffect, useState } from "react";
import { adjustWorkout, rateAdjustment, type AdjustRating, type Adjustment } from "../api";
import { t } from "../i18n";
import { targetLine } from "../messages";

type Props = { workoutId: number };

type State =
  | { kind: "loading" }
  | { kind: "ready"; adjustment: Adjustment }
  | { kind: "error"; message: string };

function errorMessage(error: unknown): string {
  const text = error instanceof Error ? error.message : "";
  if (text.includes("429")) return t.adjust.limit;
  if (text.includes("422")) return t.adjust.noStrength;
  if (text.includes("503")) return t.adjust.unavailable;
  return t.adjust.error;
}

const RATINGS: AdjustRating[] = ["fits", "too_hard", "too_easy"];

export function RatingBar({ workoutId }: Props) {
  const [status, setStatus] = useState<"idle" | "sent" | "error">("idle");

  const send = (rating: AdjustRating) =>
    rateAdjustment(workoutId, rating)
      .then(() => setStatus("sent"))
      .catch(() => setStatus("error"));

  if (status === "sent") return <p role="status">{t.adjust.rate.thanks}</p>;
  return (
    <div>
      <h3>{t.adjust.rate.title}</h3>
      <div className="chips">
        {RATINGS.map((rating) => (
          <button key={rating} type="button" className="ghost" onClick={() => send(rating)}>
            {t.adjust.rate[rating]}
          </button>
        ))}
      </div>
      {status === "error" && <p role="alert">{t.adjust.rate.error}</p>}
    </div>
  );
}

export function AdjustmentView({ workoutId }: Props) {
  const [state, setState] = useState<State>({ kind: "loading" });

  const load = useCallback(() => {
    setState({ kind: "loading" });
    adjustWorkout(workoutId)
      .then((adjustment) => setState({ kind: "ready", adjustment }))
      .catch((error) => setState({ kind: "error", message: errorMessage(error) }));
  }, [workoutId]);

  useEffect(load, [load]);

  if (state.kind === "loading") return <p role="status">{t.adjust.loading}</p>;
  if (state.kind === "error") {
    return (
      <section>
        <p role="alert">{state.message}</p>
        <button type="button" onClick={load}>
          {t.adjust.retry}
        </button>
      </section>
    );
  }

  const { adjustment } = state;
  // Расчёт движка показываем, если он не повторяет уже выведенные факты (при шаблоне они совпадают).
  const engineLines = adjustment.engine
    .map((d) => d.reason)
    .filter((reason) => !adjustment.changes.includes(reason));
  return (
    <section>
      <h2>{t.adjust.title}</h2>
      {adjustment.health_flag && <p className="levelup">{t.adjust.pain}</p>}
      <div className="chips">
        <span className="chip lime">{t.adjust.decisions[adjustment.decision]}</span>
      </div>

      <h3>{t.adjust.changes}</h3>
      <ul className="list">
        {adjustment.changes.map((change) => (
          <li key={change}>{change}</li>
        ))}
      </ul>

      {engineLines.length > 0 && (
        <>
          <h3>{t.adjust.engineTitle}</h3>
          <ul className="list">
            {engineLines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          <small>{t.adjust.engineHint}</small>
        </>
      )}

      <h3>{t.adjust.target}</h3>
      <ul className="list">
        {adjustment.next_workout.map((item) => (
          <li key={item.exercise_id}>
            {item.name}: {targetLine(item)}
          </li>
        ))}
      </ul>

      <h3>{t.adjust.why}</h3>
      <p>{adjustment.rationale}</p>
      <small>
        {adjustment.explained_by === "llm" ? t.adjust.byLlm : t.adjust.byTemplate}
      </small>
      <small>{t.adjust.disclaimer}</small>
      <RatingBar workoutId={workoutId} />
    </section>
  );
}
