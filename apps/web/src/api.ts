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
  silhouette: string | null;
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
  silhouette?: string | null;
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
  source: "ai" | "starter" | "week" | null;
  /** Поправки на сегодня: перерыв, низкое самочувствие. */
  notes: string[];
  /** Причины решения движка после прошлой тренировки. */
  decisions: string[];
  skipped_today: "move" | "rest" | null;
  /** Сессия недельного плана, если пользователь на программе. */
  session: PlanSession | null;
};

export type PlanSession = {
  title: string;
  direction: string;
  kind: "strength" | "session";
  minutes: number | null;
  blocks: string[];
  day: string;
  is_today: boolean;
  verified: boolean;
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

export const patchCharacter = (change: { target_muscles?: string[]; silhouette?: "male" | "female" }) =>
  request<Character>("/me/character", { method: "PATCH", body: JSON.stringify(change) });

// --- направления, акценты и неделя (фаза 3) ---

export type DirectionInfo = {
  key: string;
  name: string;
  kind: "strength" | "sessions" | "auto";
  accent_kind: "muscles" | "qualities" | null;
  default_days: number;
  options: { key: string; name: string }[];
  verified: boolean;
};

export type DirectionsState = {
  catalog: DirectionInfo[];
  muscles: { key: string; name: string }[];
  mine: { direction: string; days: number }[];
  saved: boolean;
  follows_week: boolean;
  total_days: number;
  max_days: number;
  accents: Record<string, { current: string[]; next: string[] }>;
  pending: Record<string, { from: string; selection: string[] }>;
  next_monday: string;
};

export type WeekLine = {
  slug: string;
  exercise_id: number;
  name: string;
  sets: number;
  reps: number[];
  unit: "reps" | "sec";
  role: string;
  accent: string | null;
};

export type WeekSession = {
  key: string;
  title: string;
  direction: string;
  kind: "strength" | "session";
  minutes: number | null;
  hard: boolean;
  tags: string[];
  exercises: WeekLine[];
  blocks: string[];
  verified: boolean;
};

export type WeekPlan = {
  offset: number;
  today: string;
  follows_week: boolean;
  week_start: string;
  days: { date: string; weekday: number; session: WeekSession | null }[];
  volume: { group: string; name: string; sets: number }[];
  warnings: string[];
  accents: Record<string, string[]>;
};

export type WeekChange = {
  weekday: number;
  day: string;
  kind: "added" | "removed" | "changed";
  title: string;
  details: string[];
};

export type WeekPreview = {
  effective_from: string;
  current_week_unchanged: boolean;
  changes: WeekChange[];
  volume: { group: string; name: string; before: number; after: number }[];
  after_warnings: string[];
};

// --- питание (фаза 4) ---

export type Meal = "breakfast" | "lunch" | "dinner" | "snack";
export type Macros = { kcal: number; protein: number; fat: number; carbs: number };

export type NutritionGoalData = {
  mode: "gain" | "maintain" | "lose";
  kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  bmr: number;
  tdee: number;
  floor: number;
  delta_kcal: number;
  adjust_kcal: number;
  assumptions: string[];
  notes: string[];
  clamped: boolean;
};

export type NutritionGoalState = {
  complete: boolean;
  requested_mode: "gain" | "maintain" | "lose";
  adjust_kcal: number;
  restrictions: string[];
  blocked: { key: string; name: string }[];
  lose_blocked: boolean;
  screening: { key: string; name: string }[];
  goal: NutritionGoalData | null;
  options: Record<"gain" | "maintain" | "lose", number | null>;
  trend_hint: string | null;
  disclaimer: string;
  profile: { weight_kg: number | null; height_cm: number | null; age: number | null };
};

export type DiaryEntry = {
  id: number;
  meal: Meal;
  name: string;
  grams: number | null;
  servings: number | null;
  food_id: number | null;
  recipe_id: number | null;
  kcal: number;
  protein: number;
  fat: number;
  carbs: number;
};

export type NutritionDay = {
  date: string;
  goal: NutritionGoalData | null;
  complete: boolean;
  totals: Macros;
  remaining: Macros | null;
  hints: string[];
  meals: { meal: Meal; name: string; entries: DiaryEntry[]; totals: Macros }[];
};

export type FoodItem = {
  id: number;
  name: string;
  group: string;
  group_name: string;
  kcal: number;
  protein: number;
  fat: number;
  carbs: number;
  piece_g: number | null;
  piece_name: string | null;
  own: boolean;
  last_grams?: number | null;
};

export type RecipeCard = {
  id: number;
  name: string;
  minutes: number;
  servings: number;
  meal: Meal;
  meal_name: string;
  tags: string[];
  kcal: number;
  protein: number;
  fat: number;
  carbs: number;
  reason?: string;
};

export type RecipeDetailData = RecipeCard & {
  servings_shown: number;
  per_serving: Macros;
  ingredients: { name: string; grams: number }[];
  steps: string[];
  note: string;
};

export const getNutritionGoal = () => request<NutritionGoalState>("/nutrition/goal");
export const saveNutritionGoal = (body: { mode: string; adjust_kcal: number; restrictions: string[] }) =>
  request<NutritionGoalState>("/nutrition/goal", { method: "PUT", body: JSON.stringify(body) });
export const getNutritionDay = (date?: string) =>
  request<NutritionDay>(`/nutrition/day${date ? `?date=${date}` : ""}`);
export const addDiaryEntry = (body: {
  date?: string;
  meal: Meal;
  food_id?: number;
  recipe_id?: number;
  grams?: number;
  servings?: number;
}) => request<DiaryEntry>("/nutrition/entries", { method: "POST", body: JSON.stringify(body) });
export const patchDiaryEntry = (id: number, body: { meal?: Meal; grams?: number; servings?: number }) =>
  request<DiaryEntry>(`/nutrition/entries/${id}`, { method: "PATCH", body: JSON.stringify(body) });
export const deleteDiaryEntry = (id: number) =>
  request<void>(`/nutrition/entries/${id}`, { method: "DELETE" });
export const searchFoods = (q: string, group?: string) => {
  const query = new URLSearchParams({ q, limit: "30" });
  if (group) query.set("group", group);
  return request<{ items: FoodItem[]; groups: { key: string; name: string }[] }>(`/nutrition/foods?${query}`);
};
export const getRecentFoods = () =>
  request<{ frequent: FoodItem[]; recent: FoodItem[] }>("/nutrition/foods/recent");
export const createFood = (body: { name: string; kcal: number; protein: number; fat: number; carbs: number }) =>
  request<FoodItem>("/nutrition/foods", { method: "POST", body: JSON.stringify(body) });
export const listRecipes = (tag?: string) =>
  request<{ items: RecipeCard[]; tags: { key: string; name: string }[]; total: number }>(
    `/nutrition/recipes${tag ? `?tag=${tag}` : ""}`,
  );
export const suggestRecipes = (training?: "before" | "after", direction?: string) => {
  const query = new URLSearchParams();
  if (training) query.set("training", training);
  if (direction) query.set("direction", direction);
  return request<{ summary: string | null; items: RecipeCard[] }>(`/nutrition/recipes/suggest?${query}`);
};
export const getRecipe = (id: number, servings: number) =>
  request<RecipeDetailData>(`/nutrition/recipes/${id}?servings=${servings}`);

export const getDirections = () => request<DirectionsState>("/directions");
export const putDirections = (items: { direction: string; days: number }[]) =>
  request<DirectionsState>("/me/directions", { method: "PUT", body: JSON.stringify({ items }) });
export const putAccent = (direction: string, selection: string[]) =>
  request<DirectionsState & { effective_from: string }>("/me/accent", {
    method: "PUT",
    body: JSON.stringify({ direction, selection }),
  });
export const getWeek = (offset: 0 | 1 = 0) => request<WeekPlan>(`/week?offset=${offset}`);
export const previewWeek = (change: {
  directions?: { direction: string; days: number }[];
  accent?: { direction: string; selection: string[] };
}) => request<WeekPreview>("/week/preview", { method: "POST", body: JSON.stringify(change) });

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

// ---------- каталог упражнений и программ ----------

export type ExerciseItem = {
  id: number;
  slug: string | null;
  name: string;
  pattern: string | null;
  pattern_name: string;
  level: string | null;
  level_name: string | null;
  ui_groups: string[];
  primary_muscles: string[];
  fits_you: boolean;
  verified: boolean;
};

export type ExerciseList = { total: number; catalog_total: number; items: ExerciseItem[] };
export type CatalogGroup = { key: string; name: string; count: number };

export type ExerciseCardData = ExerciseItem & {
  name_en: string | null;
  category: string;
  equipment_names: string[][];
  load_type: string | null;
  load_increment_kg: number | null;
  e1rm: string | null;
  flags: string[];
  muscles: { slug: string; name: string; ui_group: string; role: string; volume_weight: number }[];
  aliases: string[];
  cues: string[];
  media: string[];
  substitutes: { id: number; slug: string; name: string; reason: string }[];
};

export type SearchParams = { q?: string; group?: string; fits?: boolean; limit?: number; offset?: number };

export const getCatalogGroups = () => request<CatalogGroup[]>("/catalog/groups");

export const searchExercises = (params: SearchParams) => {
  const query = new URLSearchParams();
  if (params.q?.trim()) query.set("q", params.q.trim());
  if (params.group) query.set("group", params.group);
  if (params.fits) query.set("fits", "true");
  query.set("limit", String(params.limit ?? 40));
  query.set("offset", String(params.offset ?? 0));
  return request<ExerciseList>(`/catalog/exercises?${query}`);
};

export const getExerciseCard = (id: number) => request<ExerciseCardData>(`/catalog/exercises/${id}`);

export type ProgramCardData = {
  id: string;
  name: string;
  summary: string;
  days_min: number;
  days_max: number;
  session: number[];
  progression: string;
  engine_ready: boolean;
  fallback: string | null;
  verified: boolean;
  fits_you: boolean;
  goals: string[];
  levels: string[];
  inventory: string[];
  on_request_only: boolean;
};

export type ProgramSlot = {
  pattern: string;
  pattern_name: string;
  role: string;
  sets: number[];
  reps: number[];
  rir: number[] | null;
  progression: string;
  exercise_id: number | null;
  exercise_slug: string | null;
  exercise_name: string | null;
  via: string;
  note: string | null;
};

export type ProgramDetailData = ProgramCardData & {
  principle: string;
  warning: string | null;
  rules: Record<string, unknown> | null;
  phases: { weeks: string; scheme: string }[] | null;
  stages: Record<string, string[]> | null;
  week_scheme: string[][] | null;
  cardio: Record<string, string> | null;
  base_template: string | null;
  days: { name: string; slots: ProgramSlot[] }[];
  volume: { group: string; name: string; sets: number }[];
  empty_slots: string[];
  inventory_used: string;
  level_used: string;
};

export type Recommendation = {
  primary: ProgramCardData;
  then: ProgramCardData[];
  reasons: string[];
  usable_id: string;
  usable_note: string | null;
  inputs: Record<string, unknown>;
};

export const listPrograms = () => request<ProgramCardData[]>("/programs");
export const getProgram = (id: string) => request<ProgramDetailData>(`/programs/${id}`);
export const getRecommendation = () => request<Recommendation>("/programs/recommend");

export type ExerciseProgress = {
  exercise_id: number;
  name: string;
  points: { date: string; top_weight_kg: number | null; volume: number; score: number }[];
  plateau: boolean;
  sessions_without_gain: number;
};

export const getExerciseProgress = () => request<ExerciseProgress[]>("/progress/exercises");
