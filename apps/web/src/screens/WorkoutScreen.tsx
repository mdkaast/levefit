import { useEffect, useState, type FormEvent } from "react";
import {
  addSet,
  finishWorkout,
  getExercises,
  getPlan,
  getWorkout,
  type Exercise,
  type PlanItem,
  type Reward,
  type SetInput,
  type Workout,
} from "../api";
import { formatSet } from "../format";
import { t } from "../i18n";
import { targetLine } from "../messages";
import { AdjustmentView } from "./AdjustmentView";
import { RewardSummary } from "./RewardSummary";

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
  const [reward, setReward] = useState<Reward | null>(null);
  const [plan, setPlan] = useState<PlanItem[]>([]);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    getPlan()
      .then((p) => setPlan(p.items))
      .catch(() => undefined);
    Promise.all([getWorkout(workoutId), getExercises()])
      .then(([w, list]) => {
        setWorkout(w);
        setExercises(list);
        setExerciseId((list.find((e) => e.category === "strength") ?? list[0])?.id ?? null);
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

  function applyPlan(item: PlanItem) {
    setExerciseId(item.exercise_id);
    setWeight(item.target_weight_kg !== null ? String(item.target_weight_kg) : "");
    setReps(String(item.reps));
  }

  async function finish() {
    setBusy(true);
    setError(null);
    try {
      const { reward: earned, ...finishedWorkout } = await finishWorkout(workoutId, notes);
      setWorkout(finishedWorkout);
      setReward(earned);
    } catch {
      setError(t.workout.error);
    } finally {
      setBusy(false);
    }
  }

  const nameOf = (id: number) => exercises.find((e) => e.id === id)?.name ?? "";
  const field = { width: "100%" } as const;

  return (
    <main>
      <button type="button" onClick={onClose} className="ghost">
        {t.workout.back}
      </button>
      <h1>{workout?.title}</h1>

      {!finished && plan.length > 0 && (
        <section>
          <h3>{t.workout.plan}</h3>
          <small>{t.workout.planHint}</small>
          <ul className="list">
            {plan.map((item) => (
              <li key={item.exercise_id}>
                <button
                  type="button"
                  className="ghost"
                  style={{ width: "100%" }}
                  onClick={() => applyPlan(item)}
                >
                  {item.name}: {targetLine(item)}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {!finished && exercise && (
        <form onSubmit={submitSet}>
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
      {reward && <RewardSummary reward={reward} />}
      {reward && <AdjustmentView workoutId={workoutId} />}

      {workout && workout.sets.length === 0 && <p>{t.workout.noSets}</p>}
      <ul className="list">
        {workout?.sets.map((s) => (
          <li key={s.id}>
            {nameOf(s.exercise_id)} #{s.set_no}: {formatSet(s)}
          </li>
        ))}
      </ul>

      {!finished && workout && workout.sets.length > 0 && (
        <>
          <label>
            {t.workout.notes}
            <textarea
              value={notes}
              maxLength={2000}
              onChange={(e) => setNotes(e.target.value)}
              style={field}
            />
          </label>
          <button type="button" onClick={finish} disabled={busy}>
            {t.workout.finish}
          </button>
        </>
      )}
    </main>
  );
}
