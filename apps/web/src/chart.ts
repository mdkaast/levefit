export type WeightPoint = { date: string; weight_kg: number };

export type Chart = {
  path: string;
  dots: { x: number; y: number; date: string; weight: number }[];
  min: number;
  max: number;
};

const DAY_MS = 86_400_000;

/** Переводит записи веса в координаты SVG: X — по датам, Y — по весу (меньше вес — ниже). */
export function buildChart(points: WeightPoint[], width: number, height: number, pad = 12): Chart {
  if (points.length === 0) return { path: "", dots: [], min: 0, max: 0 };

  const times = points.map((p) => Date.parse(p.date));
  const weights = points.map((p) => p.weight_kg);
  const minT = Math.min(...times);
  const maxT = Math.max(...times);
  const min = Math.min(...weights);
  const max = Math.max(...weights);
  const spanT = Math.max(maxT - minT, DAY_MS);
  const spanW = Math.max(max - min, 0.5);
  const innerW = width - pad * 2;
  const innerH = height - pad * 2;

  const dots = points.map((p, i) => ({
    x: points.length === 1 ? width / 2 : pad + ((times[i] - minT) / spanT) * innerW,
    // Если все значения одинаковы, рисуем линию посередине, а не у нижнего края.
    y: max === min ? height / 2 : height - pad - ((p.weight_kg - min) / spanW) * innerH,
    date: p.date,
    weight: p.weight_kg,
  }));
  const path = dots.map((d, i) => `${i === 0 ? "M" : "L"}${d.x.toFixed(1)} ${d.y.toFixed(1)}`).join(" ");
  return { path, dots, min, max };
}
