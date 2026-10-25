import { useCallback, useEffect, useState, type FormEvent } from "react";
import { getWeights, listWorkouts, saveWeight, type WorkoutSummary } from "../api";
import { buildChart, type WeightPoint } from "../chart";
import { t } from "../i18n";

type Props = { onOpenWorkout: (id: number) => void };

const PERIODS = [30, 90, 365] as const;
const W = 320;
const H = 140;

function isoDaysAgo(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toISOString().slice(0, 10);
}

export function Progress({ onOpenWorkout }: Props) {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>(90);
  const [points, setPoints] = useState<WeightPoint[]>([]);
  const [history, setHistory] = useState<WorkoutSummary[] | null>(null);
  const [weight, setWeight] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const loadWeights = useCallback(() => {
    getWeights(isoDaysAgo(period))
      .then(setPoints)
      .catch(() => setPoints([]));
  }, [period]);

  useEffect(loadWeights, [loadWeights]);
  useEffect(() => {
    listWorkouts()
      .then(setHistory)
      .catch(() => setHistory([]));
  }, []);

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
    <main style={{ padding: 16, display: "grid", gap: 12 }}>
      <h1>{t.progress.title}</h1>

      <form onSubmit={submit} style={{ display: "flex", gap: 8 }}>
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

      <div style={{ display: "flex", gap: 8 }}>
        {PERIODS.map((days) => (
          <button
            key={days}
            type="button"
            aria-pressed={period === days}
            onClick={() => setPeriod(days)}
            style={{ fontWeight: period === days ? "bold" : "normal" }}
          >
            {t.progress.periods[days]}
          </button>
        ))}
      </div>

      {points.length === 0 ? (
        <p>{t.progress.empty}</p>
      ) : (
        <figure style={{ margin: 0 }}>
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={t.progress.chartLabel}>
            <path d={chart.path} fill="none" stroke="#4a8" strokeWidth={2} />
            {chart.dots.map((d) => (
              <circle key={d.date} cx={d.x} cy={d.y} r={3} fill="#4a8">
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

      <h2>{t.home.history}</h2>
      {history && history.length === 0 && <p>{t.home.historyEmpty}</p>}
      <ul style={{ paddingLeft: 0, listStyle: "none", display: "grid", gap: 8 }}>
        {history?.map((w) => (
          <li key={w.id}>
            <button type="button" onClick={() => onOpenWorkout(w.id)} style={{ width: "100%" }}>
              {w.date} · {w.title} · {w.sets_count} {t.home.sets}
              {w.status !== "finished" && ` · ${t.home.inProgress}`}
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
