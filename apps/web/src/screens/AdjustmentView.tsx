import { useCallback, useEffect, useState } from "react";
import { adjustWorkout, type Adjustment } from "../api";
import { t } from "../i18n";

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
  return (
    <section>
      <h2>{t.adjust.title}</h2>
      <div className="chips">
        <span className="chip lime">{t.adjust.decisions[adjustment.decision]}</span>
      </div>

      <h3>{t.adjust.changes}</h3>
      <ul className="list">
        {adjustment.changes.map((change) => (
          <li key={change}>{change}</li>
        ))}
      </ul>

      <h3>{t.adjust.next}</h3>
      <ul className="list">
        {adjustment.next_workout.map((item) => (
          <li key={item.exercise_id}>
            {item.name}:{" "}
            {item.target_weight_kg !== null
              ? `${item.target_weight_kg} ${t.units.kg}`
              : t.adjust.freeWeight}{" "}
            × {item.reps} × {item.sets}
          </li>
        ))}
      </ul>

      <h3>{t.adjust.why}</h3>
      <p>{adjustment.rationale}</p>
      <small>{t.adjust.disclaimer}</small>
    </section>
  );
}
