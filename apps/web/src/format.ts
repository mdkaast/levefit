import type { WorkoutSet } from "./api";
import { t } from "./i18n";

/** Краткая запись подхода: «80 кг × 8 · RIR 2» или «10 мин · 2000 м». */
export function formatSet(set: WorkoutSet): string {
  const parts: string[] = [];
  if (set.weight_kg !== null && set.reps !== null) {
    parts.push(`${set.weight_kg} ${t.units.kg} × ${set.reps}`);
  } else if (set.reps !== null) {
    parts.push(`× ${set.reps}`);
  }
  if (set.duration_s !== null) parts.push(`${Math.round(set.duration_s / 60)} ${t.units.min}`);
  if (set.distance_m !== null) parts.push(`${set.distance_m} ${t.units.m}`);
  if (set.rir !== null) parts.push(`RIR ${set.rir}`);
  return parts.join(" · ");
}

/** Имя с заглавной буквы: на главной и в профиле оно выглядит одинаково (B4). */
export function capitalizeName(raw: string): string {
  const name = raw.trim();
  return name ? name.charAt(0).toLocaleUpperCase("ru") + name.slice(1) : name;
}

/** «82,5» из «82.5»: запятая как десятичный разделитель, всегда одна десятая. */
export function formatWeight(raw: string | number): string {
  const value = Number(String(raw).replace(",", "."));
  return Number.isFinite(value) ? value.toFixed(1).replace(".", ",") : "";
}
