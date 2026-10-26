/** Чистая логика экранов направлений и акцентов (без запросов), чтобы её можно было проверить тестами. */

export const MAX_ACCENT = 2;

/** Направления для выбора при регистрации; названия в `t.onboarding.directionNames`. */
export const DIRECTION_KEYS = [
  "gym",
  "powerlifting",
  "crossfit",
  "functional",
  "running",
  "yoga",
  "home",
  "universal",
] as const;

/** Делит занятия в неделю между выбранными направлениями: поровну, остаток — первым, каждому не меньше одного. */
export function distributeDays(
  keys: readonly string[],
  total: number,
  maxPerDirection = 5,
): { direction: string; days: number }[] {
  if (keys.length === 0) return [];
  const base = Math.max(1, Math.floor(total / keys.length));
  let rest = Math.max(0, total - base * keys.length);
  return keys.map((direction) => {
    const extra = rest > 0 ? 1 : 0;
    rest -= extra;
    return { direction, days: Math.min(maxPerDirection, base + extra) };
  });
}

/** Включает или выключает группу акцента; третья заменяет самую раннюю (без окон подтверждения). */
export function toggleAccent(current: readonly string[], key: string, limit = MAX_ACCENT): string[] {
  if (current.includes(key)) return current.filter((item) => item !== key);
  return [...current, key].slice(-limit);
}

export function sameSelection(a: readonly string[], b: readonly string[]): boolean {
  return a.length === b.length && [...a].sort().join() === [...b].sort().join();
}

/** «27 окт»: дата вступления изменений в силу. */
export function shortDate(iso: string): string {
  const [year, month, day] = iso.split("-").map(Number);
  const months = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
  return year && month && day ? `${day} ${months[month - 1]}` : iso;
}

/** Мультивыбор направлений: «универсальный» нельзя смешивать с остальными, он выбирает их сам. */
export function toggleDirection(current: readonly string[], key: string): string[] {
  if (current.includes(key)) return current.filter((item) => item !== key);
  if (key === "universal") return ["universal"];
  return [...current.filter((item) => item !== "universal"), key];
}
