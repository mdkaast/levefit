/** Чистая логика экранов питания: форматирование, выбор приёма пищи, пересчёт порций. */
import type { Macros, Meal } from "./api";

export const MEALS: readonly Meal[] = ["breakfast", "lunch", "dinner", "snack"];

/** Приём пищи по умолчанию — по времени суток. */
export function defaultMeal(hour: number): Meal {
  if (hour < 11) return "breakfast";
  if (hour < 16) return "lunch";
  if (hour < 21) return "dinner";
  return "snack";
}

/** КБЖУ порции продукта: значения на 100 г, граммы. */
export function foodMacros(per100: Macros, grams: number): Macros {
  const k = grams / 100;
  return {
    kcal: Math.round(per100.kcal * k),
    protein: Math.round(per100.protein * k * 10) / 10,
    fat: Math.round(per100.fat * k * 10) / 10,
    carbs: Math.round(per100.carbs * k * 10) / 10,
  };
}

/** Граммы по числу штук и наоборот: округляем до штуки. */
export function piecesToGrams(pieces: number, pieceGrams: number): number {
  return Math.round(pieces * pieceGrams);
}

export function gramsToPieces(grams: number, pieceGrams: number): number {
  return Math.max(1, Math.round(grams / pieceGrams));
}

/** «1 487»: тысячи отделяются неразрывным пробелом. */
export function formatKcal(value: number): string {
  return Math.round(value)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/** «98 / 148 г». */
export function macroLine(value: number, goal: number | undefined): string {
  const eaten = Math.round(value);
  return goal === undefined ? `${eaten} г` : `${eaten} / ${Math.round(goal)} г`;
}

/** Доля 0…1 для полос; без цели полосы пустые. */
export function share(value: number, goal: number | undefined): number {
  if (!goal || goal <= 0) return 0;
  return Math.min(1, Math.max(0, value / goal));
}
