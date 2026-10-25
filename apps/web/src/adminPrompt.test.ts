import { describe, expect, it } from "vitest";
import { buildChangePrompt } from "./adminPrompt";

describe("buildChangePrompt", () => {
  const base = { kind: "bug", area: "home", title: " Сломана кнопка ", details: "Не нажимается", result: "" };

  it("includes type, area, task and safety rules", () => {
    const text = buildChangePrompt(base);
    expect(text).toContain("Тип: Исправить ошибку");
    expect(text).toContain("Раздел: Главная");
    expect(text).toContain("Задача: Сломана кнопка");
    expect(text).toContain("docs/handoff.md");
    expect(text).toContain("в main не вливай");
    expect(text).not.toContain("Ожидаемый результат");
  });

  it("adds the expected result when given", () => {
    expect(buildChangePrompt({ ...base, result: "Кнопка работает" })).toContain(
      "Ожидаемый результат:\nКнопка работает",
    );
  });
});
