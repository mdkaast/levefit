import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  deleteMe,
  getAchievements,
  getMe,
  patchMe,
  type Achievement,
  type Character,
} from "../api";
import { capitalizeName } from "../format";
import { t } from "../i18n";
import { loadPrefs, savePrefs } from "../prefs";
import { ListRow } from "../ui/ui";
import { Directions } from "./Directions";

type Props = { onDeleted: () => void };

const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;
const STATS = ["strength", "endurance", "agility", "discipline"] as const;

/** Смещение пояса от UTC: «GMT+10»; если браузер не умеет, показываем только название. */
function zoneOffset(zone: string): string {
  try {
    const parts = new Intl.DateTimeFormat("ru", { timeZone: zone, timeZoneName: "shortOffset" }).formatToParts(new Date());
    return parts.find((p) => p.type === "timeZoneName")?.value ?? "";
  } catch {
    return "";
  }
}

function listZones(current: string, device: string): string[] {
  const all = (Intl as { supportedValuesOf?: (key: string) => string[] }).supportedValuesOf?.("timeZone") ?? [];
  return Array.from(new Set([device, current, ...all].filter(Boolean)));
}

export function Profile({ onDeleted }: Props) {
  const [character, setCharacter] = useState<Character | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [paused, setPaused] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const [time, setTime] = useState("19:00");
  const [timezone, setTimezone] = useState("");
  const [view, setView] = useState<"profile" | "directions">("profile");
  const [prefs, setPrefs] = useState(loadPrefs());
  const device = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const zones = useMemo(() => listZones(timezone, device), [timezone, device]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(({ user, character: me }) => {
        setCharacter(me);
        setPaused(user.mode === "paused");
        setEnabled(user.reminders_enabled);
        setTime(user.reminder_time);
        setTimezone(user.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone);
      })
      .catch(() => setError(t.profile.error));
    getAchievements()
      .then(setAchievements)
      .catch(() => undefined);
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    if (!TIME_RE.test(time) || !timezone.trim()) return setError(t.profile.error);
    try {
      await patchMe({ reminders_enabled: enabled, reminder_time: time, timezone: timezone.trim() });
      setMessage(t.profile.saved);
    } catch {
      setError(t.profile.error);
    }
  }

  async function switchMode() {
    setMessage(null);
    setError(null);
    try {
      const user = await patchMe({ mode: paused ? "active" : "paused" });
      setPaused(user.mode === "paused");
    } catch {
      setError(t.profile.modeError);
    }
  }

  function changePrefs(change: Partial<typeof prefs>) {
    const next = { ...prefs, ...change };
    setPrefs(next);
    savePrefs(next);
  }

  async function remove() {
    if (!window.confirm(t.profile.confirmDelete)) return;
    try {
      await deleteMe();
      onDeleted();
    } catch {
      setError(t.profile.deleteError);
    }
  }

  if (view === "directions") {
    return (
      <main>
        <Directions onBack={() => setView("profile")} />
      </main>
    );
  }

  const field = { display: "block", width: "100%" } as const;
  const rank = character ? (t.ranks[character.rank as keyof typeof t.ranks] ?? character.rank) : "";

  return (
    <main>
      <h1>{t.profile.title}</h1>

      {character && (
        <section>
          <div className="row">
            <h2>{capitalizeName(character.name)}</h2>
            <span className="muted">
              {rank} · {t.home.level} {character.level}
            </span>
          </div>
          <div className="chips">
            <span className="chip lime">
              {t.home.xp}: {character.xp}
            </span>
            <span className="chip">
              {t.home.levelPoints}: {character.level_points}
            </span>
          </div>
          <h3>{t.profile.characteristics}</h3>
          <ul className="list">
            {STATS.map((stat) => (
              <li key={stat} className="row">
                <span>{t.home.stats[stat]}</span>
                <b>{character[stat]}</b>
              </li>
            ))}
          </ul>
        </section>
      )}

      {achievements.length > 0 && (
        <section>
          <h3>{t.profile.achievements}</h3>
          <ul className="list">
            {achievements.map((a) => {
              const text = t.achievements[a.code as keyof typeof t.achievements];
              return (
                <li key={a.code} className={`task-item${a.earned ? " done" : ""}`}>
                  <div className="row">
                    <span>{text?.title ?? a.code}</span>
                    <small>{a.earned ? t.profile.earned : `${a.progress}/${a.target}`}</small>
                  </div>
                  {text && <small>{text.hint}</small>}
                  {!a.earned && (
                    <div className="bar thin">
                      <i style={{ width: `${Math.round((a.progress / a.target) * 100)}%` }} />
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <section>
        <h2>{t.profile.modeTitle}</h2>
        <p className="muted">{t.profile.modeHint}</p>
        <button type="button" className={paused ? undefined : "ghost"} onClick={switchMode}>
          {paused ? t.profile.modeOff : t.profile.modeOn}
        </button>
      </section>

      <form onSubmit={save}>
        <h2>{t.profile.reminders}</h2>
        <label style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--text)" }}>
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />{" "}
          {t.profile.remindersEnabled}
        </label>
        <label>
          {t.profile.time}
          <input type="time" step={900} value={time} onChange={(e) => setTime(e.target.value)} style={field} />
        </label>
        <label>
          {t.profile.timezone}
          <select value={timezone} onChange={(e) => setTimezone(e.target.value)} style={field}>
            {zones.map((zone) => (
              <option key={zone} value={zone}>
                {zone.replace("_", " ")} {zoneOffset(zone)}
              </option>
            ))}
          </select>
        </label>
        {timezone && device !== timezone && (
          <p className="muted">
            {t.profile.timezoneDevice}: {device} {zoneOffset(device)}{" "}
            <button type="button" className="ghost" onClick={() => setTimezone(device)}>
              {t.profile.timezoneApply}
            </button>
          </p>
        )}
        <button type="submit">{t.profile.save}</button>
      </form>

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}

      <section>
        <ListRow
          title={t.directions.profileRow}
          hint={t.directions.profileHint}
          onClick={() => setView("directions")}
        />
      </section>

      <section>
        <h2>{t.profile.lookTitle}</h2>
        <label style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--text)" }}>
          <input type="checkbox" checked={prefs.reducedMotion} onChange={(e) => changePrefs({ reducedMotion: e.target.checked })} />
          {t.profile.reducedMotion}
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--text)" }}>
          <input type="checkbox" checked={prefs.haptics} onChange={(e) => changePrefs({ haptics: e.target.checked })} />
          {t.profile.haptics}
        </label>
      </section>

      <section>
        <h2>{t.profile.dangerZone}</h2>
        <p>{t.profile.deleteHint}</p>
        <button type="button" onClick={remove} className="danger">
          {t.profile.delete}
        </button>
      </section>
    </main>
  );
}
