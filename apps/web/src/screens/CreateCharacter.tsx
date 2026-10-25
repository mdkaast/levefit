import { useState, type FormEvent } from "react";
import { createCharacter, type Character } from "../api";
import { Icon, type IconName } from "../icons";
import { t } from "../i18n";
import { NAME_MAX_LEN, validateName } from "../validation";

type Props = { onCreated: (character: Character) => void };

const APPEARANCES = ["warrior", "runner", "sage"] as const;
const APPEARANCE_ICONS: Record<(typeof APPEARANCES)[number], IconName> = {
  warrior: "dumbbell",
  runner: "bolt",
  sage: "leaf",
};
const GOALS = ["mass", "strength", "shape"] as const;
const EQUIPMENT = ["gym", "home", "none"] as const;

export function CreateCharacter({ onCreated }: Props) {
  const [name, setName] = useState("");
  const [appearance, setAppearance] = useState<string>(APPEARANCES[0]);
  const [goal, setGoal] = useState("");
  const [perWeek, setPerWeek] = useState(3);
  const [equipment, setEquipment] = useState<string>(EQUIPMENT[0]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const nameError = validateName(name);
    if (nameError) return setError(nameError);
    setSaving(true);
    setError(null);
    try {
      const character = await createCharacter({
        name: name.trim(),
        appearance,
        goal: goal || null,
        workouts_per_week: perWeek,
        equipment,
      });
      onCreated(character);
    } catch {
      setError(t.create.error);
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="card" style={{ margin: 16, display: "grid", gap: 14 }}>
      <h1>{t.create.title}</h1>

      <label>
        {t.create.name}
        <input
          value={name}
          maxLength={NAME_MAX_LEN}
          placeholder={t.create.namePlaceholder}
          onChange={(e) => setName(e.target.value)}
          style={{ display: "block", width: "100%" }}
        />
      </label>

      <div style={{ display: "grid", gap: 6 }}>
        <label>{t.create.appearance}</label>
        <div className="choices">
          {APPEARANCES.map((a) => (
            <button
              key={a}
              type="button"
              aria-pressed={appearance === a}
              onClick={() => setAppearance(a)}
            >
              <Icon name={APPEARANCE_ICONS[a]} />
              {t.appearances[a]}
            </button>
          ))}
        </div>
      </div>

      <label>
        {t.create.goal}
        <select
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          style={{ display: "block", width: "100%" }}
        >
          <option value="">{t.create.goalNone}</option>
          {GOALS.map((g) => (
            <option key={g} value={g}>
              {t.goals[g]}
            </option>
          ))}
        </select>
      </label>

      <label>
        {t.create.workoutsPerWeek}: {perWeek}
        <input
          type="range"
          min={1}
          max={7}
          value={perWeek}
          onChange={(e) => setPerWeek(Number(e.target.value))}
          style={{ display: "block", width: "100%" }}
        />
      </label>

      <label>
        {t.create.equipment}
        <select
          value={equipment}
          onChange={(e) => setEquipment(e.target.value)}
          style={{ display: "block", width: "100%" }}
        >
          {EQUIPMENT.map((q) => (
            <option key={q} value={q}>
              {t.equipment[q]}
            </option>
          ))}
        </select>
      </label>

      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={saving}>
        {saving ? t.create.saving : t.create.submit}
      </button>
    </form>
  );
}
