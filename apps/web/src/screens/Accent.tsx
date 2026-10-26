import { useEffect, useRef, useState } from "react";
import {
  getMe,
  patchCharacter,
  previewWeek,
  putAccent,
  type DirectionInfo,
  type WeekPreview,
} from "../api";
import { FocusSilhouette } from "../body/FocusSilhouette";
import type { Sex } from "../body/model";
import { sameSelection, shortDate, toggleAccent } from "../directions";
import { t } from "../i18n";
import { Button, Chip, Hint, Segmented } from "../ui/ui";
import { WeekChanges } from "./WeekChanges";

type Props = {
  info: DirectionInfo;
  /** Акцент, который будет действовать со следующего понедельника. */
  initial: string[];
  nextMonday: string;
  onBack: () => void;
  onSaved: () => void;
};

/** Выбор акцента направления: группы мышц на силуэте (до двух) или качества. Применяется с понедельника. */
export function Accent({ info, initial, nextMonday, onBack, onSaved }: Props) {
  const d = t.directions;
  const muscles = info.accent_kind === "muscles";
  const [selection, setSelection] = useState<string[]>(initial);
  const [sex, setSex] = useState<Sex | null>(null);
  const [preview, setPreview] = useState<WeekPreview | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(false);
  const request = useRef(0);
  const names = Object.fromEntries(info.options.map((o) => [o.key, o.name]));

  useEffect(() => {
    getMe()
      .then(({ character }) => {
        const saved = character?.silhouette;
        if (saved === "male" || saved === "female") setSex(saved);
        else if (character?.gender === "male" || character?.gender === "female") setSex(character.gender);
        else setSex("female");
      })
      .catch(() => setSex("female"));
  }, []);

  // Предпросмотр «до / после» пересчитывается после паузы, чтобы не слать запрос на каждое касание.
  useEffect(() => {
    if (sameSelection(selection, initial)) {
      setPreview(null);
      return;
    }
    const id = ++request.current;
    const timer = setTimeout(() => {
      previewWeek({ accent: { direction: info.key, selection } })
        .then((result) => id === request.current && setPreview(result))
        .catch(() => id === request.current && setPreview(null));
    }, 350);
    return () => clearTimeout(timer);
  }, [selection, initial, info.key]);

  function chooseSex(next: Sex) {
    setSex(next);
    patchCharacter({ silhouette: next }).catch(() => undefined);
  }

  async function apply() {
    setSaving(true);
    setError(false);
    try {
      await putAccent(info.key, selection);
      onSaved();
    } catch {
      setError(true);
      setSaving(false);
    }
  }

  const toggle = (key: string) => setSelection((current) => toggleAccent(current, key));
  const changed = !sameSelection(selection, initial);

  return (
    <>
      <Button variant="text" onClick={onBack}>
        ‹ {d.back}
      </Button>
      <p className="kicker">{info.name}</p>
      <h1>{muscles ? d.accentMuscles : d.accentQualities}</h1>
      <p className="muted">{muscles ? d.accentHintMuscles : d.accentHintQualities}</p>

      {muscles && sex && (
        <>
          <Segmented
            items={[
              { id: "female" as const, label: d.silhouette.female },
              { id: "male" as const, label: d.silhouette.male },
            ]}
            value={sex}
            onChange={chooseSex}
          />
          <FocusSilhouette
            sex={sex}
            selected={selection}
            names={names}
            onToggle={toggle}
            label={d.silhouette.frontBack}
          />
        </>
      )}

      <div className="chip-row wrap" role="group" aria-label={info.name}>
        {info.options.map((option) => (
          <Chip key={option.key} selected={selection.includes(option.key)} onClick={() => toggle(option.key)}>
            {selection.includes(option.key) ? `✓ ${option.name}` : option.name}
          </Chip>
        ))}
      </div>

      {!info.verified && <Hint>{d.unverified}</Hint>}
      {changed && preview && <WeekChanges preview={preview} />}
      {changed && <p className="muted">{d.effective(shortDate(nextMonday))}</p>}
      {error && <p role="alert">{d.error}</p>}
      <Button disabled={!changed} loading={saving} onClick={apply}>
        {saving ? d.applying : d.apply}
      </Button>
    </>
  );
}
