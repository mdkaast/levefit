import type { Plan } from "../api";
import type { Session } from "../cycle/session";
import { t } from "../i18n";
import { targetLine } from "../messages";
import { Button, Card, Chip, Hint } from "../ui/ui";

type Props = {
  plan: Plan | null;
  session: Session | null;
  onStart: () => void;
  onResume: () => void;
  onSkip: () => void;
  onUndoSkip: () => void;
};

/** Карточка «Тренировка сегодня»: состав, решение тренера после прошлой тренировки и кнопки. */
export function TodayCard({ plan, session, onStart, onResume, onSkip, onUndoSkip }: Props) {
  const c = t.cycle.today;
  const items = plan?.items ?? [];
  const sets = items.reduce((sum, i) => sum + i.sets, 0);

  if (session) {
    return (
      <Card accent>
        <p className="kicker">{c.workoutToday}</p>
        <h2>{session.title}</h2>
        <p className="muted">{c.inProgress}</p>
        <Button onClick={onResume}>{c.resume}</Button>
      </Card>
    );
  }

  if (plan?.skipped_today) {
    return (
      <Card>
        <p className="kicker">{c.workoutToday}</p>
        <p>{plan.skipped_today === "move" ? c.skippedMove : c.skippedRest}</p>
        <Button variant="secondary" onClick={onUndoSkip}>
          {c.undoSkip}
        </Button>
      </Card>
    );
  }

  return (
    <Card accent>
      <p className="kicker">{c.workoutToday}</p>
      {items.length > 0 && (
        <div className="chips">
          <Chip>{c.exercises(items.length)}</Chip>
          <Chip>{c.sets(sets)}</Chip>
        </div>
      )}

      {plan?.source === "starter" && items.length > 0 && (
        <Hint>
          <b>{c.firstTitle}.</b> {c.firstText}
        </Hint>
      )}

      {plan && plan.decisions.length > 0 && (
        <div className="decision-block">
          <small>{c.decisionTitle}</small>
          {plan.decisions.map((reason) => (
            <b key={reason}>{reason}</b>
          ))}
        </div>
      )}

      {plan?.notes.map((note) => (
        <p key={note} className="muted">
          {note}
        </p>
      ))}

      {items.length > 0 ? (
        <ul className="plain-list">
          {items.map((item) => (
            <li key={item.exercise_id}>
              <span>{item.name}</span>
              <span className="num">{targetLine(item)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">{c.noPlan}</p>
      )}

      <Button onClick={onStart}>{c.start}</Button>
      <Button variant="text" onClick={onSkip}>
        {c.skip}
      </Button>
    </Card>
  );
}
