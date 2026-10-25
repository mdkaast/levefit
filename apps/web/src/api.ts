const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Character = {
  name: string;
  level: number;
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
};

export type Streak = {
  weeks: number;
  freezes_left: number;
  week_workouts: number;
  weekly_goal: number;
};

export type UserSettings = {
  reminders_enabled: boolean;
  reminder_time: string;
  timezone: string | null;
};

export type Me = {
  user: { id: number; username: string | null } & UserSettings;
  character: Character | null;
  streak: Streak | null;
};

export type CharacterInput = {
  name: string;
  appearance: string;
  goal: string | null;
  workouts_per_week: number;
  equipment: string;
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
  quest_xp: number;
  week_xp: number;
  level_before: number;
  level_after: number;
  leveled_up: boolean;
  quests_completed: string[];
  week_closed: boolean;
  streak_weeks: number;
};

export const finishWorkout = (workoutId: number) =>
  request<Workout & { reward: Reward }>(`/workouts/${workoutId}/finish`, { method: "POST" });

export type Quest = {
  id: number;
  code: string;
  kind: "daily" | "weekly";
  progress: number;
  target: number;
  xp_reward: number;
  status: "active" | "completed";
};

export const getQuests = () => request<Quest[]>("/quests");

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
