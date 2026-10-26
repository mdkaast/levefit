import { type MuscleKey, MUSCLE_KEYS, type Sex } from "./model";
import { Silhouette2D } from "./Silhouette2D";
import meta from "./silhouette-meta.json";

type Meta = Record<"m" | "f", { w: number; h: number; parts: Record<string, number[]> }>;
const SIZES = meta as unknown as Meta;

type Props = {
  sex: Sex;
  selected: readonly string[];
  names: Record<string, string>;
  onToggle: (key: MuscleKey) => void;
  label: string;
};

/** Силуэт спереди и сзади: нажатие по группе включает акцент. Те же группы доступны чипами выше. */
export function FocusSilhouette({ sex, selected, names, onToggle, label }: Props) {
  const prefix = sex === "male" ? "m" : "f";
  const { w, h, parts } = SIZES[prefix];
  // большие зоны (плечи) рисуем первыми, чтобы маленькие (грудь) оставались нажимаемыми
  const ordered = MUSCLE_KEYS.filter((k) => parts[k]).sort((a, b) => area(parts[b]) - area(parts[a]));
  return (
    <div className="focus-silhouette">
      <Silhouette2D sex={sex} selected={selected.filter(isMuscle)} label={label} />
      {ordered.map((key) => {
        const [x0, y0, x1, y1] = parts[key];
        const on = selected.includes(key);
        return (
          <button
            key={key}
            type="button"
            className={`hotspot${on ? " on" : ""}`}
            aria-label={names[key] ?? key}
            aria-pressed={on}
            style={{
              left: `${(x0 / w) * 100}%`,
              top: `${(y0 / h) * 100}%`,
              width: `${((x1 - x0) / w) * 100}%`,
              height: `${((y1 - y0) / h) * 100}%`,
            }}
            onClick={() => onToggle(key)}
          >
            {on && <span aria-hidden="true">✓</span>}
          </button>
        );
      })}
    </div>
  );
}

function area(box: number[]): number {
  return (box[2] - box[0]) * (box[3] - box[1]);
}

function isMuscle(key: string): key is MuscleKey {
  return (MUSCLE_KEYS as readonly string[]).includes(key);
}
