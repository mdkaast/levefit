import type { Reward } from "../api";
import { Icon } from "../icons";
import { t } from "../i18n";
import { achievementMessages, levelUpMessage, rankMessage, workoutDoneMessage } from "../messages";

export function RewardSummary({ reward }: { reward: Reward }) {
  const notices = [levelUpMessage(reward), rankMessage(reward), ...achievementMessages(reward)];
  const parts = [
    [t.reward.breakdown.workout, reward.workout_xp],
    [t.reward.breakdown.sets, reward.sets_xp],
    [t.reward.breakdown.tasks, reward.task_xp],
    [t.reward.breakdown.week, reward.week_xp],
  ] as const;

  return (
    <section className="reward">
      <h3>{t.reward.title}</h3>
      <p>
        <strong>{workoutDoneMessage(reward)}</strong>
      </p>
      {reward.counted && (
        <div className="chips">
          {parts
            .filter(([, xp]) => xp > 0)
            .map(([label, xp]) => (
              <span className="chip" key={label}>
                {label}: +{xp}
              </span>
            ))}
          <span className="chip pink">
            <Icon name="flame" />
            {reward.streak_weeks} {t.home.weeksShort}
          </span>
        </div>
      )}
      {notices
        .filter((line): line is string => line !== null)
        .map((line) => (
          <p className="levelup" key={line}>
            {line}
          </p>
        ))}
    </section>
  );
}
