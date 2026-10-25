import { expect, test } from "vitest";
import type { WorkoutSet } from "./api";
import { formatSet } from "./format";

const base: WorkoutSet = {
  id: 1,
  exercise_id: 1,
  set_no: 1,
  weight_kg: null,
  reps: null,
  rir: null,
  duration_s: null,
  distance_m: null,
};

test("силовой подход с RIR", () => {
  expect(formatSet({ ...base, weight_kg: 80, reps: 8, rir: 2 })).toBe("80 кг × 8 · RIR 2");
});

test("кардио: время и дистанция", () => {
  expect(formatSet({ ...base, duration_s: 600, distance_m: 2000 })).toBe("10 мин · 2000 м");
});

test("повторы без веса", () => {
  expect(formatSet({ ...base, reps: 15 })).toBe("× 15");
});
