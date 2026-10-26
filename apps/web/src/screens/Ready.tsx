import { useEffect, useState } from "react";
import { createWorkout, getPlan, type Checkin, type Plan, type PlanItem } from "../api";
import { t } from "../i18n";
import { Button, Chip, Hint } from "../ui/ui";

type Props = {
  plan: Plan;
  onBack: () => void;
  /** Тренировка создана: сервер вернул её id, items — план с поправками на сегодня. */
  onStarted: (workoutId: number, items: PlanItem[]) => void;
};

// Оценки сна и самочувствия по шкале 1–5; значения «плохо» и ниже включают лёгкий день (≤2).
const LEVELS = { bad: 2, ok: 4, good: 5 } as const;
type Level = keyof typeof LEVELS;
const LEVEL_KEYS: Level[] = ["bad", "ok", "good"];

/** «Как вы сегодня?»: необязательные вопросы, которые меняют план и показывают как именно. */
export function Ready({ plan, onBack, onStarted }: Props) {
  const c = t.cycle.ready;
  const [sleep, setSleep] = useState<Level>("ok");
  const [energy, setEnergy] = useState<Level>("ok");
  const [pain, setPain] = useState(false);
  const [adjusted, setAdjusted] = useState<Plan>(plan);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Пересчитываем план по ответам: так видно, как они меняют тренировку.
  useEffect(() => {
    let cancelled = false;
    getPlan({ sleep: LEVELS[sleep], energy: LEVELS[energy] })
      .then((p) => !cancelled && setAdjusted(p))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [sleep, energy]);

  async function start(withAnswers: boolean) {
    setBusy(true);
    setError(null);
    const checkin: Checkin = withAnswers
      ? { sleep_quality: LEVELS[sleep], energy: LEVELS[energy], pain }
      : {};
    try {
      const workout = await createWorkout(t.workout.defaultTitle, checkin);
      onStarted(workout.id, withAnswers ? adjusted.items : plan.items);
    } catch {
      setError(c.error);
      setBusy(false);
    }
  }

  const light = adjusted.notes.find((n) => n.toLowerCase().includes("лёгкий день"));
  const effect = pain
    ? { title: c.effectPain, text: c.painText }
    : light
      ? { title: c.effectLight, text: light }
      : { title: c.effectSame, text: adjusted.items.map((i) => i.name).join(", ") || c.effectSame };

  const group = (
    label: string,
    options: Record<Level, string>,
    value: Level,
    set: (v: Level) => void,
  ) => (
    <div className="field-group">
      <h3>{label}</h3>
      <div className="three">
        {LEVEL_KEYS.map((key) => (
          <Chip key={key} selected={value === key} onClick={() => set(key)}>
            {options[key]}
          </Chip>
        ))}
      </div>
    </div>
  );

  return (
    <main className="ready">
      <button type="button" className="ghost back-link" onClick={onBack}>
        {t.onboarding.back}
      </button>
      <p className="kicker">{c.kicker}</p>
      <h1>{c.title}</h1>
      <p className="muted">{c.hint}</p>

      {group(c.sleep, c.sleepOpts, sleep, setSleep)}
      {group(c.energy, c.energyOpts, energy, setEnergy)}

      <div className="field-group">
        <h3>{c.pain}</h3>
        <div className="two">
          <Chip selected={!pain} onClick={() => setPain(false)}>
            {c.painOpts.no}
          </Chip>
          <Chip selected={pain} onClick={() => setPain(true)}>
            {c.painOpts.yes}
          </Chip>
        </div>
      </div>

      <div className="effect" aria-live="polite">
        <small>{effect.title}</small>
        <p>{effect.text}</p>
      </div>
      {pain && <Hint>{c.painText}</Hint>}
      {error && <p role="alert">{error}</p>}

      <Button loading={busy} onClick={() => start(true)}>
        {busy ? c.starting : c.start}
      </Button>
      <Button variant="text" disabled={busy} onClick={() => start(false)}>
        {c.skipQuestion}
      </Button>
    </main>
  );
}
