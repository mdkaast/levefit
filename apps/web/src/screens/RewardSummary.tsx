import type { Reward } from "../api";
import { Icon } from "../icons";
import { t } from "../i18n";

export function RewardSummary({ reward }: { reward: Reward }) {
  if (!reward.counted) return <p className="muted">{t.reward.notCounted}</p>;
  return (
    <section className="reward">
      <h3>{t.reward.title}</h3>
      <p className="big">+{reward.xp_gained} XP</p>
      <div className="chips">
        <span className="chip">
          {t.reward.workout}: +{reward.workout_xp}
        </span>
        <span className="chip">
          {t.reward.sets}: +{reward.sets_xp}
        </span>
        {reward.quest_xp > 0 && (
          <span className="chip lime">
            {t.reward.quests}: +{reward.quest_xp}
          </span>
        )}
        {reward.week_xp > 0 && (
          <span className="chip lime">
            {t.reward.week}: +{reward.week_xp}
          </span>
        )}
        <span className="chip pink">
          <Icon name="flame" />
          {reward.streak_weeks} {t.home.weeksShort}
        </span>
      </div>
      {reward.leveled_up && (
        <p className="levelup">
          {t.reward.levelUp}: {reward.level_after}
        </p>
      )}
    </section>
  );
}
