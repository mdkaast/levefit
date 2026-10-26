import { useCallback, useEffect, useState, type FormEvent } from "react";
import { getWeights, saveWeight } from "../api";
import { buildChart, type WeightPoint } from "../chart";
import { t } from "../i18n";

const PERIODS = [30, 90, 365] as const;
const W = 320;
const H = 140;

function isoDaysAgo(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toISOString().slice(0, 10);
}

export function Progress() {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>(90);
  const [points, setPoints] = useState<WeightPoint[]>([]);
  const [weight, setWeight] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const loadWeights = useCallback(() => {
    getWeights(isoDaysAgo(period))
      .then(setPoints)
      .catch(() => setPoints([]));
  }, [period]);

  useEffect(loadWeights, [loadWeights]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const value = Number(weight.replace(",", "."));
    if (!Number.isFinite(value) || value <= 0) return setMessage(t.progress.invalid);
    try {
      const saved = await saveWeight(value);
      setMessage(saved.xp_gained > 0 ? `${t.progress.saved} +${saved.xp_gained} XP` : t.progress.saved);
      setWeight("");
      loadWeights();
    } catch {
      setMessage(t.progress.error);
    }
  }

  const chart = buildChart(points, W, H);

  return (
    <main>
      <h1>{t.progress.title}</h1>

      <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8 }}>
        <input
          inputMode="decimal"
          placeholder={t.progress.weightPlaceholder}
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          style={{ flex: 1 }}
        />
        <button type="submit">{t.progress.save}</button>
      </form>
      {message && <p role="status">{message}</p>}

      <div className="segments">
        {PERIODS.map((days) => (
          <button
            key={days}
            type="button"
            aria-pressed={period === days}
            onClick={() => setPeriod(days)}
          >
            {t.progress.periods[days]}
          </button>
        ))}
      </div>

      {points.length === 0 ? (
        <p>{t.progress.empty}</p>
      ) : (
        <figure>
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={t.progress.chartLabel}>
            <defs>
              <linearGradient id="weight-area" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#c8e85c" stopOpacity="0.45" />
                <stop offset="100%" stopColor="#c8e85c" stopOpacity="0" />
              </linearGradient>
            </defs>
            {chart.dots.length > 1 && (
              <path
                d={`${chart.path} L${chart.dots[chart.dots.length - 1].x.toFixed(1)} ${H} L${chart.dots[0].x.toFixed(1)} ${H} Z`}
                fill="url(#weight-area)"
              />
            )}
            <path d={chart.path} fill="none" stroke="var(--lime)" strokeWidth={2.5} />
            {chart.dots.map((d) => (
              <circle key={d.date} cx={d.x} cy={d.y} r={3} fill="var(--yellow)">
                <title>
                  {d.date}: {d.weight} {t.units.kg}
                </title>
              </circle>
            ))}
          </svg>
          <figcaption>
            {t.progress.range}: {chart.min}–{chart.max} {t.units.kg}
          </figcaption>
        </figure>
      )}
    </main>
  );
}
