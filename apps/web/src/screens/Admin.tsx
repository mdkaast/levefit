import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  addChangeRequest,
  addCoachRule,
  deleteChangeRequest,
  getAdminStats,
  getChangeRequests,
  getCoachRules,
  getRecentAdjustments,
  learnCoachRules,
  setChangeRequestStatus,
  setCoachRuleStatus,
  type AdminStats,
  type ChangeRequest,
  type CoachRule,
  type RecentAdjustment,
} from "../api";
import { t } from "../i18n";
import { buildChangePrompt, CHANGE_AREAS, CHANGE_KINDS } from "../adminPrompt";

type Tab = "stats" | "ai" | "teach" | "changes";
const TABS: Tab[] = ["stats", "ai", "teach", "changes"];

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

function Teach() {
  const [rules, setRules] = useState<CoachRule[]>([]);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const load = useCallback(() => {
    getCoachRules()
      .then(setRules)
      .catch(() => setError(t.admin.error));
  }, []);
  useEffect(load, [load]);
  const a = t.admin.teach;

  async function add(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await addCoachRule(text.trim());
      setText("");
      load();
    } catch {
      setError(t.admin.error);
    }
  }
  async function decide(id: number, status: "approved" | "rejected") {
    try {
      await setCoachRuleStatus(id, status);
      load();
    } catch {
      setError(t.admin.error);
    }
  }
  async function learn() {
    setError(null);
    setNote(null);
    try {
      const created = await learnCoachRules();
      setNote(created.length ? a.learned(created.length) : a.nothing);
      load();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      setError(msg.includes("409") ? a.notEnough : msg.includes("503") ? a.aiOff : t.admin.error);
    }
  }
  const group = (status: string) => rules.filter((r) => r.status === status);
  return (
    <section>
      <form onSubmit={add}>
        <label>
          {a.newRule}
          <textarea value={text} maxLength={500} rows={3} onChange={(e) => setText(e.target.value)} placeholder={a.placeholder} />
        </label>
        <button type="submit" disabled={text.trim().length < 3}>
          {a.add}
        </button>
      </form>
      <button type="button" className="ghost" onClick={learn}>
        {a.learn}
      </button>
      {note && <p role="status">{note}</p>}
      <Failure error={error} />
      <h3>{a.proposed}</h3>
      <ul className="list">
        {group("proposed").map((r) => (
          <li key={r.id}>
            {r.text}
            <div className="chips">
              <button type="button" onClick={() => decide(r.id, "approved")}>{a.approve}</button>
              <button type="button" className="ghost" onClick={() => decide(r.id, "rejected")}>{a.reject}</button>
            </div>
          </li>
        ))}
        {group("proposed").length === 0 && <li>{a.none}</li>}
      </ul>
      <h3>{a.approved}</h3>
      <ul className="list">
        {group("approved").map((r) => (
          <li key={r.id}>
            {r.text}
            <br />
            <small>{r.source === "ai" ? a.fromAi : a.fromOwner}</small>
            <div className="chips">
              <button type="button" className="ghost" onClick={() => decide(r.id, "rejected")}>{a.disable}</button>
            </div>
          </li>
        ))}
        {group("approved").length === 0 && <li>{a.none}</li>}
      </ul>
    </section>
  );
}

function Changes() {
  const [items, setItems] = useState<ChangeRequest[]>([]);
  const [kind, setKind] = useState(CHANGE_KINDS[0].id);
  const [area, setArea] = useState(CHANGE_AREAS[0].id);
  const [title, setTitle] = useState("");
  const [details, setDetails] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<number | "draft" | null>(null);
  const a = t.admin.changes;

  const load = useCallback(() => {
    getChangeRequests()
      .then(setItems)
      .catch(() => setError(t.admin.error));
  }, []);
  useEffect(load, [load]);

  const draft = buildChangePrompt({ kind, area, title, details, result });
  const ready = title.trim().length >= 3 && details.trim().length >= 10;

  async function copy(text: string, mark: number | "draft") {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(mark);
    } catch {
      setError(a.copyFailed);
    }
  }
  async function save(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await addChangeRequest(title.trim(), draft);
      setTitle("");
      setDetails("");
      setResult("");
      load();
    } catch {
      setError(t.admin.error);
    }
  }
  async function mark(id: number, status: "draft" | "sent" | "done") {
    try {
      await setChangeRequestStatus(id, status);
      load();
    } catch {
      setError(t.admin.error);
    }
  }
  async function remove(id: number) {
    try {
      await deleteChangeRequest(id);
      load();
    } catch {
      setError(t.admin.error);
    }
  }

  return (
    <section>
      <form onSubmit={save}>
        <label>
          {a.kind}
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {CHANGE_KINDS.map((k) => (
              <option key={k.id} value={k.id}>{k.label}</option>
            ))}
          </select>
        </label>
        <label>
          {a.area}
          <select value={area} onChange={(e) => setArea(e.target.value)}>
            {CHANGE_AREAS.map((k) => (
              <option key={k.id} value={k.id}>{k.label}</option>
            ))}
          </select>
        </label>
        <label>
          {a.title}
          <input value={title} maxLength={120} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label>
          {a.details}
          <textarea value={details} rows={4} maxLength={4000} onChange={(e) => setDetails(e.target.value)} />
        </label>
        <label>
          {a.result}
          <textarea value={result} rows={2} maxLength={1000} onChange={(e) => setResult(e.target.value)} />
        </label>
        <h3>{a.preview}</h3>
        <pre className="prompt">{ready ? draft : a.previewEmpty}</pre>
        <div className="chips">
          <button type="submit" disabled={!ready}>{a.save}</button>
          <button type="button" className="ghost" disabled={!ready} onClick={() => copy(draft, "draft")}>
            {copied === "draft" ? a.copied : a.copy}
          </button>
        </div>
      </form>
      <Failure error={error} />
      <h3>{a.saved}</h3>
      <ul className="list">
        {items.map((r) => (
          <li key={r.id}>
            <b>{r.title}</b> · <small>{a.statuses[r.status as keyof typeof a.statuses]}</small>
            <div className="chips">
              <button type="button" className="ghost" onClick={() => copy(r.prompt, r.id)}>
                {copied === r.id ? a.copied : a.copy}
              </button>
              {r.status !== "sent" && <button type="button" className="ghost" onClick={() => mark(r.id, "sent")}>{a.markSent}</button>}
              {r.status !== "done" && <button type="button" className="ghost" onClick={() => mark(r.id, "done")}>{a.markDone}</button>}
              <button type="button" className="danger" onClick={() => remove(r.id)}>{a.remove}</button>
            </div>
          </li>
        ))}
        {items.length === 0 && <li>{a.none}</li>}
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
      {tab === "teach" && <Teach />}
      {tab === "changes" && <Changes />}
    </main>
  );
}
