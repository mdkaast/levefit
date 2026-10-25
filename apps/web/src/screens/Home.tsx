import { useEffect, useState } from "react";
import { createWorkout, listWorkouts, type Character, type WorkoutSummary } from "../api";
import { t } from "../i18n";

type Props = { character: Character; onOpenWorkout: (id: number) => void };

export function Home({ character, onOpenWorkout }: Props) {
  const [history, setHistory] = useState<WorkoutSummary[] | null>(null);

  useEffect(() => {
    listWorkouts()
      .then(setHistory)
      .catch(() => setHistory([]));
  }, []);

  async function start() {
    const workout = await createWorkout(t.workout.defaultTitle);
    onOpenWorkout(workout.id);
  }

  return (
    <main style={{ padding: 16, display: "grid", gap: 12 }}>
      <h1>{character.name}</h1>
      <p>
        {t.home.level} {character.level}
      </p>
      <button type="button" onClick={start}>
        {t.home.startWorkout}
      </button>

      <h2>{t.home.history}</h2>
      {history && history.length === 0 && <p>{t.home.historyEmpty}</p>}
      <ul style={{ paddingLeft: 0, listStyle: "none", display: "grid", gap: 8 }}>
        {history?.map((w) => (
          <li key={w.id}>
            <button type="button" onClick={() => onOpenWorkout(w.id)} style={{ width: "100%" }}>
              {w.date} · {w.title} · {w.sets_count} {t.home.sets}
              {w.status !== "finished" && ` · ${t.home.inProgress}`}
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
