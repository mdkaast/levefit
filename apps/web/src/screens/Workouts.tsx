import { useEffect, useState } from "react";
import { listWorkouts, type WorkoutSummary } from "../api";
import { t } from "../i18n";
import { Button, EmptyState, ListRow, Segmented, Skeleton } from "../ui/ui";

type Props = { onOpenWorkout: (id: number) => void; onStart: () => void };

type Mode = "week" | "programs" | "exercises";

/** Вкладка «Тренировки». Неделя, программы и каталог подключаются в фазах 1–2; пока здесь история и старт. */
export function Workouts({ onOpenWorkout, onStart }: Props) {
  const [mode, setMode] = useState<Mode>("week");
  const [history, setHistory] = useState<WorkoutSummary[] | null>(null);

  useEffect(() => {
    listWorkouts()
      .then(setHistory)
      .catch(() => setHistory([]));
  }, []);

  const items = [
    { id: "week" as const, label: t.workouts.modes.week },
    { id: "programs" as const, label: t.workouts.modes.programs },
    { id: "exercises" as const, label: t.workouts.modes.exercises },
  ];

  return (
    <main>
      <h1>{t.workouts.title}</h1>
      <Segmented items={items} value={mode} onChange={setMode} />

      {mode === "week" && (
        <>
          <Button onClick={onStart}>{t.home.startWorkout}</Button>
          <h3>{t.home.history}</h3>
          {history === null && <Skeleton height={56} />}
          {history && history.length === 0 && (
            <EmptyState title={t.home.historyEmpty} text={t.workouts.emptyHistory} />
          )}
          <div className="stack">
            {history?.map((w) => (
              <ListRow
                key={w.id}
                title={`${w.date} · ${w.title}`}
                hint={`${w.sets_count} ${t.home.sets}${w.status !== "finished" ? ` · ${t.home.inProgress}` : ""}`}
                onClick={() => onOpenWorkout(w.id)}
              />
            ))}
          </div>
        </>
      )}

      {mode === "programs" && (
        <EmptyState title={t.workouts.programsTitle} text={t.workouts.programsText} />
      )}
      {mode === "exercises" && (
        <EmptyState title={t.workouts.exercisesTitle} text={t.workouts.exercisesText} />
      )}
    </main>
  );
}
