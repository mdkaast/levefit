import { useEffect, useState, type FormEvent } from "react";
import {
  addSet,
  finishWorkout,
  getExercises,
  getWorkout,
  type Exercise,
  type SetInput,
  type Workout,
} from "../api";
import { formatSet } from "../format";
import { t } from "../i18n";

type Props = { workoutId: number; onClose: () => void };

const num = (value: string) => (value.trim() === "" ? undefined : Number(value));

export function WorkoutScreen({ workoutId, onClose }: Props) {
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [exerciseId, setExerciseId] = useState<number | null>(null);
  const [weight, setWeight] = useState("");
  const [reps, setReps] = useState("");
  const [rir, setRir] = useState("");
  const [minutes, setMinutes] = useState("");
  const [meters, setMeters] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([getWorkout(workoutId), getExercises()])
      .then(([w, list]) => {
        setWorkout(w);
        setExercises(list);
        setExerciseId(list[0]?.id ?? null);
      })
      .catch(() => setError(t.workout.error));
  }, [workoutId]);

  const exercise = exercises.find((e) => e.id === exerciseId);
  const finished = workout?.status === "finished";

  async function submitSet(event: FormEvent) {
    event.preventDefault();
    if (!exercise) return;
    const input: SetInput = { exercise_id: exercise.id };
    if (exercise.category === "strength") {
      input.weight_kg = num(weight);
      input.reps = num(reps);
      input.rir = num(rir);
    } else if (exercise.category === "cardio") {
      input.duration_s = minutes ? Number(minutes) * 60 : undefined;
      input.distance_m = num(meters);
    } else {
      input.reps = num(reps);
      input.duration_s = minutes ? Number(minutes) * 60 : undefined;
    }
    setBusy(true);
    setError(null);
    try {
      await addSet(workoutId, input);
      setWorkout(await getWorkout(workoutId));
    } catch {
      setError(t.workout.error);
    } finally {
      setBusy(false);
    }
  }

  async function finish() {
    setBusy(true);
    setError(null);
    try {
      setWorkout(await finishWorkout(workoutId));
    } catch {
      setError(t.workout.error);
    } finally {
      setBusy(false);
    }
  }

  const nameOf = (id: number) => exercises.find((e) => e.id === id)?.name ?? "";
  const field = { display: "block", width: "100%" } as const;

  return (
    <main style={{ padding: 16, display: "grid", gap: 12 }}>
      <button type="button" onClick={onClose}>
        {t.workout.back}
      </button>
      <h1>{workout?.title}</h1>

      {!finished && exercise && (
        <form onSubmit={submitSet} style={{ display: "grid", gap: 8 }}>
          <label>
            {t.workout.exercise}
            <select
              value={exerciseId ?? ""}
              onChange={(e) => setExerciseId(Number(e.target.value))}
              style={field}
            >
              {exercises.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name}
                </option>
              ))}
            </select>
          </label>

          {exercise.category === "strength" && (
            <>
              <label>
                {t.workout.weight}
                <input inputMode="decimal" value={weight} onChange={(e) => setWeight(e.target.value)} style={field} />
              </label>
              <label>
                {t.workout.reps}
                <input inputMode="numeric" value={reps} onChange={(e) => setReps(e.target.value)} style={field} />
              </label>
              <label>
                {t.workout.rir}
                <input inputMode="numeric" value={rir} onChange={(e) => setRir(e.target.value)} style={field} />
              </label>
            </>
          )}
          {exercise.category !== "strength" && (
            <>
              <label>
                {t.workout.minutes}
                <input inputMode="decimal" value={minutes} onChange={(e) => setMinutes(e.target.value)} style={field} />
              </label>
              {exercise.category === "cardio" ? (
                <label>
                  {t.workout.meters}
                  <input inputMode="numeric" value={meters} onChange={(e) => setMeters(e.target.value)} style={field} />
                </label>
              ) : (
                <label>
                  {t.workout.reps}
                  <input inputMode="numeric" value={reps} onChange={(e) => setReps(e.target.value)} style={field} />
                </label>
              )}
            </>
          )}
          <button type="submit" disabled={busy}>
            {t.workout.addSet}
          </button>
        </form>
      )}

      {error && <p role="alert">{error}</p>}
      {finished && <p>{t.workout.finished}</p>}

      {workout && workout.sets.length === 0 && <p>{t.workout.noSets}</p>}
      <ul style={{ paddingLeft: 16 }}>
        {workout?.sets.map((s) => (
          <li key={s.id}>
            {nameOf(s.exercise_id)} #{s.set_no}: {formatSet(s)}
          </li>
        ))}
      </ul>

      {!finished && workout && workout.sets.length > 0 && (
        <button type="button" onClick={finish} disabled={busy}>
          {t.workout.finish}
        </button>
      )}
    </main>
  );
}
