import { describe, expect, it } from "vitest";
import { distributeDays, sameSelection, shortDate, toggleAccent, toggleDirection } from "./directions";

describe("distributeDays", () => {
  it("делит поровну, остаток отдаёт первым", () => {
    expect(distributeDays(["gym", "running"], 5)).toEqual([
      { direction: "gym", days: 3 },
      { direction: "running", days: 2 },
    ]);
    expect(distributeDays(["gym", "yoga", "running"], 4)).toEqual([
      { direction: "gym", days: 2 },
      { direction: "yoga", days: 1 },
      { direction: "running", days: 1 },
    ]);
  });

  it("каждому направлению не меньше одного занятия и не больше предела", () => {
    expect(distributeDays(["gym", "yoga", "running"], 1).every((d) => d.days >= 1)).toBe(true);
    expect(distributeDays(["gym"], 7)).toEqual([{ direction: "gym", days: 5 }]);
    expect(distributeDays([], 3)).toEqual([]);
  });
});

describe("toggleAccent", () => {
  it("не больше двух: третья заменяет самую раннюю", () => {
    expect(toggleAccent(["chest", "abs"], "lats")).toEqual(["abs", "lats"]);
  });
  it("повторное нажатие снимает группу", () => {
    expect(toggleAccent(["chest", "abs"], "chest")).toEqual(["abs"]);
    expect(toggleAccent([], "chest")).toEqual(["chest"]);
  });
});

describe("helpers", () => {
  it("сравнивает выбор без учёта порядка", () => {
    expect(sameSelection(["a", "b"], ["b", "a"])).toBe(true);
    expect(sameSelection(["a"], ["a", "b"])).toBe(false);
  });
  it("форматирует дату", () => {
    expect(shortDate("2026-11-02")).toBe("2 ноя");
  });
});

describe("toggleDirection", () => {
  it("добавляет и снимает направления", () => {
    expect(toggleDirection(["gym"], "running")).toEqual(["gym", "running"]);
    expect(toggleDirection(["gym", "running"], "gym")).toEqual(["running"]);
  });
  it("«универсальный» заменяет остальные, а остальные снимают его", () => {
    expect(toggleDirection(["gym", "yoga"], "universal")).toEqual(["universal"]);
    expect(toggleDirection(["universal"], "yoga")).toEqual(["yoga"]);
  });
});
