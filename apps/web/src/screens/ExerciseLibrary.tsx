import { useCallback, useEffect, useState } from "react";
import {
  getCatalogGroups,
  searchExercises,
  type CatalogGroup,
  type ExerciseItem,
} from "../api";
import { plural } from "../format";
import { t } from "../i18n";
import { Button, Chip, EmptyState, ListRow, Skeleton, Tag } from "../ui/ui";

type Props = { onOpen: (id: number) => void };

const PAGE = 40;

/** Библиотека упражнений: поиск, группы мышц, «подходит вам» и счётчик «из 374». */
export function ExerciseLibrary({ onOpen }: Props) {
  const c = t.catalog;
  const [groups, setGroups] = useState<CatalogGroup[]>([]);
  const [group, setGroup] = useState<string | undefined>();
  const [fits, setFits] = useState(false);
  const [text, setText] = useState("");
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<ExerciseItem[] | null>(null);
  const [total, setTotal] = useState(0);
  const [catalogTotal, setCatalogTotal] = useState(0);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getCatalogGroups()
      .then(setGroups)
      .catch(() => undefined);
  }, []);

  // Поиск откладываем на 300 мс после ввода, чтобы не слать запрос на каждую букву.
  useEffect(() => {
    const timer = setTimeout(() => setQuery(text), 300);
    return () => clearTimeout(timer);
  }, [text]);

  const load = useCallback(
    (offset: number) => {
      setFailed(false);
      searchExercises({ q: query, group, fits, limit: PAGE, offset })
        .then((result) => {
          setTotal(result.total);
          setCatalogTotal(result.catalog_total);
          setItems((prev) => (offset === 0 || !prev ? result.items : [...prev, ...result.items]));
        })
        .catch(() => setFailed(true));
    },
    [query, group, fits],
  );

  useEffect(() => {
    setItems(null);
    load(0);
  }, [load]);

  const noun = plural(
    catalogTotal,
    c.exercisesCount.split("|")[0],
    c.exercisesCount.split("|")[1],
    c.exercisesCount.split("|")[2],
  );

  return (
    <>
      <p className="kicker">
        {c.library} · {catalogTotal || ""} {catalogTotal ? noun : ""}
      </p>
      <input
        type="search"
        value={text}
        placeholder={c.search}
        aria-label={c.search}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="chip-row" role="group" aria-label={c.muscles}>
        <Chip selected={!group} onClick={() => setGroup(undefined)}>
          {c.allGroups}
        </Chip>
        {groups.map((g) => (
          <Chip key={g.key} selected={group === g.key} onClick={() => setGroup(g.key)}>
            {g.name}
          </Chip>
        ))}
      </div>
      <div className="row">
        <small className="kicker">{items ? c.found(items.length, total) : ""}</small>
        <Chip selected={fits} onClick={() => setFits((v) => !v)}>
          {c.onlyFits}
        </Chip>
      </div>

      {failed && (
        <EmptyState
          title={c.loadError}
          text=""
          action={<Button variant="secondary" onClick={() => load(0)}>{c.retry}</Button>}
        />
      )}
      {!failed && items === null && (
        <div className="stack">
          <Skeleton height={56} />
          <Skeleton height={56} />
          <Skeleton height={56} />
        </div>
      )}
      {items && items.length === 0 && <EmptyState title={c.empty} text="" />}
      <div className="stack">
        {items?.map((item) => (
          <ListRow
            key={item.id}
            title={item.name}
            hint={[item.pattern_name, item.level ? c.levels[item.level as keyof typeof c.levels] : null]
              .filter(Boolean)
              .join(" · ")}
            trailing={item.fits_you ? <Tag tone="fit">{c.fitsYou}</Tag> : undefined}
            onClick={() => onOpen(item.id)}
          />
        ))}
      </div>
      {items && items.length < total && (
        <Button variant="secondary" onClick={() => load(items.length)}>
          {c.more}
        </Button>
      )}
    </>
  );
}
