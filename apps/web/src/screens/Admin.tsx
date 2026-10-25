import { useEffect, useState } from "react";
import {
  getAdminStats,
  getRecentAdjustments,
  type AdminStats,
  type RecentAdjustment,
} from "../api";
import { t } from "../i18n";

type Tab = "stats" | "ai";
const TABS: Tab[] = ["stats", "ai"];

function Failure({ error }: { error: string | null }) {
  return error ? <p role="alert">{error}</p> : null;
}

function Stats() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getAdminStats()
      .then(setStats)
      .catch(() => setError(t.admin.error));
  }, []);
  if (!stats) return error ? <Failure error={error} /> : <p role="status">{t.loading}</p>;
  const max = Math.max(1, ...stats.workouts.daily.map((d) => d.count));
  const a = t.admin.stats;
  const tiles: [string, number][] = [
    [a.users, stats.users.total],
    [a.new7, stats.users.new_7d],
    [a.active7, stats.users.active_7d],
    [a.paused, stats.users.paused],
    [a.workouts, stats.workouts.finished],
    [a.workouts7, stats.workouts.finished_7d],
    [a.sets, stats.workouts.sets],
    [a.aiTotal, stats.ai.total],
  ];
  return (
    <section>
      <div className="tiles">
        {tiles.map(([label, value]) => (
          <div className="card" key={label}>
            <small>{label}</small>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <h3>{a.daily}</h3>
      <div className="spark" role="img" aria-label={a.daily}>
        {stats.workouts.daily.map((d) => (
          <i key={d.date} title={`${d.date}: ${d.count}`} style={{ height: `${(d.count / max) * 100}%` }} />
        ))}
      </div>
    </section>
  );
}

function AiInfo() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [recent, setRecent] = useState<RecentAdjustment[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getAdminStats()
      .then(setStats)
      .catch(() => setError(t.admin.error));
    getRecentAdjustments()
      .then(setRecent)
      .catch(() => setError(t.admin.error));
  }, []);
  const a = t.admin.ai;
  return (
    <section>
      <Failure error={error} />
      {stats && (
        <>
          <p>
            {a.status}: {stats.ai.configured ? a.on : a.off} · {stats.ai.model}
          </p>
          <p>
            {a.total}: {stats.ai.total} · {a.week}: {stats.ai.last_7d}
          </p>
          <h3>{a.ratings}</h3>
          <div className="chips">
            <span className="chip lime">{t.adjust.rate.fits}: {stats.ai.ratings.fits}</span>
            <span className="chip pink">{t.adjust.rate.too_hard}: {stats.ai.ratings.too_hard}</span>
            <span className="chip">{t.adjust.rate.too_easy}: {stats.ai.ratings.too_easy}</span>
          </div>
          <h3>{a.decisions}</h3>
          <ul className="list">
            {stats.ai.by_decision.map((d) => (
              <li key={d.decision}>
                {t.adjust.decisions[d.decision as keyof typeof t.adjust.decisions] ?? d.decision}:{" "}
                {d.count}
              </li>
            ))}
          </ul>
        </>
      )}
      <h3>{a.recent}</h3>
      <ul className="list">
        {recent.map((r) => (
          <li key={r.id}>
            <b>{t.adjust.decisions[r.decision as keyof typeof t.adjust.decisions] ?? r.decision}</b>
            {r.rating ? ` · ${t.adjust.rate[r.rating as keyof typeof t.adjust.rate]}` : ""}
            <br />
            <small>{r.rationale}</small>
          </li>
        ))}
        {recent.length === 0 && <li>{a.empty}</li>}
      </ul>
    </section>
  );
}

export function Admin() {
  const [tab, setTab] = useState<Tab>("stats");
  return (
    <main>
      <h2>{t.admin.title}</h2>
      <div className="chips" role="tablist">
        {TABS.map((name) => (
          <button
            key={name}
            type="button"
            role="tab"
            aria-selected={tab === name}
            className={tab === name ? undefined : "ghost"}
            onClick={() => setTab(name)}
          >
            {t.admin.tabs[name]}
          </button>
        ))}
      </div>
      {tab === "stats" && <Stats />}
      {tab === "ai" && <AiInfo />}
    </main>
  );
}
