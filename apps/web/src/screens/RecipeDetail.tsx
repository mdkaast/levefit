import { useEffect, useState } from "react";
import { addDiaryEntry, getRecipe, type Meal, type RecipeDetailData } from "../api";
import { t } from "../i18n";
import { defaultMeal, MEALS } from "../nutrition";
import { Button, Card, Chip, EmptyState, Hint, Skeleton, Stepper } from "../ui/ui";

type Props = { id: number; meal?: Meal; onBack: () => void; onAdded: () => void };

/** Рецепт: КБЖУ на порцию, масштаб порций, ингредиенты, шаги и добавление в дневник. */
export function RecipeDetail({ id, meal: initialMeal, onBack, onAdded }: Props) {
  const r = t.nutrition.recipes;
  const n = t.nutrition;
  const [servings, setServings] = useState(1);
  const [data, setData] = useState<RecipeDetailData | null>(null);
  const [meal, setMeal] = useState<Meal>(initialMeal ?? defaultMeal(new Date().getHours()));
  const [failed, setFailed] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getRecipe(id, servings)
      .then(setData)
      .catch(() => setFailed(true));
  }, [id, servings]);

  const back = (
    <Button variant="text" onClick={onBack}>
      ‹ {r.back}
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
  if (!data) {
    return (
      <>
        {back}
        <Skeleton height={32} width="70%" />
        <Skeleton height={140} />
      </>
    );
  }

  async function add() {
    setSaving(true);
    try {
      await addDiaryEntry({ meal, recipe_id: id, servings });
      onAdded();
    } catch {
      setSaving(false);
    }
  }

  const per = data.per_serving;
  return (
    <>
      {back}
      <p className="kicker">{data.meal_name}</p>
      <h1>{data.name}</h1>
      <Card>
        <div className="macro-tiles">
          <div>
            <small>{n.kcal}</small>
            <b className="num">{per.kcal}</b>
          </div>
          <div>
            <small>Б</small>
            <b className="num">{per.protein}</b>
          </div>
          <div>
            <small>Ж</small>
            <b className="num">{per.fat}</b>
          </div>
          <div>
            <small>У</small>
            <b className="num">{per.carbs}</b>
          </div>
        </div>
        <small className="muted">
          {r.per} · {r.minutes(data.minutes)}
        </small>
      </Card>

      <h3>{r.servings}</h3>
      <Stepper value={servings} min={1} max={6} label={r.servings} onChange={setServings} />

      <h3>{r.ingredients}</h3>
      <ul className="plain-list">
        {data.ingredients.map((item) => (
          <li key={item.name}>
            <span>{item.name}</span>
            <b className="num">{item.grams} г</b>
          </li>
        ))}
      </ul>

      <h3>{r.steps}</h3>
      <ol className="steps">
        {data.steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>

      <div className="chip-row" role="group">
        {MEALS.map((m) => (
          <Chip key={m} selected={meal === m} onClick={() => setMeal(m)}>
            {n.meals[m]}
          </Chip>
        ))}
      </div>
      <Button loading={saving} onClick={add}>
        {r.addTo}
      </Button>
      <Hint>{data.note}</Hint>
    </>
  );
}
