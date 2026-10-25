import { useEffect, useState } from "react";
import {
  createWorkout,
  getMe,
  getQuests,
  type Character,
  type Quest,
  type Streak,
} from "../api";
import { t } from "../i18n";

type Props = { character: Character; onOpenWorkout: (id: number) => void };

const STATS = ["strength", "endurance", "agility", "discipline"] as const;

export function Home({ character: initial, onOpenWorkout }: Props) {
  const [character, setCharacter] = useState(initial);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [quests, setQuests] = useState<Quest[]>([]);

  useEffect(() => {
    getMe()
      .then((me) => {
        if (me.character) setCharacter(me.character);
        setStreak(me.streak);
      })
      .catch(() => undefined);
    getQuests()
      .then(setQuests)
      .catch(() => undefined);
  }, []);

  async function start() {
    const workout = await createWorkout(t.workout.defaultTitle);
    onOpenWorkout(workout.id);
  }

  const percent = Math.min(100, Math.round((character.xp_in_level / character.xp_to_next) * 100));

  return (
    <main style={{ padding: 16, display: "grid", gap: 12 }}>
      <h1>{character.name}</h1>
      <section>
        <p>
          {t.home.level} {character.level} · {character.xp_in_level}/{character.xp_to_next}{" "}
          {t.home.xp}
        </p>
        <div style={{ background: "#ddd", height: 10, borderRadius: 5 }}>
          <div
            style={{ width: `${percent}%`, height: "100%", background: "#4a8", borderRadius: 5 }}
          />
        </div>
      </section>

      <ul style={{ paddingLeft: 0, listStyle: "none", display: "grid", gap: 4 }}>
        {STATS.map((stat) => (
          <li key={stat}>
            {t.home.stats[stat]}: {character[stat]}
          </li>
        ))}
      </ul>

      {streak && (
        <section>
          <p>
            {t.home.streak}: {streak.weeks} · {t.home.freezes}: {streak.freezes_left}
          </p>
          <p>
            {t.home.weekProgress}: {streak.week_workouts}/{streak.weekly_goal}
          </p>
        </section>
      )}

      {(["daily", "weekly"] as const).map((kind) => {
        const list = quests.filter((q) => q.kind === kind);
        if (list.length === 0) return null;
        return (
          <section key={kind}>
            <h2>{kind === "daily" ? t.home.questsDaily : t.home.questsWeekly}</h2>
            <ul style={{ paddingLeft: 0, listStyle: "none", display: "grid", gap: 4 }}>
              {list.map((q) => (
                <li key={q.id}>
                  {t.quests[q.code as keyof typeof t.quests] ?? q.code}: {q.progress}/{q.target} · +
                  {q.xp_reward} {t.home.xp}
                  {q.status === "completed" && ` · ${t.home.questDone}`}
                </li>
              ))}
            </ul>
          </section>
        );
      })}

      <button type="button" onClick={start}>
        {t.home.startWorkout}
      </button>
    </main>
  );
}
