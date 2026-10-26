import { expect, test } from "vitest";
import { parseAge, parseHeight, parseWeight, validateName } from "./validation";

test("пустое имя отклоняется", () => {
  expect(validateName("   ")).not.toBeNull();
});

test("слишком длинное имя отклоняется", () => {
  expect(validateName("а".repeat(21))).not.toBeNull();
});

test("слишком короткое имя отклоняется", () => {
  expect(validateName(" а ")).not.toBeNull();
});

test("нормальное имя принимается", () => {
  expect(validateName(" Бодрый ")).toBeNull();
});

test("возраст: целое от 12 до 100", () => {
  expect(parseAge("30")).toBe(30);
  expect(parseAge("11")).toBeNull();
  expect(parseAge("101")).toBeNull();
  expect(parseAge("30.5")).toBeNull();
  expect(parseAge("")).toBeNull();
  expect(parseAge("abc")).toBeNull();
});

test("рост: целое от 120 до 230", () => {
  expect(parseHeight("175")).toBe(175);
  expect(parseHeight("119")).toBeNull();
  expect(parseHeight("231")).toBeNull();
});

test("вес: число от 20 до 500, запятая допустима", () => {
  expect(parseWeight("82,4")).toBe(82.4);
  expect(parseWeight("19")).toBeNull();
  expect(parseWeight("501")).toBeNull();
  expect(parseWeight(" ")).toBeNull();
});
