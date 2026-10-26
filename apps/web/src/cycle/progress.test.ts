import { describe, expect, it } from "vitest";
import type { PlanItem } from "../api";
import { clock, deltaLabel, locate, planPercent, repsLine, repTarget } from "./progress";

const bench: PlanItem = { exercise_id: 1, name: "Жим", target_weight_kg: 80, sets: 3, reps: 8, rep_targets: [8, 8, 7] };
const row: PlanItem = { exercise_id: 2, name: "Тяга", target_weight_kg: 70, sets: 2, reps: 10 };

describe("цикл тренировки", () => {
  it("цель по повторениям берётся по подходам или из верха диапазона", () => {
    expect(repTarget(bench, 0)).toBe(8);
    expect(repTarget(bench, 2)).toBe(7);
    expect(repTarget(bench, 5)).toBe(7);
    expect(repTarget(row, 1)).toBe(10);
  });

  it("находит текущее упражнение и подход по числу записанных", () => {
    expect(locate([bench, row], {})).toEqual({ exercise: 0, set: 0, finished: false });
    expect(locate([bench, row], { 1: 2 })).toEqual({ exercise: 0, set: 2, finished: false });
    expect(locate([bench, row], { 1: 3, 2: 1 })).toEqual({ exercise: 1, set: 1, finished: false });
    expect(locate([bench, row], { 1: 3, 2: 2 }).finished).toBe(true);
  });

  it("подписывает подход относительно плана", () => {
    expect(deltaLabel(8, 8)).toBe("как в плане");
    expect(deltaLabel(7, 8)).toBe("−1");
    expect(deltaLabel(10, 8)).toBe("+2");
  });

  it("форматирует время и строку повторов", () => {
    expect(clock(107)).toBe("1:47");
    expect(clock(150)).toBe("2:30");
    expect(clock(-5)).toBe("0:00");
    expect(repsLine([{ reps: 8 }, { reps: 7 }, { reps: null }])).toBe("8/7/0");
  });

  it("считает выполнение плана без превышения", () => {
    expect(planPercent([bench], { 1: [8, 8, 7] })).toBe(100);
    expect(planPercent([bench], { 1: [8, 7, 6] })).toBe(91);
    expect(planPercent([bench], { 1: [12, 12, 12] })).toBe(100);
    expect(planPercent([bench, row], {})).toBe(0);
    expect(planPercent([], {})).toBe(0);
  });
});
