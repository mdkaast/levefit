import { useCallback, useEffect, useState } from "react";
import { getNutritionDay, type DiaryEntry, type Meal, type NutritionDay } from "../api";
import { FLAGS } from "../flags";
import { t } from "../i18n";
import { formatKcal, macroLine, share } from "../nutrition";
import { Button, Card, EmptyState, ListRow, ProgressRing, Segmented, Skeleton } from "../ui/ui";
import { FoodAdd } from "./FoodAdd";
import { NutritionGoal } from "./NutritionGoal";
import { RecipeDetail } from "./RecipeDetail";
import { Recipes } from "./Recipes";

type Mode = "diary" | "recipes";
type View =
  | { kind: "list" }
  | { kind: "add"; meal: Meal; entry?: DiaryEntry }
  | { kind: "goal" }
  | { kind: "recipe"; id: number; meal?: Meal };

/** Вкладка «Питание»: дневник и рецепты, добавление еды, цель по калориям. */
export function Nutrition() {
  const n = t.nutrition;
  const [mode, setMode] = useState<Mode>("diary");
  const [view, setView] = useState<View>({ kind: "list" });
  const [day, setDay] = useState<NutritionDay | null>(null);
  const [failed, setFailed] = useState(false);

  const load = useCallback(() => {
    setFailed(false);
    getNutritionDay()
      .then(setDay)
      .catch(() => setFailed(true));
  }, []);

  useEffect(() => {
    if (FLAGS.nutrition) load();
  }, [load]);

  if (!FLAGS.nutrition) {
    return (
      <main>
        <h1>{n.title}</h1>
        <EmptyState title={n.soonTitle} text={n.soonText} />
      </main>
    );
  }

  const back = () => {
    setView({ kind: "list" });
    load();
  };

  if (view.kind === "add") {
    return (
      <main>
        <FoodAdd meal={view.meal} entry={view.entry} onBack={back} />
      </main>
    );
  }
  if (view.kind === "goal") {
    return (
      <main>
        <NutritionGoal onBack={back} />
      </main>
    );
  }
  if (view.kind === "recipe") {
    return (
      <main>
        <RecipeDetail id={view.id} meal={view.meal} onBack={back} onAdded={back} />
      </main>
    );
  }

  const goal = day?.goal ?? null;
  const items = [
    { id: "diary" as const, label: n.modes.diary },
    { id: "recipes" as const, label: n.modes.recipes },
  ];

  return (
    <main>
      <h1>{n.title}</h1>
      <Segmented items={items} value={mode} onChange={setMode} />

      {mode === "recipes" && <Recipes onOpen={(id) => setView({ kind: "recipe", id })} />}

      {mode === "diary" && (
        <>
          {failed && (
            <EmptyState
              title={n.loadError}
              text=""
              action={
                <Button variant="secondary" onClick={load}>
                  {n.retry}
                </Button>
              }
            />
          )}
          {!failed && !day && <Skeleton height={180} />}
          {day && (
            <>
              <Card>
                <div className="nutri-ring">
                  <ProgressRing
                    value={share(day.totals.kcal, goal?.kcal)}
                    size={112}
                    label={n.eaten}
                  >
                    {formatKcal(day.totals.kcal)}
                  </ProgressRing>
                  <div>
                    <small className="muted">{n.eaten}</small>
                    <b className="num">
                      {goal ? `${formatKcal(day.totals.kcal)} / ${formatKcal(goal.kcal)}` : formatKcal(day.totals.kcal)}{" "}
                      {n.kcal}
                    </b>
                    {day.remaining && <small className="muted">{n.remaining(Math.round(day.remaining.kcal))}</small>}
                  </div>
                </div>
                {(["protein", "fat", "carbs"] as const).map((key) => {
                  const target = goal ? { protein: goal.protein_g, fat: goal.fat_g, carbs: goal.carbs_g }[key] : undefined;
                  return (
                    <div key={key} className="vol-row">
                      <span>{n[key]}</span>
                      <div className="ui-bar" aria-hidden="true">
                        <i style={{ width: `${share(day.totals[key], target) * 100}%` }} />
                      </div>
                      <b className="num">{macroLine(day.totals[key], target)}</b>
                    </div>
                  );
                })}
                {day.hints.map((hint) => (
                  <small key={hint} className="muted">
                    {hint}
                  </small>
                ))}
              </Card>

              {!day.complete && (
                <Card accent>
                  <h3>{n.noGoalTitle}</h3>
                  <p className="muted">{n.noGoalText}</p>
                </Card>
              )}
              <ListRow
                title={n.goal}
                hint={goal ? `${n.goalScreen.modes[goal.mode]} · ${formatKcal(goal.kcal)} ${n.kcal}` : n.goalLink}
                onClick={() => setView({ kind: "goal" })}
              />

              {day.meals.map((meal) => (
                <Card key={meal.meal}>
                  <div className="row">
                    <h3>{n.meals[meal.meal]}</h3>
                    <b className="num">{meal.totals.kcal ? `${formatKcal(meal.totals.kcal)} ${n.kcal}` : ""}</b>
                  </div>
                  {meal.entries.length === 0 && <small className="muted">{n.emptyMeal}</small>}
                  <div className="stack">
                    {meal.entries.map((entry) => (
                      <ListRow
                        key={entry.id}
                        title={entry.name}
                        hint={`${entry.grams ? `${Math.round(entry.grams)} ${n.gramsShort}` : `${entry.servings} порц.`} · Б ${Math.round(entry.protein)}`}
                        trailing={<b className="num">{entry.kcal}</b>}
                        onClick={() => setView({ kind: "add", meal: meal.meal, entry })}
                      />
                    ))}
                  </div>
                  <Button variant="secondary" onClick={() => setView({ kind: "add", meal: meal.meal })}>
                    + {n.addFood}
                  </Button>
                </Card>
              ))}
              <small className="muted">{n.estimate}</small>
            </>
          )}
        </>
      )}
    </main>
  );
}
