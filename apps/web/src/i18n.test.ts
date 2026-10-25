import { expect, test } from "vitest";
import { t } from "./i18n";

test("заголовок приложения задан", () => {
  expect(t.appTitle.length).toBeGreaterThan(0);
});
