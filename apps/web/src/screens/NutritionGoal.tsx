import { useEffect, useState } from "react";
import { getNutritionGoal, saveNutritionGoal, type NutritionGoalState } from "../api";
import { t } from "../i18n";
import { formatKcal } from "../nutrition";
import { Button, Card, Chip, EmptyState, Hint, Segmented, Skeleton, Stepper } from "../ui/ui";

type Props = { onBack: () => void };
type Mode = "gain" | "maintain" | "lose";

const signed = (value: number) => (value > 0 ? `+${value}` : String(value));

/** Цель питания: режим, ручная поправка, допущения расчёта и отметки, при которых дефицит не предлагается. */
export function NutritionGoal({ onBack }: Props) {
  const g = t.nutrition.goalScreen;
  const n = t.nutrition;
  const [state, setState] = useState<NutritionGoalState | null>(null);
  const [mode, setMode] = useState<Mode>("maintain");
  const [adjust, setAdjust] = useState(0);
  const [flags, setFlags] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getNutritionGoal()
      .then((s) => {
        setState(s);
        setMode(s.goal?.mode ?? s.requested_mode);
        setAdjust(s.adjust_kcal);
        setFlags(s.restrictions);
      })
      .catch(() => setFailed(true));
  }, []);

  const back = (
    <Button variant="text" onClick={onBack}>
      ‹ {g.back}
    </Button>
  );

  if (failed) {
    return (
      <>
        {back}
        <EmptyState title={n.loadError} text="" />
      </>
    );
  }
  if (!state) {
    return (
      <>
        {back}
        <Skeleton height={32} width="70%" />
        <Skeleton height={160} />
      </>
    );
  }
  if (!state.complete || !state.goal) {
    return (
      <>
        {back}
        <h1>{g.title}</h1>
        <EmptyState title={n.noGoalTitle} text={n.noGoalText} />
      </>
    );
  }

  const autoBlocked = state.blocked.some((b) => !state.screening.some((s) => s.key === b.key));
  const loseBlocked = flags.length > 0 || autoBlocked;
  const modes = (["gain", "maintain", "lose"] as const).filter((m) => m !== "lose" || !loseBlocked);
  const effective: Mode = mode === "lose" && loseBlocked ? "maintain" : mode;
  // Цифра под выбранным режимом: серверный расчёт для сохранённой поправки плюс разница поправок.
  const base = state.options[effective] ?? state.goal.kcal;
  const kcal = Math.max(state.goal.floor, base + (adjust - state.adjust_kcal));
  const protein = state.goal.protein_g;
  const fat = state.goal.fat_g;
  const carbs =
    kcal === state.goal.kcal ? state.goal.carbs_g : Math.max(0, Math.round((kcal - protein * 4 - fat * 9) / 4));

  async function save() {
    setSaving(true);
    setMessage(null);
    try {
      const next = await saveNutritionGoal({ mode: effective, adjust_kcal: adjust, restrictions: flags });
      setState(next);
      setMessage(g.saved);
    } catch {
      setMessage(g.error);
    } finally {
      setSaving(false);
    }
  }

  const toggleFlag = (key: string) =>
    setFlags((current) => (current.includes(key) ? current.filter((k) => k !== key) : [...current, key]));

  return (
    <>
      {back}
      <h1>{g.title}</h1>
      <Segmented
        items={modes.map((m) => ({ id: m, label: g.modes[m] }))}
        value={effective}
        onChange={setMode}
      />
      <Card accent>
        <p className="kicker">{g.perDay}</p>
        <h2 className="num">
          {formatKcal(kcal)} {n.kcal}
        </h2>
        <div className="macro-tiles">
          <div>
            <small>{n.protein}</small>
            <b className="num">{protein} г</b>
          </div>
          <div>
            <small>{n.fat}</small>
            <b className="num">{fat} г</b>
          </div>
          <div>
            <small>{n.carbs}</small>
            <b className="num">{carbs} г</b>
          </div>
        </div>
        <small className="muted">{g.floorNote(state.goal.floor)}</small>
      </Card>

      <h3>{g.adjust}</h3>
      <Stepper value={adjust} min={-300} max={300} step={50} label={g.adjust} format={(v) => `${signed(v)} ${n.kcal}`} onChange={setAdjust} />

      {loseBlocked && (
        <Card>
          <h3>{g.blockedTitle}</h3>
          <p className="muted">{g.blockedText}</p>
        </Card>
      )}
      {state.goal.notes.map((note) => (
        <Hint key={note}>{note}</Hint>
      ))}
      {state.trend_hint && <Hint>{state.trend_hint}</Hint>}

      <h3>{g.screening}</h3>
      <p className="muted">{g.screeningHint}</p>
      <div className="chip-row wrap">
        {state.screening.map((item) => (
          <Chip key={item.key} selected={flags.includes(item.key)} onClick={() => toggleFlag(item.key)}>
            {flags.includes(item.key) ? `✓ ${item.name}` : item.name}
          </Chip>
        ))}
      </div>

      <h3>{g.assumptions}</h3>
      <ul className="plain-list">
        {state.goal.assumptions.map((line) => (
          <li key={line}>
            <small className="muted">{line}</small>
          </li>
        ))}
      </ul>

      {message && <p role="status">{message}</p>}
      <Button loading={saving} onClick={save}>
        {g.save}
      </Button>
      <Hint>
        {state.disclaimer}
      </Hint>
    </>
  );
}
