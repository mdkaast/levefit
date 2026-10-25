import { useEffect, useState, type FormEvent } from "react";
import { deleteMe, getMe, patchMe } from "../api";
import { t } from "../i18n";

type Props = { onDeleted: () => void };

const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

export function Profile({ onDeleted }: Props) {
  const [enabled, setEnabled] = useState(true);
  const [time, setTime] = useState("19:00");
  const [timezone, setTimezone] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(({ user }) => {
        setEnabled(user.reminders_enabled);
        setTime(user.reminder_time);
        setTimezone(user.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone);
      })
      .catch(() => setError(t.profile.error));
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

  async function remove() {
    if (!window.confirm(t.profile.confirmDelete)) return;
    try {
      await deleteMe();
      onDeleted();
    } catch {
      setError(t.profile.deleteError);
    }
  }

  const field = { display: "block", width: "100%" } as const;

  return (
    <main>
      <h1>{t.profile.title}</h1>

      <form onSubmit={save}>
        <h2>{t.profile.reminders}</h2>
        <label style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--text)" }}>
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />{" "}
          {t.profile.remindersEnabled}
        </label>
        <label>
          {t.profile.time}
          <input type="time" value={time} onChange={(e) => setTime(e.target.value)} style={field} />
        </label>
        <label>
          {t.profile.timezone}
          <input value={timezone} onChange={(e) => setTimezone(e.target.value)} style={field} />
        </label>
        <button type="submit">{t.profile.save}</button>
      </form>

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}

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
