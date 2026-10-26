import type { WeekPreview } from "../api";
import { t } from "../i18n";
import { Card, Tag } from "../ui/ui";

type Props = { preview: WeekPreview };

/** «До / после» для следующей недели: что добавится, исчезнет или изменится, и сдвиг объёма по группам. */
export function WeekChanges({ preview }: Props) {
  const d = t.directions;
  const sign = (value: number) => (value > 0 ? "+" : "");
  return (
    <Card>
      <h3>{d.changesTitle}</h3>
      {preview.changes.length === 0 && <p className="muted">{d.nothingChanges}</p>}
      <div className="stack">
        {preview.changes.map((change) => (
          <div key={`${change.weekday}-${change.kind}`} className="change-row">
            <div className="row">
              <b>
                {change.day} · {change.title}
              </b>
              <Tag tone={change.kind === "removed" ? "neutral" : "info"}>{d.changeKind[change.kind]}</Tag>
            </div>
            {change.details.map((line) => (
              <small key={line} className="muted">
                {line}
              </small>
            ))}
          </div>
        ))}
      </div>
      {preview.volume.length > 0 && (
        <>
          <h3>{d.volumeTitle}</h3>
          {preview.volume.slice(0, 4).map((row) => (
            <div key={row.group} className="row">
              <span>{row.name}</span>
              <b className="num">
                {String(row.before).replace(".", ",")} → {String(row.after).replace(".", ",")} (
                {sign(row.after - row.before)}
                {String(Math.round((row.after - row.before) * 10) / 10).replace(".", ",")})
              </b>
            </div>
          ))}
        </>
      )}
      {preview.after_warnings.length > 0 && (
        <ul className="plain-list">
          {preview.after_warnings.map((w) => (
            <li key={w}>
              <small className="muted">{warningText(w)}</small>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

export function warningText(code: string, names: Record<string, string> = {}): string {
  const w = t.directions.warnings;
  const [kind, arg = ""] = code.split(":");
  if (kind === "overload") return w.overload(Number(arg));
  if (kind === "conflicts") return w.conflicts;
  if (kind === "catalog_missing") return w.catalog_missing;
  if (kind === "accent_capped") return w.accent_capped(names[arg] ?? arg);
  if (kind === "accent_unavailable") return w.accent_unavailable(names[arg] ?? arg);
  return code;
}
