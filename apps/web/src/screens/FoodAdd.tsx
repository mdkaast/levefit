import { useEffect, useState } from "react";
import {
  addDiaryEntry,
  createFood,
  deleteDiaryEntry,
  getRecentFoods,
  patchDiaryEntry,
  searchFoods,
  type DiaryEntry,
  type FoodItem,
  type Meal,
} from "../api";
import { t } from "../i18n";
import { foodMacros, gramsToPieces, MEALS, piecesToGrams } from "../nutrition";
import { Button, Card, Chip, EmptyState, Hint, ListRow, Stepper } from "../ui/ui";

type Props = { meal: Meal; entry?: DiaryEntry; onBack: () => void };

const DEFAULT_GRAMS = 200;

/** Добавление еды: поиск, частые продукты, граммы шаговым счётчиком, правка и удаление записи. */
export function FoodAdd({ meal: initialMeal, entry, onBack }: Props) {
  const a = t.nutrition.add;
  const n = t.nutrition;
  const [meal, setMeal] = useState<Meal>(initialMeal);
  const [query, setQuery] = useState("");
  const [found, setFound] = useState<FoodItem[]>([]);
  const [groups, setGroups] = useState<{ key: string; name: string }[]>([]);
  const [group, setGroup] = useState<string | undefined>();
  const [frequent, setFrequent] = useState<FoodItem[]>([]);
  const [recent, setRecent] = useState<FoodItem[]>([]);
  const [picked, setPicked] = useState<FoodItem | null>(null);
  const [grams, setGrams] = useState(entry?.grams ?? DEFAULT_GRAMS);
  const [own, setOwn] = useState(false);
  const [draft, setDraft] = useState({ name: "", kcal: "", protein: "", fat: "", carbs: "" });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Правка записи: продукт нужен только для пересчёта КБЖУ, поэтому ищем его по названию.
  useEffect(() => {
    if (!entry || !entry.food_id) return;
    searchFoods(entry.name)
      .then((r) => setPicked(r.items.find((f) => f.id === entry.food_id) ?? null))
      .catch(() => undefined);
  }, [entry]);

  useEffect(() => {
    getRecentFoods()
      .then((r) => {
        setFrequent(r.frequent);
        setRecent(r.recent);
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchFoods(query, group)
        .then((r) => {
          setFound(r.items);
          setGroups(r.groups);
        })
        .catch(() => undefined);
    }, 250);
    return () => clearTimeout(timer);
  }, [query, group]);

  const pick = (food: FoodItem) => {
    setPicked(food);
    setGrams(food.last_grams ?? DEFAULT_GRAMS);
    setError(null);
  };

  async function save() {
    if (!picked && !entry) return;
    setSaving(true);
    setError(null);
    try {
      if (entry) await patchDiaryEntry(entry.id, { grams, meal });
      else if (picked) await addDiaryEntry({ meal, food_id: picked.id, grams });
      onBack();
    } catch {
      setError(a.error);
      setSaving(false);
    }
  }

  async function remove() {
    if (!entry) return;
    await deleteDiaryEntry(entry.id).catch(() => undefined);
    onBack();
  }

  async function createOwn() {
    const body = {
      name: draft.name.trim(),
      kcal: Number(draft.kcal.replace(",", ".")),
      protein: Number(draft.protein.replace(",", ".")),
      fat: Number(draft.fat.replace(",", ".")),
      carbs: Number(draft.carbs.replace(",", ".")),
    };
    try {
      const food = await createFood(body);
      setOwn(false);
      pick(food);
    } catch {
      setError(a.ownError);
    }
  }

  const header = (
    <>
      <Button variant="text" onClick={onBack}>
        ‹ {n.goalScreen.back}
      </Button>
      <h1>{entry ? entry.name : a.title}</h1>
      <div className="chip-row" role="group" aria-label={a.meal}>
        {MEALS.map((m) => (
          <Chip key={m} selected={meal === m} onClick={() => setMeal(m)}>
            {n.meals[m]}
          </Chip>
        ))}
      </div>
    </>
  );

  if (picked || entry) {
    const base = picked ?? { kcal: entry?.kcal ?? 0, protein: entry?.protein ?? 0, fat: entry?.fat ?? 0, carbs: entry?.carbs ?? 0, piece_g: null, piece_name: null, name: entry?.name ?? "" };
    const per100 = picked
      ? { kcal: picked.kcal, protein: picked.protein, fat: picked.fat, carbs: picked.carbs }
      : entry && entry.grams
        ? {
            kcal: (entry.kcal / entry.grams) * 100,
            protein: (entry.protein / entry.grams) * 100,
            fat: (entry.fat / entry.grams) * 100,
            carbs: (entry.carbs / entry.grams) * 100,
          }
        : { kcal: base.kcal, protein: base.protein, fat: base.fat, carbs: base.carbs };
    const m = foodMacros(per100, grams);
    const pieceG = picked?.piece_g ?? null;
    return (
      <>
        {header}
        <Card>
          <h3>{picked?.name ?? entry?.name}</h3>
          <small className="muted">
            {a.per100}: {Math.round(per100.kcal)} {n.kcal} · Б {Math.round(per100.protein)} · Ж {Math.round(per100.fat)} · У{" "}
            {Math.round(per100.carbs)}
          </small>
          <Stepper
            value={grams}
            min={5}
            max={2000}
            step={10}
            label={a.grams}
            format={(v) => `${v} ${n.gramsShort}`}
            onChange={setGrams}
          />
          {pieceG && picked?.piece_name && (
            <>
              <small className="muted">{a.piece(picked.piece_name)}</small>
              <Stepper
                value={gramsToPieces(grams, pieceG)}
                min={1}
                max={40}
                label={picked.piece_name}
                format={(v) => `${v} ${picked.piece_name?.split(" ")[0] ?? "шт."}`}
                onChange={(pieces) => setGrams(piecesToGrams(pieces, pieceG))}
              />
            </>
          )}
          <div className="macro-tiles">
            <div>
              <small>{n.kcal}</small>
              <b className="num">{m.kcal}</b>
            </div>
            <div>
              <small>Б</small>
              <b className="num">{m.protein}</b>
            </div>
            <div>
              <small>Ж</small>
              <b className="num">{m.fat}</b>
            </div>
            <div>
              <small>У</small>
              <b className="num">{m.carbs}</b>
            </div>
          </div>
        </Card>
        {error && <p role="alert">{error}</p>}
        <Button loading={saving} onClick={save}>
          {entry ? a.save : a.submit}
        </Button>
        {entry && (
          <Button variant="secondary" onClick={remove}>
            {a.remove}
          </Button>
        )}
        <Hint>{n.estimate}</Hint>
      </>
    );
  }

  if (own) {
    const field = (key: keyof typeof draft, label: string, numeric = true) => (
      <label>
        {label}
        <input
          inputMode={numeric ? "decimal" : "text"}
          value={draft[key]}
          onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
        />
      </label>
    );
    return (
      <>
        {header}
        <Card>
          <h3>{a.own}</h3>
          <small className="muted">{a.ownHint}</small>
          {field("name", a.ownName, false)}
          {field("kcal", `${n.kcal}`)}
          {field("protein", n.protein)}
          {field("fat", n.fat)}
          {field("carbs", n.carbs)}
        </Card>
        {error && <p role="alert">{error}</p>}
        <Button onClick={createOwn} disabled={draft.name.trim().length < 2}>
          {a.ownCreate}
        </Button>
        <Button variant="text" onClick={() => setOwn(false)}>
          {n.goalScreen.back}
        </Button>
      </>
    );
  }

  const list = (items: FoodItem[]) => (
    <div className="stack">
      {items.map((food) => (
        <ListRow
          key={food.id}
          title={food.name}
          hint={`${Math.round(food.kcal)} ${n.kcal} · Б ${Math.round(food.protein)} · на 100 г`}
          onClick={() => pick(food)}
        />
      ))}
    </div>
  );

  return (
    <>
      {header}
      <input
        type="search"
        value={query}
        placeholder={a.search}
        aria-label={a.search}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="chip-row">
        <Chip selected={!group} onClick={() => setGroup(undefined)}>
          {a.groups}
        </Chip>
        {groups.map((g) => (
          <Chip key={g.key} selected={group === g.key} onClick={() => setGroup(g.key)}>
            {g.name}
          </Chip>
        ))}
      </div>
      {!query && !group && frequent.length > 0 && (
        <>
          <h3>{a.frequent}</h3>
          {list(frequent)}
        </>
      )}
      {!query && !group && recent.length > 0 && (
        <>
          <h3>{a.recent}</h3>
          {list(recent)}
        </>
      )}
      <h3>{a.results}</h3>
      {found.length === 0 ? <EmptyState title={a.empty} text="" /> : list(found)}
      <Button variant="secondary" onClick={() => setOwn(true)}>
        + {a.own}
      </Button>
    </>
  );
}
