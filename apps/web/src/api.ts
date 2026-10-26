const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Character = {
  name: string;
  level: number;
  rank: string;
  level_points: number;
  xp: number;
  strength: number;
  endurance: number;
  agility: number;
  discipline: number;
  appearance: string;
  goal: string | null;
  workouts_per_week: number;
  equipment: string;
  xp_in_level: number;
  xp_to_next: number;
  gender: string | null;
  age: number | null;
  height_cm: number | null;
  experience: string | null;
  lifestyle: string | null;
  target_muscles: string[] | null;
};

export type Streak = {
  weeks: number;
  freezes_left: number;
  week_workouts: number;
  weekly_goal: number;
};

export type UserSettings = {
  mode: "active" | "paused";
  reminders_enabled: boolean;
  reminder_time: string;
  timezone: string | null;
};

export type Me = {
  is_admin: boolean;
  user: { id: number; username: string | null } & UserSettings;
  character: Character | null;
  streak: Streak | null;
};

export type CharacterInput = {
  name: string;
  goal: string | null;
  workouts_per_week: number;
  equipment: string;
  gender: string | null;
  age: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  experience: string | null;
  lifestyle: string | null;
  target_muscles: string[];
};

let token: string | null = null;

/** Ошибка ответа сервера. Текст «HTTP 404» используют старые проверки на экранах. */
export class ApiError extends Error {
  constructor(public status: number) {
    super(`HTTP ${status}`);
  }
}

/** Что делать с неудавшейся записью: повторить позже (нет связи, сбой сервера) или отбросить. */
export function classifyFailure(error: unknown): "retry" | "drop" {
  if (error instanceof ApiError) return error.status >= 500 || error.status === 408 || error.status === 429 ? "retry" : "drop";
  return "retry"; // fetch отклонён: связи нет
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!response.ok) throw new ApiError(response.status);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(initData: string): Promise<void> {
  const body = await request<{ access_token: string }>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
  token = body.access_token;
}

export const getMe = () => request<Me>("/me");

export const createCharacter = (input: CharacterInput) =>
  request<Character>("/characters", { method: "POST", body: JSON.stringify(input) });

export type Exercise = {
  id: number;
  name: string;
  category: "strength" | "cardio" | "mobility";
  muscle_group: string;
  owner_id: number | null;
};

export type WorkoutSet = {
  id: number;
  exercise_id: number;
  set_no: number;
  weight_kg: number | null;
  reps: number | null;
  rir: number | null;
  duration_s: number | null;
  distance_m: number | null;
};

export type Workout = {
  id: number;
  date: string;
  title: string;
  status: "planned" | "in_progress" | "finished";
  duration_min: number | null;
  notes: string | null;
  sets: WorkoutSet[];
};

export type WorkoutSummary = Omit<Workout, "notes" | "sets"> & { sets_count: number };

export type SetInput = {
  client_id?: string;
  exercise_id: number;
  weight_kg?: number;
  reps?: number;
  rir?: number;
  duration_s?: number;
  distance_m?: number;
};

export const getExercises = () => request<Exercise[]>("/exercises");
export const listWorkouts = () => request<WorkoutSummary[]>("/workouts");
export const getWorkout = (id: number) => request<Workout>(`/workouts/${id}`);
export type Checkin = { sleep_quality?: number; energy?: number; pain?: boolean };

export const createWorkout = (title: string, checkin: Checkin = {}) =>
  request<Workout>("/workouts", { method: "POST", body: JSON.stringify({ title, ...checkin }) });
export const addSet = (workoutId: number, input: SetInput) =>
  request<WorkoutSet>(`/workouts/${workoutId}/sets`, {
    method: "POST",
    body: JSON.stringify(input),
  });
export type Reward = {
  counted: boolean;
  xp_gained: number;
  workout_xp: number;
  sets_xp: number;
  task_xp: number;
  week_xp: number;
  weight_xp: number;
  level_before: number;
  level_after: number;
  leveled_up: boolean;
  rank_before: string;
  rank_after: string;
  rank_changed: boolean;
  level_points_gained: number;
  stat_gains: Record<string, number>;
  tasks_completed: string[];
  achievements_earned: string[];
  week_closed: boolean;
  streak_weeks: number;
};

export const finishWorkout = (workoutId: number, notes?: string) =>
  request<Workout & { reward: Reward }>(`/workouts/${workoutId}/finish`, {
    method: "POST",
    body: JSON.stringify(notes?.trim() ? { notes: notes.trim() } : {}),
  });

export type Adjustment = {
  health_flag: boolean;
  changes: string[];
  decision:
    | "increase_weight"
    | "keep_weight"
    | "reduce_weight"
    | "deload"
    | "change_volume"
    | "replace_exercise"
    | "change_rep_range";
  next_workout: PlanItem[];
  rationale: string;
  /** Кто написал объяснение: ИИ-тренер или шаблон (если ИИ недоступен). */
  explained_by: "llm" | "template" | null;
  engine_version: string | null;
  /** Решения движка по упражнениям: числа считает он, ИИ-тренер их только объясняет. */
  engine: {
    exercise_id: number;
    name: string;
    action: string;
    rule: string;
    reason: string;
    from_weight_kg: number | null;
    next_weight_kg: number | null;
  }[];
};

/** Решение движка после тренировки; plan — то, что планировалось на сегодня (иначе берётся прошлое решение). */
export const adjustWorkout = (workoutId: number, plan?: PlanItem[]) =>
  request<Adjustment>(`/workouts/${workoutId}/adjust`, {
    method: "POST",
    body: JSON.stringify(
      plan
        ? {
            plan: plan.map((p) => ({
              exercise_id: p.exercise_id,
              weight_kg: p.target_weight_kg,
              sets: p.sets,
              reps: p.reps,
            })),
          }
        : {},
    ),
  });

export type AdjustRating = "fits" | "too_hard" | "too_easy";

export const rateAdjustment = (workoutId: number, rating: AdjustRating) =>
  request<void>(`/workouts/${workoutId}/adjust/feedback`, {
    method: "POST",
    body: JSON.stringify({ rating }),
  });

export type Task = {
  id: number;
  code: string;
  period: "daily" | "weekly";
  kind: "main" | "minor" | "recovery";
  progress: number;
  target: number;
  xp_reward: number;
  status: "active" | "completed";
};

export const getTasks = () => request<Task[]>("/tasks");
export const completeTask = (id: number) =>
  request<Reward>(`/tasks/${id}/complete`, { method: "POST" });

export type Achievement = {
  code: string;
  earned: boolean;
  earned_at: string | null;
  progress: number;
  target: number;
};

export const getAchievements = () => request<Achievement[]>("/achievements");

export type PlanItem = {
  exercise_id: number;
  name: string;
  target_weight_kg: number | null;
  sets: number;
  reps: number; // верх диапазона повторений
  rep_targets?: number[] | null; // цель на каждый подход, например 8/8/7
};

export type Plan = {
  workout_id: number | null;
  items: PlanItem[];
  source: "ai" | "starter" | null;
  /** Поправки на сегодня: перерыв, низкое самочувствие. */
  notes: string[];
  /** Причины решения движка после прошлой тренировки. */
  decisions: string[];
  skipped_today: "move" | "rest" | null;
};

export const getPlan = (checkin?: { sleep?: number; energy?: number }) => {
  const query = new URLSearchParams();
  if (checkin?.sleep) query.set("sleep", String(checkin.sleep));
  if (checkin?.energy) query.set("energy", String(checkin.energy));
  const suffix = query.size ? `?${query}` : "";
  return request<Plan>(`/plan${suffix}`);
};

export type WeightEntry = { date: string; weight_kg: number };

export const getWeights = (from: string) =>
  request<WeightEntry[]>(`/metrics/weight?from=${encodeURIComponent(from)}`);
export const saveWeight = (weight_kg: number) =>
  request<WeightEntry & { xp_gained: number }>("/metrics/weight", {
    method: "PUT",
    body: JSON.stringify({ weight_kg }),
  });

export const patchMe = (settings: Partial<UserSettings>) =>
  request<Me["user"]>("/me", { method: "PATCH", body: JSON.stringify(settings) });

export async function deleteMe(): Promise<void> {
  await request<void>("/me", { method: "DELETE" });
  token = null;
}

export type AdminStats = {
  users: { total: number; new_7d: number; active_7d: number; paused: number };
  workouts: { finished: number; finished_7d: number; sets: number; daily: { date: string; count: number }[] };
  ai: {
    total: number;
    last_7d: number;
    by_decision: { decision: string; count: number }[];
    ratings: { fits: number; too_hard: number; too_easy: number };
    rules: { approved: number; proposed: number; rejected: number };
    configured: boolean;
    model: string;
  };
};

export type RecentAdjustment = {
  id: number;
  created_at: string;
  decision: string;
  rationale: string;
  model: string;
  rating: string | null;
  rules_used: number;
};

export const getAdminStats = () => request<AdminStats>("/admin/stats");
export const getRecentAdjustments = () => request<RecentAdjustment[]>("/admin/ai/recent");

export const patchCharacter = (targetMuscles: string[]) =>
  request<Character>("/me/character", {
    method: "PATCH",
    body: JSON.stringify({ target_muscles: targetMuscles }),
  });

export type ExerciseRatingValue = "easy" | "normal" | "hard";

export const rateExercise = (
  workoutId: number,
  exerciseId: number,
  rating: ExerciseRatingValue,
  pain: boolean,
) =>
  request<{ exercise_id: number; rating: string; pain: boolean }>(
    `/workouts/${workoutId}/ratings/${exerciseId}`,
    { method: "PUT", body: JSON.stringify({ rating, pain }) },
  );

export const skipToday = (kind: "move" | "rest") =>
  request<{ day: string; kind: string }>("/skips", { method: "POST", body: JSON.stringify({ kind }) });

export const undoSkip = () => request<void>("/skips/today", { method: "DELETE" });

export type LastSession = {
  day: string;
  top_weight_kg: number | null;
  sets: { weight_kg: number | null; reps: number | null; rir: number | null }[];
};

export const getLastSession = (exerciseId: number) =>
  request<LastSession | null>(`/exercises/${exerciseId}/last`);

export const overrideDecision = (workoutId: number, exerciseId: number, weightKg: number, reason?: string) =>
  request<Adjustment>(`/workouts/${workoutId}/adjust/exercise/${exerciseId}`, {
    method: "PATCH",
    body: JSON.stringify({ weight_kg: weightKg, reason: reason?.trim() || undefined }),
  });

export type ExerciseRatingOut = { exercise_id: number; rating: ExerciseRatingValue; pain: boolean };

export const listRatings = (workoutId: number) =>
  request<ExerciseRatingOut[]>(`/workouts/${workoutId}/ratings`);
