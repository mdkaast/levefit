import { expect, test } from "vitest";
import { validateName } from "./validation";

test("пустое имя отклоняется", () => {
  expect(validateName("   ")).not.toBeNull();
});

test("слишком длинное имя отклоняется", () => {
  expect(validateName("а".repeat(31))).not.toBeNull();
});

test("нормальное имя принимается", () => {
  expect(validateName(" Бодрый ")).toBeNull();
});
