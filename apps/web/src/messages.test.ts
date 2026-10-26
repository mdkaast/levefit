import { expect, test } from "vitest";
import type { Reward } from "./api";
import {
  achievementMessages,
  levelUpMessage,
  pointsPhrase,
  rankMessage,
  targetLine,
  workoutDoneMessage,
} from "./messages";

const base: Reward = {
  counted: true,
  xp_gained: 140,
  workout_xp: 50,
  sets_xp: 15,
  task_xp: 20,
  week_xp: 50,
  weight_xp: 0,
  level_before: 11,
  level_after: 12,
  leveled_up: true,
  rank_before: "amateur",
  rank_after: "amateur",
  rank_changed: false,
  level_points_gained: 1,
  stat_gains: { strength: 2, discipline: 1 },
  tasks_completed: [],
  achievements_earned: [],
  week_closed: false,
  streak_weeks: 2,
};

test("тренировка завершена: образец из ТЗ", () => {
  expect(workoutDoneMessage(base)).toBe(
    "Задание выполнено. Начислено 140 XP. Сила +2, Дисциплина +1.",
  );
});

test("лимит за сутки: XP не начислен, без давления", () => {
  const text = workoutDoneMessage({ ...base, counted: false });
  expect(text).toContain("XP не начислен");
});

test("новый уровень: образец из ТЗ", () => {
  expect(levelUpMessage(base)).toBe("Достигнут уровень 12. Доступно одно очко улучшения.");
  expect(levelUpMessage({ ...base, leveled_up: false })).toBeNull();
});

test("несколько очков уровня склоняются", () => {
  expect(pointsPhrase(1)).toBe("одно очко");
  expect(pointsPhrase(2)).toBe("2 очка");
  expect(pointsPhrase(5)).toBe("5 очков");
  expect(pointsPhrase(11)).toBe("11 очков");
  expect(pointsPhrase(22)).toBe("22 очка");
});

test("ранг и достижения", () => {
  expect(rankMessage(base)).toBeNull();
  expect(rankMessage({ ...base, rank_changed: true, rank_after: "practitioner" })).toBe(
    "Новый ранг: Практик.",
  );
  expect(achievementMessages({ ...base, achievements_earned: ["first_workout", "x"] })).toEqual([
    "Новое достижение: Первая тренировка.",
    "Новое достижение: x.",
  ]);
});

test("цель тренировки: вес × подходы × повторы", () => {
  expect(targetLine({ target_weight_kg: 80, sets: 3, reps: 8 })).toBe("80 кг × 3 × 8");
  expect(targetLine({ target_weight_kg: null, sets: 3, reps: 10 })).toContain("× 3 × 10");
});

test("цель по подходам показывается через слэш, если она разная", () => {
  expect(targetLine({ target_weight_kg: 80, sets: 3, reps: 8, rep_targets: [8, 8, 7] })).toBe(
    "80 кг × 8/8/7",
  );
  expect(targetLine({ target_weight_kg: 82.5, sets: 3, reps: 8, rep_targets: [6, 6, 6] })).toBe(
    "82,5 кг × 3 × 6",
  );
  expect(targetLine({ target_weight_kg: null, sets: 3, reps: 8 })).toContain("× 3 × 8");
});
