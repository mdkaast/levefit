import { useState } from "react";
import { createCharacter, type Character } from "../api";
import { NeonAthlete } from "../components/NeonAthlete";
import { Silhouette } from "../components/Silhouette";
import { Icon } from "../icons";
import { t } from "../i18n";
import { NAME_MAX_LEN, parseAge, parseHeight, parseWeight, validateName } from "../validation";

type Props = { onCreated: (character: Character) => void };

const STEPS = [
  "name",
  "gender",
  "age",
  "body",
  "goal",
  "experience",
  "schedule",
  "muscles",
] as const;
type Step = (typeof STEPS)[number];

const GENDERS = ["male", "female", "other"] as const;
const GOALS = ["mass", "strength", "shape", "weight_loss"] as const;
const LEVELS = ["beginner", "intermediate", "advanced"] as const;
const EQUIPMENT = ["gym", "home", "none"] as const;
const MUSCLES = ["chest", "back", "shoulders", "arms", "legs", "core"] as const;

type Values = {
  name: string;
  gender: string;
  age: string;
  height: string;
  weight: string;
  goal: string;
  experience: string;
  perWeek: number;
  equipment: string;
  muscles: string[];
};

const INITIAL: Values = {
  name: "",
  gender: "",
  age: "",
  height: "",
  weight: "",
  goal: "",
  experience: "",
  perWeek: 3,
  equipment: "gym",
  muscles: [],
};

function canContinue(step: Step, v: Values): boolean {
  switch (step) {
    case "name":
      return validateName(v.name) === null;
    case "gender":
      return v.gender !== "";
    case "age":
      return parseAge(v.age) !== null;
    case "body":
      return parseHeight(v.height) !== null && parseWeight(v.weight) !== null;
    case "goal":
      return v.goal !== "";
    case "experience":
      return v.experience !== "";
    case "schedule":
      return v.perWeek >= 1 && v.perWeek <= 7 && v.equipment !== "";
    case "muscles":
      return v.muscles.length > 0;
  }
}

type PickProps<T extends string> = {
  items: readonly T[];
  value: string;
  labels: Record<T, string>;
  onPick: (item: T) => void;
};

function SinglePick<T extends string>({ items, value, labels, onPick }: PickProps<T>) {
  return (
    <div className="options">
      {items.map((item) => (
        <button
          key={item}
          type="button"
          className="option"
          aria-pressed={value === item}
          onClick={() => onPick(item)}
        >
          {labels[item]}
        </button>
      ))}
    </div>
  );
}

export function Onboarding({ onCreated }: Props) {
  const [index, setIndex] = useState(-1); // -1 — приветствие
  const [values, setValues] = useState<Values>(INITIAL);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = <K extends keyof Values>(key: K, value: Values[K]) =>
    setValues((previous) => ({ ...previous, [key]: value }));

  if (index === -1) {
    return (
      <div className="onboarding welcome">
        <div className="art">
          <NeonAthlete />
        </div>
        <p className="brand">{t.appTitle}</p>
        <h1>{t.onboarding.welcomeTitle}</h1>
        <p className="muted" style={{ marginTop: 10 }}>
          {t.onboarding.welcomeText}
        </p>
        <div className="actions">
          <button type="button" onClick={() => setIndex(0)}>
            {t.onboarding.start}
            <Icon name="arrow" />
          </button>
        </div>
      </div>
    );
  }

  const step = STEPS[index];
  const last = index === STEPS.length - 1;
  const texts = t.onboarding.steps[step];

  async function submit() {
    setSaving(true);
    setError(null);
    try {
      const character = await createCharacter({
        name: values.name.trim(),
        goal: values.goal,
        workouts_per_week: values.perWeek,
        equipment: values.equipment,
        gender: values.gender,
        age: parseAge(values.age),
        height_cm: parseHeight(values.height),
        weight_kg: parseWeight(values.weight),
        experience: values.experience,
        target_muscles: values.muscles,
      });
      onCreated(character);
    } catch {
      setError(t.create.error);
      setSaving(false);
    }
  }

  function next() {
    if (!canContinue(step, values)) return;
    if (last) void submit();
    else setIndex(index + 1);
  }

  const toggleMuscle = (muscle: string) =>
    set(
      "muscles",
      values.muscles.includes(muscle)
        ? values.muscles.filter((m) => m !== muscle)
        : [...values.muscles, muscle],
    );

  return (
    <div className="onboarding">
      <div className="top">
        <button type="button" className="back" onClick={() => setIndex(index - 1)}>
          {t.onboarding.back}
        </button>
        <div className="steps" role="progressbar" aria-valuenow={index + 1} aria-valuemax={STEPS.length}>
          {STEPS.map((name, i) => (
            <i key={name} className={i <= index ? "done" : ""} />
          ))}
        </div>
      </div>

      <div className="body">
        <div>
          <h1>{texts.title}</h1>
          <p className="hint">{texts.hint}</p>
        </div>

        {step === "name" && (
          <input
            autoFocus
            value={values.name}
            maxLength={NAME_MAX_LEN}
            placeholder={t.create.namePlaceholder}
            onChange={(e) => set("name", e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && next()}
          />
        )}

        {step === "gender" && (
          <SinglePick
            items={GENDERS}
            value={values.gender}
            labels={t.onboarding.gender}
            onPick={(item) => set("gender", item)}
          />
        )}

        {step === "age" && (
          <div className="big-field" style={{ gridTemplateColumns: "1fr" }}>
            <input
              inputMode="numeric"
              autoFocus
              value={values.age}
              placeholder={t.onboarding.age}
              onChange={(e) => set("age", e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && next()}
            />
          </div>
        )}

        {step === "body" && (
          <div className="big-field">
            <label>
              {t.onboarding.height}
              <input
                inputMode="numeric"
                value={values.height}
                onChange={(e) => set("height", e.target.value)}
              />
            </label>
            <label>
              {t.onboarding.weight}
              <input
                inputMode="decimal"
                value={values.weight}
                onChange={(e) => set("weight", e.target.value)}
              />
            </label>
          </div>
        )}

        {step === "goal" && (
          <SinglePick
            items={GOALS}
            value={values.goal}
            labels={t.goals}
            onPick={(item) => set("goal", item)}
          />
        )}

        {step === "experience" && (
          <SinglePick
            items={LEVELS}
            value={values.experience}
            labels={t.onboarding.experience}
            onPick={(item) => set("experience", item)}
          />
        )}

        {step === "schedule" && (
          <>
            <div className="stepper">
              <button
                type="button"
                aria-label="−"
                onClick={() => set("perWeek", Math.max(1, values.perWeek - 1))}
              >
                −
              </button>
              <output>{values.perWeek}</output>
              <button
                type="button"
                aria-label="+"
                onClick={() => set("perWeek", Math.min(7, values.perWeek + 1))}
              >
                +
              </button>
            </div>
            <p className="muted" style={{ textAlign: "center" }}>
              {t.onboarding.perWeek}
            </p>
            <SinglePick
              items={EQUIPMENT}
              value={values.equipment}
              labels={t.equipment}
              onPick={(item) => set("equipment", item)}
            />
          </>
        )}

        {step === "muscles" && (
          <div className="muscles-pick">
            <div className="options multi">
              {MUSCLES.map((muscle) => (
                <button
                  key={muscle}
                  type="button"
                  className="option"
                  aria-pressed={values.muscles.includes(muscle)}
                  onClick={() => toggleMuscle(muscle)}
                >
                  {t.onboarding.muscles[muscle]}
                </button>
              ))}
            </div>
            <Silhouette selected={values.muscles} onToggle={toggleMuscle} />
          </div>
        )}

        {error && <p role="alert">{error}</p>}
      </div>

      <button
        type="button"
        className="cta"
        disabled={!canContinue(step, values) || saving}
        onClick={next}
      >
        {saving ? t.onboarding.saving : last ? t.onboarding.finish : t.onboarding.next}
        <Icon name="arrow" />
      </button>
    </div>
  );
}
