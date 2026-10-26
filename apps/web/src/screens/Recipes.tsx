import { useEffect, useState } from "react";
import { listRecipes, suggestRecipes, type RecipeCard } from "../api";
import { t } from "../i18n";
import { Chip, EmptyState, Hint, ListRow, Skeleton, Tag } from "../ui/ui";

type Props = { onOpen: (id: number) => void };
type Filter = "for_you" | "all" | string;
type Training = "before" | "after" | undefined;

/** Рецепты: «Под вас» с причиной выбора и фильтры по тегам. */
export function Recipes({ onOpen }: Props) {
  const r = t.nutrition.recipes;
  const [filter, setFilter] = useState<Filter>("for_you");
  const [training, setTraining] = useState<Training>(undefined);
  const [tags, setTags] = useState<{ key: string; name: string }[]>([]);
  const [items, setItems] = useState<RecipeCard[] | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setItems(null);
    setFailed(false);
    const done = (cards: RecipeCard[], text: string | null) => {
      setItems(cards);
      setSummary(text);
    };
    if (filter === "for_you") {
      suggestRecipes(training)
        .then((res) => done(res.items, res.summary))
        .catch(() => setFailed(true));
    } else {
      listRecipes(filter === "all" ? undefined : filter)
        .then((res) => {
          setTags(res.tags);
          done(res.items, null);
        })
        .catch(() => setFailed(true));
    }
  }, [filter, training]);

  useEffect(() => {
    listRecipes()
      .then((res) => setTags(res.tags))
      .catch(() => undefined);
  }, []);

  // «До тренировки» и «После тренировки» для подбора, остальные теги для списка
  const quickTags = tags.filter((tag) => ["protein", "quick", "pre", "post_run", "light"].includes(tag.key));

  return (
    <>
      <div className="chip-row">
        <Chip selected={filter === "for_you"} onClick={() => setFilter("for_you")}>
          {r.forYou}
        </Chip>
        <Chip selected={filter === "all"} onClick={() => setFilter("all")}>
          {r.all}
        </Chip>
        {quickTags.map((tag) => (
          <Chip key={tag.key} selected={filter === tag.key} onClick={() => setFilter(tag.key)}>
            {tag.name}
          </Chip>
        ))}
      </div>
      {filter === "for_you" && (
        <>
          <div className="chip-row">
            <Chip selected={training === "before"} onClick={() => setTraining(training === "before" ? undefined : "before")}>
              {r.beforeTraining}
            </Chip>
            <Chip selected={training === "after"} onClick={() => setTraining(training === "after" ? undefined : "after")}>
              {r.afterTraining}
            </Chip>
          </div>
          {summary && <Hint>{summary}</Hint>}
        </>
      )}
      {failed && <EmptyState title={t.nutrition.loadError} text="" />}
      {!failed && items === null && (
        <div className="stack">
          <Skeleton height={72} />
          <Skeleton height={72} />
          <Skeleton height={72} />
        </div>
      )}
      {items && items.length === 0 && <EmptyState title={r.empty} text="" />}
      {items && items.length > 0 && filter !== "for_you" && <small className="kicker">{r.count(items.length)}</small>}
      <div className="stack">
        {items?.map((card) => (
          <div key={card.id} className="recipe-card">
            <ListRow
              title={card.name}
              hint={`${card.kcal} ккал · Б ${card.protein} г · ${r.minutes(card.minutes)}`}
              trailing={card.tags.includes("protein") ? <Tag tone="fit">Белок</Tag> : undefined}
              onClick={() => onOpen(card.id)}
            />
            {card.reason && <small className="muted recipe-reason">{card.reason}</small>}
          </div>
        ))}
      </div>
    </>
  );
}
