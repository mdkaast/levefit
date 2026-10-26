import type { PlanItem } from "../api";

/** Чистые функции цикла тренировки: что делать дальше, как подписать подход, как показать время. */

export const DEFAULT_REST_S = 150; // 2:30, как в макете; для тяжёлых базовых можно +15 с кнопкой

export type Position = { exercise: number; set: number; finished: boolean };

/** Цель по повторениям для подхода: у каждого подхода своя (8/8/7) или общая верхняя граница. */
export function repTarget(item: PlanItem, setIndex: number): number {
  return item.rep_targets?.[setIndex] ?? item.rep_targets?.[item.rep_targets.length - 1] ?? item.reps;
}

/** Где пользователь сейчас: по числу уже записанных подходов каждого упражнения. */
export function locate(items: PlanItem[], counts: Record<number, number>): Position {
  for (let i = 0; i < items.length; i += 1) {
    const done = counts[items[i].exercise_id] ?? 0;
    if (done < items[i].sets) return { exercise: i, set: done, finished: false };
  }
  return { exercise: Math.max(0, items.length - 1), set: items[items.length - 1]?.sets ?? 0, finished: true };
}

/** Подпись подхода относительно плана: «как в плане», «−1», «+2». */
export function deltaLabel(reps: number, target: number): string {
  const diff = reps - target;
  if (diff === 0) return "как в плане";
  return diff > 0 ? `+${diff}` : `−${Math.abs(diff)}`;
}

/** «1:47» из секунд. */
export function clock(totalSeconds: number): string {
  const s = Math.max(0, Math.round(totalSeconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

/** Строка «8/7/6» из повторов подходов. */
export function repsLine(sets: { reps: number | null }[]): string {
  return sets.map((s) => s.reps ?? 0).join("/");
}

/** Выполнение плана в процентах: сумма повторов к плановой сумме, не больше 100. */
export function planPercent(items: PlanItem[], logged: Record<number, number[]>): number {
  let planned = 0;
  let done = 0;
  for (const item of items) {
    for (let i = 0; i < item.sets; i += 1) planned += repTarget(item, i);
    (logged[item.exercise_id] ?? []).slice(0, item.sets).forEach((reps, i) => {
      done += Math.min(reps, repTarget(item, i));
    });
  }
  return planned ? Math.round((done / planned) * 100) : 0;
}
