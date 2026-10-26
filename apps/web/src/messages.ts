import type { PlanItem, Reward } from "./api";
import { t } from "./i18n";

const STAT_ORDER = ["strength", "endurance", "agility", "discipline"] as const;

/** «одно очко», «2 очка», «5 очков». */
export function pointsPhrase(count: number): string {
  if (count === 1) return "одно очко";
  const lastTwo = count % 100;
  const last = count % 10;
  if (lastTwo >= 11 && lastTwo <= 14) return `${count} очков`;
  if (last >= 2 && last <= 4) return `${count} очка`;
  return `${count} очков`;
}

/** «Задание выполнено. Начислено 140 XP. Сила +2, Дисциплина +1.» */
export function workoutDoneMessage(reward: Reward): string {
  if (!reward.counted) return t.reward.limitReached;
  const gains = STAT_ORDER.filter((stat) => (reward.stat_gains[stat] ?? 0) > 0)
    .map((stat) => `${t.reward.stats[stat]} +${reward.stat_gains[stat]}`)
    .join(", ");
  const base = `Задание выполнено. Начислено ${reward.xp_gained} XP.`;
  return gains ? `${base} ${gains}.` : base;
}

/** «Достигнут уровень 12. Доступно одно очко улучшения.» */
export function levelUpMessage(reward: Reward): string | null {
  if (!reward.leveled_up) return null;
  const base = `Достигнут уровень ${reward.level_after}.`;
  if (reward.level_points_gained <= 0) return base;
  const points = pointsPhrase(reward.level_points_gained);
  const noun = reward.level_points_gained === 1 ? "улучшения" : "улучшений";
  return `${base} Доступно ${points} ${noun}.`;
}

export function rankMessage(reward: Reward): string | null {
  if (!reward.rank_changed) return null;
  const name = t.ranks[reward.rank_after as keyof typeof t.ranks] ?? reward.rank_after;
  return `Новый ранг: ${name}.`;
}

export function achievementMessages(reward: Reward): string[] {
  return reward.achievements_earned.map((code) => {
    const known = t.achievements[code as keyof typeof t.achievements];
    return `Новое достижение: ${known ? known.title : code}.`;
  });
}

/** «80 кг × 3 × 8» или, если цели по подходам разные, «80 кг × 8/8/7». */
export function targetLine(
  item: Pick<PlanItem, "target_weight_kg" | "sets" | "reps" | "rep_targets">,
): string {
  const weight =
    item.target_weight_kg !== null
      ? `${String(item.target_weight_kg).replace(".", ",")} ${t.units.kg}`
      : t.adjust.freeWeight;
  const targets = item.rep_targets;
  if (targets && targets.length > 1 && new Set(targets).size > 1) {
    return `${weight} × ${targets.join("/")}`;
  }
  return `${weight} × ${item.sets} × ${targets?.[0] ?? item.reps}`;
}
