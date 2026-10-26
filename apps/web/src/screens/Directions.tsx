import { useCallback, useEffect, useState } from "react";
import {
  getDirections,
  previewWeek,
  putDirections,
  type DirectionsState,
  type WeekPreview,
} from "../api";
import { shortDate } from "../directions";
import { t } from "../i18n";
import { Button, Card, Chip, EmptyState, Hint, Skeleton, Stepper } from "../ui/ui";
import { Accent } from "./Accent";
import { WeekChanges } from "./WeekChanges";

type Item = { direction: string; days: number };
type Props = { onBack: () => void };

const same = (a: Item[], b: Item[]) =>
  a.length === b.length && a.every((item, i) => item.direction === b[i].direction && item.days === b[i].days);

/** Профиль → «Направления и акценты»: дни по направлениям, акцент, предпросмотр и сохранение. */
export function Directions({ onBack }: Props) {
  const d = t.directions;
  const [state, setState] = useState<DirectionsState | null>(null);
  const [draft, setDraft] = useState<Item[]>([]);
  const [preview, setPreview] = useState<WeekPreview | null>(null);
  const [accentFor, setAccentFor] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    setFailed(false);
    getDirections()
      .then((next) => {
        setState(next);
        setDraft(next.mine);
        setPreview(null);
      })
      .catch(() => setFailed(true));
  }, []);

  useEffect(load, [load]);

  if (failed) {
    return (
      <>
        <Button variant="text" onClick={onBack}>
          ‹ {d.back}
        </Button>
        <EmptyState
          title={d.loadError}
          text=""
          action={
            <Button variant="secondary" onClick={load}>
              {t.catalog.retry}
            </Button>
          }
        />
      </>
    );
  }
  if (!state) {
    return (
      <>
        <Skeleton height={32} width="70%" />
        <Skeleton height={120} />
      </>
    );
  }

  const info = (key: string) => state.catalog.find((c) => c.key === key);
  const accentInfo = accentFor ? info(accentFor) : undefined;
  if (accentInfo) {
    return (
      <Accent
        info={accentInfo}
        initial={state.accents[accentInfo.key]?.next ?? []}
        nextMonday={state.next_monday}
        onBack={() => setAccentFor(null)}
        onSaved={() => {
          setAccentFor(null);
          setMessage(d.saved(shortDate(state.next_monday)));
          load();
        }}
      />
    );
  }

  const total = draft.filter((item) => item.direction !== "universal").reduce((sum, item) => sum + item.days, 0);
  const changed = !same(draft, state.mine);
  const free = state.catalog.filter((c) => !draft.some((item) => item.direction === c.key));
  const draftSessions = draft.some((item) => info(item.direction)?.kind === "sessions");

  function update(next: Item[]) {
    setDraft(next);
    setPreview(null);
    setMessage(null);
  }

  async function showPreview() {
    try {
      setPreview(await previewWeek({ directions: draft }));
    } catch {
      setMessage(d.error);
    }
  }

  async function save() {
    if (!state) return;
    setSaving(true);
    try {
      const wasSaved = state.saved;
      const next = await putDirections(draft);
      setState(next);
      setDraft(next.mine);
      setPreview(null);
      setMessage(wasSaved ? d.saved(shortDate(next.next_monday)) : d.savedNow);
    } catch {
      setMessage(d.error);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Button variant="text" onClick={onBack}>
        ‹ {d.back}
      </Button>
      <h1>{d.title}</h1>
      <p className="muted">{d.profileHint}</p>

      <h3>{d.whatYouDo}</h3>
      <div className="stack">
        {draft.map((item) => {
          const direction = info(item.direction);
          const accent = state.accents[item.direction]?.next ?? [];
          const names = Object.fromEntries((direction?.options ?? []).map((o) => [o.key, o.name]));
          const pending = state.pending[item.direction];
          return (
            <Card key={item.direction}>
              <div className="row">
                <b>{direction?.name ?? item.direction}</b>
                {draft.length > 1 && (
                  <Button variant="text" onClick={() => update(draft.filter((x) => x.direction !== item.direction))}>
                    {d.remove}
                  </Button>
                )}
              </div>
              {item.direction !== "universal" && (
                <Stepper
                  value={item.days}
                  min={1}
                  max={state.max_days}
                  label={direction?.name ?? item.direction}
                  format={d.days}
                  onChange={(days) =>
                    update(draft.map((x) => (x.direction === item.direction ? { ...x, days } : x)))
                  }
                />
              )}
              {direction?.accent_kind && !changed && (
                <div className="row">
                  <small className="muted">
                    {accent.length ? d.accent(accent.map((k) => names[k] ?? k).join(", ")) : d.noAccent}
                  </small>
                  <Button variant="text" onClick={() => setAccentFor(item.direction)}>
                    {d.change}
                  </Button>
                </div>
              )}
              {pending && <small className="muted">{d.pending(shortDate(pending.from))}</small>}
              {direction && !direction.verified && direction.kind === "sessions" && (
                <small className="muted">{t.directions.week.draft}</small>
              )}
            </Card>
          );
        })}
      </div>

      {free.length > 0 && (
        <>
          <h3>{d.add}</h3>
          <div className="chip-row wrap">
            {free.map((c) => (
              <Chip
                key={c.key}
                onClick={() => update([...draft, { direction: c.key, days: Math.min(c.default_days, 2) }])}
              >
                + {c.name}
              </Chip>
            ))}
          </div>
        </>
      )}

      <p className={total > state.max_days ? "warn" : "muted"}>
        {d.total(total, state.max_days)}
        {total > state.max_days && ` · ${d.overload}`}
      </p>
      {draftSessions && <Hint>{d.unverified}</Hint>}

      {changed && preview && <WeekChanges preview={preview} />}
      {message && <p role="status">{message}</p>}
      {changed && (
        <div className="stack">
          <Button variant="secondary" onClick={showPreview}>
            {d.preview}
          </Button>
          <Button loading={saving} onClick={save}>
            {saving ? d.saving : d.save}
          </Button>
        </div>
      )}
      {!state.saved && !changed && (
        <Card accent>
          <p className="muted">{t.directions.week.goProgramHint}</p>
          <Button loading={saving} onClick={save}>
            {t.directions.week.goProgram}
          </Button>
        </Card>
      )}
    </>
  );
}
