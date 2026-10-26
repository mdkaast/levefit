import { useEffect, useState } from "react";
import { listPrograms, type ProgramCardData } from "../api";
import { plural } from "../format";
import { t } from "../i18n";
import { Button, Chip, EmptyState, Skeleton, Tag } from "../ui/ui";

type Props = { onOpen: (id: string) => void };

type Filter = "fit" | "all" | "strength" | "strength_mass" | "mass" | "return" | "weight_loss" | "general";
const FILTERS: Filter[] = ["fit", "strength", "strength_mass", "mass", "return", "weight_loss", "general", "all"];

function days(card: ProgramCardData): string {
  return card.days_min === card.days_max ? `${card.days_min}` : `${card.days_min}–${card.days_max}`;
}

function minutes(card: ProgramCardData): string {
  const [low, high] = card.session;
  return low === high ? `${low}` : `${low}–${high}`;
}

/** Программы: «Для вас» сверху, остальные по целям; 22 шаблона. */
export function Programs({ onOpen }: Props) {
  const c = t.catalog;
  const [items, setItems] = useState<ProgramCardData[] | null>(null);
  const [filter, setFilter] = useState<Filter>("fit");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    listPrograms()
      .then(setItems)
      .catch(() => setFailed(true));
  }, []);

  if (failed) return <EmptyState title={c.loadError} text="" />;
  if (!items) {
    return (
      <div className="stack">
        <Skeleton height={96} />
        <Skeleton height={96} />
      </div>
    );
  }

  const label = (f: Filter) => (f === "fit" ? c.goalChips.fit : f === "all" ? c.goalChips.all : t.goals[f]);
  const shown = items.filter((p) =>
    filter === "fit" ? p.fits_you : filter === "all" ? true : p.goals.includes(filter),
  );
  const noun = plural(items.length, ...(c.programsCount.split("|") as [string, string, string]));

  return (
    <>
      <p className="kicker">
        {c.library} · {items.length} {noun}
      </p>
      <div className="chip-row">
        {FILTERS.map((f) => (
          <Chip key={f} selected={filter === f} onClick={() => setFilter(f)}>
            {label(f)}
          </Chip>
        ))}
      </div>
      <div className="stack">
        {shown.map((p) => (
          <button key={p.id} type="button" className="program-card" onClick={() => onOpen(p.id)}>
            <span className="row">
              <b>{p.name}</b>
              <small className="muted">{p.id}</small>
            </span>
            <small className="muted">
              {days(p)} {plural(p.days_max, "день", "дня", "дней")} · {p.inventory.map((i) => c.inventories[i as keyof typeof c.inventories] ?? i).join(", ")} · {minutes(p)} {c.program.minutes}
            </small>
            <span className="chips">
              {p.fits_you && <Tag tone="fit">{c.fitsYou}</Tag>}
              {!p.engine_ready && p.fallback && <Tag tone="info">→ {p.fallback}</Tag>}
              {p.on_request_only && <Tag>{c.program.onRequest}</Tag>}
              <Tag>{p.levels.map((l) => c.levels[l as keyof typeof c.levels]).join(" – ")}</Tag>
            </span>
          </button>
        ))}
        {shown.length === 0 && <EmptyState title={c.empty} text="" />}
      </div>
      {filter !== "all" && (
        <Button variant="secondary" onClick={() => setFilter("all")}>
          {c.program.showAll(items.length)}
        </Button>
      )}
    </>
  );
}
