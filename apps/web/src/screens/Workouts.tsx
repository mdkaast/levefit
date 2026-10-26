import { useEffect, useState } from "react";
import { listWorkouts, type WorkoutSummary } from "../api";
import { t } from "../i18n";
import { Button, EmptyState, ListRow, Segmented, Skeleton } from "../ui/ui";
import { ExerciseCard } from "./ExerciseCard";
import { ExerciseLibrary } from "./ExerciseLibrary";
import { ProgramDetail } from "./ProgramDetail";
import { Programs } from "./Programs";

type Props = { onOpenWorkout: (id: number) => void; onStart: () => void };

type Mode = "week" | "programs" | "exercises";

/** Открытая карточка внутри вкладки; стек позволяет вернуться, например, от замены к исходному упражнению. */
type Detail = { kind: "exercise"; id: number } | { kind: "program"; id: string };

/** Вкладка «Тренировки». Неделя, программы и каталог подключаются в фазах 1–2; пока здесь история и старт. */
export function Workouts({ onOpenWorkout, onStart }: Props) {
  const [mode, setMode] = useState<Mode>("week");
  const [history, setHistory] = useState<WorkoutSummary[] | null>(null);
  const [stack, setStack] = useState<Detail[]>([]);

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

  const open = (detail: Detail) => setStack((prev) => [...prev, detail]);
  const back = () => setStack((prev) => prev.slice(0, -1));
  const top = stack[stack.length - 1];
  if (top) {
    return (
      <main>
        {top.kind === "exercise" ? (
          <ExerciseCard
            id={top.id}
            onBack={back}
            onOpen={(id) => open({ kind: "exercise", id })}
          />
        ) : (
          <ProgramDetail
            id={top.id}
            onBack={back}
            onOpenExercise={(id) => open({ kind: "exercise", id })}
          />
        )}
      </main>
    );
  }

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

      {mode === "programs" && <Programs onOpen={(id) => open({ kind: "program", id })} />}
      {mode === "exercises" && <ExerciseLibrary onOpen={(id) => open({ kind: "exercise", id })} />}
    </main>
  );
}
