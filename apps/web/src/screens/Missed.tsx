import { useState } from "react";
import { patchMe, skipToday } from "../api";
import { t } from "../i18n";
import { haptic } from "../prefs";
import { Button, Tag } from "../ui/ui";

type Props = { onClose: () => void; onApplied: () => void };

type Choice = "move" | "rest" | "pause";

/** Пропуск тренировки: перенос, засчитанный отдых или пауза. Ничего не отнимает. */
export function Missed({ onClose, onApplied }: Props) {
  const c = t.cycle.missed;
  const [choice, setChoice] = useState<Choice>("move");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  async function apply() {
    setBusy(true);
    setError(false);
    try {
      if (choice === "pause") await patchMe({ mode: "paused" });
      else await skipToday(choice);
      haptic("success");
      onApplied();
    } catch {
      setError(true);
      setBusy(false);
    }
  }

  const options: { id: Choice; title: string; text: string; badge?: string }[] = [
    { id: "move", ...c.move },
    { id: "rest", ...c.rest, badge: undefined },
    { id: "pause", ...c.pause, badge: undefined },
  ];

  return (
    <main className="missed">
      <button type="button" className="ghost back-link" onClick={onClose}>
        {t.onboarding.back}
      </button>
      <p className="kicker">{c.kicker}</p>
      <h1>{c.title}</h1>
      <p className="muted">{c.hint}</p>
      <div className="stack">
        {options.map((option) => (
          <button
            key={option.id}
            type="button"
            className="choice"
            aria-pressed={choice === option.id}
            onClick={() => {
              haptic("select");
              setChoice(option.id);
            }}
          >
            <span>
              <b>{option.title}</b>
              <small>{option.text}</small>
            </span>
            {option.badge && <Tag tone="fit">{option.badge}</Tag>}
          </button>
        ))}
      </div>
      {error && <p role="alert">{c.error}</p>}
      <Button loading={busy} onClick={() => void apply()}>
        {c.apply}
      </Button>
    </main>
  );
}
