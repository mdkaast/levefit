import { describe, expect, it } from "vitest";
import {
  defaultMeal,
  foodMacros,
  formatKcal,
  gramsToPieces,
  macroLine,
  piecesToGrams,
  share,
} from "./nutrition";

describe("defaultMeal", () => {
  it("выбирает приём пищи по времени суток", () => {
    expect(defaultMeal(8)).toBe("breakfast");
    expect(defaultMeal(13)).toBe("lunch");
    expect(defaultMeal(19)).toBe("dinner");
    expect(defaultMeal(23)).toBe("snack");
  });
});

describe("foodMacros", () => {
  it("пересчитывает значения на 100 г под граммовку", () => {
    const egg = { kcal: 143, protein: 12.6, fat: 9.5, carbs: 0.7 };
    expect(foodMacros(egg, 110)).toEqual({ kcal: 157, protein: 13.9, fat: 10.5, carbs: 0.8 });
    expect(foodMacros(egg, 0).kcal).toBe(0);
  });
});

describe("штуки и граммы", () => {
  it("переводит туда и обратно", () => {
    expect(piecesToGrams(3, 55)).toBe(165);
    expect(gramsToPieces(165, 55)).toBe(3);
    expect(gramsToPieces(10, 55)).toBe(1);
  });
});

describe("форматирование", () => {
  it("разделяет тысячи неразрывным пробелом", () => {
    expect(formatKcal(1487)).toBe("1 487");
    expect(formatKcal(980.4)).toBe("980");
  });
  it("показывает съеденное и цель", () => {
    expect(macroLine(98.4, 148)).toBe("98 / 148 г");
    expect(macroLine(40, undefined)).toBe("40 г");
  });
  it("считает долю в пределах 0…1", () => {
    expect(share(50, 100)).toBe(0.5);
    expect(share(300, 100)).toBe(1);
    expect(share(10, undefined)).toBe(0);
  });
});
