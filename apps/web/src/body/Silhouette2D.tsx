import type { MuscleKey, Sex } from "./model";

/** Группы, для которых в макетах есть PNG-оверлей (`public/silhouettes/<m|f>_<ключ>.png`). */
const OVERLAY: Record<MuscleKey, string> = {
  chest: "chest",
  biceps: "biceps",
  triceps: "triceps",
  delts: "delts",
  abs: "abs",
  lats: "lats",
  glutes: "glutes",
  quads: "quads",
};

type Props = {
  sex: Sex;
  selected?: readonly MuscleKey[];
  label: string;
};

/** Запасной 2D-силуэт: базовое тело и поверх него подсветка выбранных групп. */
export function Silhouette2D({ sex, selected = [], label }: Props) {
  const prefix = sex === "male" ? "m" : "f";
  return (
    <div className="silhouette2d" role="img" aria-label={label}>
      <img src={`/silhouettes/${prefix}_base.png`} alt="" loading="lazy" />
      {selected.map((key) => (
        <img key={key} src={`/silhouettes/${prefix}_${OVERLAY[key]}.png`} alt="" loading="lazy" />
      ))}
    </div>
  );
}
