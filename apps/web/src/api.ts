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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
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
export const createWorkout = (title: string) =>
  request<Workout>("/workouts", { method: "POST", body: JSON.stringify({ title }) });
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
  decision: "keep_weight" | "reduce_weight" | "change_volume" | "replace_exercise";
  next_workout: {
    exercise_id: number;
    name: string;
    target_weight_kg: number | null;
    sets: number;
    reps: number;
  }[];
  rationale: string;
};

export const adjustWorkout = (workoutId: number) =>
  request<Adjustment>(`/workouts/${workoutId}/adjust`, { method: "POST" });

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
  reps: number;
};

export const getPlan = () => request<{ workout_id: number | null; items: PlanItem[] }>("/plan");

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
