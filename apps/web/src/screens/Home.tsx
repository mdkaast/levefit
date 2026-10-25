import { useEffect, useState } from "react";
import {
  createWorkout,
  getMe,
  getQuests,
  type Character,
  type Quest,
  type Streak,
} from "../api";
import { Icon } from "../icons";
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
  const statMax = Math.max(10, ...STATS.map((stat) => character[stat]));
  const goal = streak?.weekly_goal ?? 0;

  return (
    <main>
      <p className="brand">{t.appTitle}</p>
      <header className="card hero">
        <div className="avatar" aria-hidden="true">
          {character.name.trim().charAt(0).toUpperCase()}
          <i className="lvl">{character.level}</i>
        </div>
        <div>
          <h1>{character.name}</h1>
          <p className="muted">
            {t.home.level} {character.level}
          </p>
        </div>
        <div className="chips">
          <span className="chip pink">
            <Icon name="flame" />
            {streak?.weeks ?? 0} {t.home.weeksShort}
          </span>
          <span className="chip lime">
            <Icon name="bolt" />
            {character.xp} {t.home.xp}
          </span>
        </div>
      </header>

      <section>
        <div className="row">
          <h2>
            {t.home.level} {character.level}
          </h2>
          <span className="muted">
            {character.xp_in_level} / {character.xp_to_next} {t.home.xp}
          </span>
        </div>
        <div
          className="bar"
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <i style={{ width: `${percent}%` }} />
        </div>
      </section>

      <section className="stats">
        {STATS.map((stat) => (
          <div className="stat" key={stat}>
            <div className="tube">
              <i style={{ height: `${Math.max(6, (character[stat] / statMax) * 100)}%` }} />
            </div>
            <b>{character[stat]}</b>
            <span>{t.home.stats[stat]}</span>
          </div>
        ))}
      </section>

      {streak && goal > 0 && (
        <section>
          <div className="row">
            <h2>{t.home.weekProgress}</h2>
            <span className="muted">
              {streak.week_workouts}/{goal}
            </span>
          </div>
          <div className="dots">
            {Array.from({ length: goal }, (_, i) => (
              <i key={i} className={i < streak.week_workouts ? "on" : ""} />
            ))}
          </div>
          <small>
            {t.home.freezes}: {streak.freezes_left}
          </small>
        </section>
      )}

      {(["daily", "weekly"] as const).map((kind) => {
        const list = quests.filter((q) => q.kind === kind);
        if (list.length === 0) return null;
        return (
          <section key={kind}>
            <h3>{kind === "daily" ? t.home.questsDaily : t.home.questsWeekly}</h3>
            <ul className="list">
              {list.map((q) => (
                <li key={q.id} className={`quest${q.status === "completed" ? " done" : ""}`}>
                  <div className="row">
                    <span>{t.quests[q.code as keyof typeof t.quests] ?? q.code}</span>
                    <span className="xp">
                      +{q.xp_reward} {t.home.xp}
                    </span>
                  </div>
                  <div className="bar thin">
                    <i style={{ width: `${Math.round((q.progress / q.target) * 100)}%` }} />
                  </div>
                  <small>
                    {q.status === "completed" ? t.home.questDone : `${q.progress}/${q.target}`}
                  </small>
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
