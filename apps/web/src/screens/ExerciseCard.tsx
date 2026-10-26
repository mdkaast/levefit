import { useEffect, useState } from "react";
import {
  getExerciseCard,
  getExerciseProgress,
  type ExerciseCardData,
  type ExerciseProgress,
} from "../api";
import { t } from "../i18n";
import { Button, Card, Chip, EmptyState, Hint, ListRow, Skeleton, Tag } from "../ui/ui";

type Props = { id: number; onBack: () => void; onOpen: (id: number) => void };

/** Карточка упражнения: мышцы, инвентарь, на что обратить внимание, замены и ваша история. */
export function ExerciseCard({ id, onBack, onOpen }: Props) {
  const c = t.catalog;
  const [card, setCard] = useState<ExerciseCardData | null>(null);
  const [progress, setProgress] = useState<ExerciseProgress | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setCard(null);
    setFailed(false);
    getExerciseCard(id)
      .then(setCard)
      .catch(() => setFailed(true));
    getExerciseProgress()
      .then((list) => setProgress(list.find((p) => p.exercise_id === id) ?? null))
      .catch(() => setProgress(null));
  }, [id]);

  const back = (
    <Button variant="text" onClick={onBack}>
      ‹ {c.back}
    </Button>
  );

  if (failed) {
    return (
      <>
        {back}
        <EmptyState title={c.loadError} text="" />
      </>
    );
  }
  if (!card) {
    return (
      <>
        {back}
        <Skeleton height={32} width="70%" />
        <Skeleton height={120} />
      </>
    );
  }

  const primary = card.muscles.filter((m) => m.role === "primary");
  const secondary = card.muscles.filter((m) => m.role !== "primary");
  const last = progress?.points[progress.points.length - 1];

  return (
    <>
      {back}
      <p className="kicker">{card.pattern_name}</p>
      <h1>{card.name}</h1>
      {card.name_en && <p className="muted">{card.name_en}</p>}
      <div className="chips">
        {card.level && <Chip>{c.levels[card.level as keyof typeof c.levels]}</Chip>}
        {card.fits_you && <Chip fit>{c.fitsYou}</Chip>}
        {!card.verified && <Chip>{c.unverified}</Chip>}
      </div>

      <Card>
        <h3>{c.muscles}</h3>
        {primary.length > 0 && (
          <>
            <small className="muted">{c.primary}</small>
            <div className="chips">
              {primary.map((m) => (
                <Chip key={m.slug} selected>
                  {m.name}
                </Chip>
              ))}
            </div>
          </>
        )}
        {secondary.length > 0 && (
          <>
            <small className="muted">{c.secondary}</small>
            <div className="chips">
              {secondary.map((m) => (
                <Chip key={m.slug}>{m.name}</Chip>
              ))}
            </div>
          </>
        )}
      </Card>

      <Card>
        <h3>{c.equipment}</h3>
        <p>{card.equipment_names.map((alt) => alt.join(" + ")).join(` ${c.equipmentOr} `)}</p>
        {card.load_increment_kg && <small className="muted">{c.step(card.load_increment_kg)}</small>}
      </Card>

      {card.flags.length > 0 && (
        <Card>
          <h3>{c.cautions}</h3>
          <ul className="plain-list">
            {card.flags.map((flag) => (
              <li key={flag}>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
          <Hint>{c.cautionHint}</Hint>
        </Card>
      )}

      <Card>
        <h3>{c.myProgress}</h3>
        {last ? (
          <>
            <p>
              {c.estimate}: <b className="num">{String(last.score).replace(".", ",")}</b>
              {last.top_weight_kg ? ` · ${String(last.top_weight_kg).replace(".", ",")} кг` : ""}
            </p>
            {progress?.plateau && <Tag tone="info">{c.plateau}</Tag>}
          </>
        ) : (
          <p className="muted">{c.noHistory}</p>
        )}
      </Card>

      <Card>
        <h3>{c.technique}</h3>
        <p className="muted">{c.techniqueEmpty}</p>
      </Card>

      {card.substitutes.length > 0 && (
        <>
          <h3>{c.substitutes}</h3>
          <div className="stack">
            {card.substitutes.map((s) => (
              <ListRow
                key={s.id}
                title={s.name}
                hint={c.substituteReason[s.reason as keyof typeof c.substituteReason]}
                onClick={() => onOpen(s.id)}
              />
            ))}
          </div>
        </>
      )}
    </>
  );
}
