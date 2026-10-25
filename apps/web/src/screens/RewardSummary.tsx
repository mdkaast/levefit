import type { Reward } from "../api";
import { t } from "../i18n";

export function RewardSummary({ reward }: { reward: Reward }) {
  if (!reward.counted) return <p>{t.reward.notCounted}</p>;
  return (
    <section>
      <h2>{t.reward.title}</h2>
      <p>
        {t.reward.total}: +{reward.xp_gained}
      </p>
      <ul style={{ paddingLeft: 16 }}>
        <li>
          {t.reward.workout}: +{reward.workout_xp}
        </li>
        <li>
          {t.reward.sets}: +{reward.sets_xp}
        </li>
        {reward.quest_xp > 0 && (
          <li>
            {t.reward.quests}: +{reward.quest_xp}
          </li>
        )}
        {reward.week_xp > 0 && (
          <li>
            {t.reward.week}: +{reward.week_xp}
          </li>
        )}
      </ul>
      {reward.leveled_up && (
        <p>
          {t.reward.levelUp}: {reward.level_after}
        </p>
      )}
      <p>
        {t.reward.streak}: {reward.streak_weeks}
      </p>
    </section>
  );
}
