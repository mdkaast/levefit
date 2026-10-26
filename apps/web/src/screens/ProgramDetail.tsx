import { useEffect, useState } from "react";
import { getProgram, type ProgramDetailData } from "../api";
import { t } from "../i18n";
import { Button, Card, EmptyState, Hint, ListRow, Segmented, Skeleton } from "../ui/ui";

type Props = { id: string; onBack: () => void; onOpenExercise: (id: number) => void };

const range = (v: number[]) => (v[0] === v[1] ? `${v[0]}` : `${v[0]}–${v[1]}`);

/** Программа: описание, объём по группам мышц, дни с подобранными под вас упражнениями. */
export function ProgramDetail({ id, onBack, onOpenExercise }: Props) {
  const c = t.catalog;
  const [data, setData] = useState<ProgramDetailData | null>(null);
  const [failed, setFailed] = useState(false);
  const [day, setDay] = useState(0);

  useEffect(() => {
    setData(null);
    setFailed(false);
    setDay(0);
    getProgram(id)
      .then(setData)
      .catch(() => setFailed(true));
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
  if (!data) {
    return (
      <>
        {back}
        <Skeleton height={32} width="70%" />
        <Skeleton height={160} />
      </>
    );
  }

  const max = Math.max(1, ...data.volume.map((v) => v.sets));
  const current = data.days[Math.min(day, data.days.length - 1)];
  const tabs = data.days.map((d, i) => ({ id: String(i), label: d.name }));
  const [low, high] = data.session;

  return (
    <>
      {back}
      <p className="kicker">
        {data.id} · {data.goals.map((g) => t.goals[g as keyof typeof t.goals]).join(" / ")}
      </p>
      <h1>{data.name}</h1>
      <p className="muted">{data.summary}</p>

      <div className="tiles">
        <div className="card">
          <small>{c.program.days}</small>
          <strong>{data.days_min === data.days_max ? data.days_min : `${data.days_min}–${data.days_max}`}</strong>
        </div>
        <div className="card">
          <small>{c.program.time}</small>
          <strong>
            {low === high ? low : `${low}–${high}`} {c.program.minutes}
          </strong>
        </div>
        <div className="card">
          <small>{c.program.level}</small>
          <strong>{data.levels.map((l) => c.levels[l as keyof typeof c.levels]).join(" – ")}</strong>
        </div>
        <div className="card">
          <small>{c.program.where}</small>
          <strong>{data.inventory.map((i) => c.inventories[i as keyof typeof c.inventories] ?? i).join(", ")}</strong>
        </div>
      </div>

      {data.warning && <Hint>{data.warning}</Hint>}
      {!data.engine_ready && data.fallback && <Hint>{c.program.engineLater(data.fallback)}</Hint>}
      {!data.verified && <Hint>{c.program.unverified}</Hint>}

      {data.volume.length > 0 && (
        <Card>
          <h3>{c.program.volume}</h3>
          {data.volume.slice(0, 10).map((v) => (
            <div key={v.group} className="vol-row">
              <span>{v.name}</span>
              <div className="ui-bar" aria-hidden="true">
                <i style={{ width: `${(v.sets / max) * 100}%` }} />
              </div>
              <b className="num">{String(v.sets).replace(".", ",")}</b>
            </div>
          ))}
          <small className="muted">{c.program.volumeHint}</small>
        </Card>
      )}

      {data.days.length > 1 && <Segmented items={tabs} value={String(day)} onChange={(v) => setDay(Number(v))} />}
      {current && (
        <div className="stack">
          {current.slots.map((slot, i) => (
            <ListRow
              key={`${slot.pattern}-${i}`}
              title={slot.exercise_name ?? c.program.empty}
              hint={[slot.pattern_name, slot.note].filter(Boolean).join(" · ")}
              trailing={
                <b className="num">
                  {range(slot.sets)} × {range(slot.reps)}
                </b>
              }
              onClick={slot.exercise_id ? () => onOpenExercise(slot.exercise_id as number) : undefined}
            />
          ))}
        </div>
      )}

      {data.phases && (
        <Card>
          {data.phases.map((p) => (
            <p key={p.weeks}>
              <b>{p.weeks}:</b> {p.scheme}
            </p>
          ))}
        </Card>
      )}
      <small className="muted">
        {c.program.principle}: {data.principle}
      </small>
      <Hint>{c.program.applyLater}</Hint>
    </>
  );
}
