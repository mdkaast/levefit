import { expect, test } from "vitest";
import { buildChart } from "./chart";

test("пустой список даёт пустой график", () => {
  expect(buildChart([], 300, 100)).toEqual({ path: "", dots: [], min: 0, max: 0 });
});

test("одна точка ставится по центру", () => {
  const chart = buildChart([{ date: "2026-10-01", weight_kg: 80 }], 300, 100);
  expect(chart.dots).toHaveLength(1);
  expect(chart.dots[0].x).toBe(150);
  expect(chart.path.startsWith("M150")).toBe(true);
});

test("меньший вес ниже, позже — правее", () => {
  const chart = buildChart(
    [
      { date: "2026-10-01", weight_kg: 82 },
      { date: "2026-10-11", weight_kg: 80 },
    ],
    300,
    100,
  );
  const [a, b] = chart.dots;
  expect(b.x).toBeGreaterThan(a.x);
  expect(b.y).toBeGreaterThan(a.y); // в SVG больше y — ниже
  expect(chart.min).toBe(80);
  expect(chart.max).toBe(82);
});

test("одинаковый вес не даёт NaN", () => {
  const chart = buildChart(
    [
      { date: "2026-10-01", weight_kg: 80 },
      { date: "2026-10-02", weight_kg: 80 },
    ],
    300,
    100,
  );
  expect(chart.dots.every((d) => Number.isFinite(d.x) && Number.isFinite(d.y))).toBe(true);
});

test("одна точка по вертикали посередине", () => {
  const chart = buildChart([{ date: "2026-10-01", weight_kg: 80 }], 300, 100);
  expect(chart.dots[0].y).toBe(50);
});
