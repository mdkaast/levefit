import { useCallback, useEffect, useState } from "react";
import {
  completeTask,
  createWorkout,
  getMe,
  getPlan,
  getTasks,
  type Character,
  type PlanItem,
  type Streak,
  type Task,
} from "../api";
import { Icon } from "../icons";
import { t } from "../i18n";
import { targetLine } from "../messages";

type Props = { character: Character; onOpenWorkout: (id: number) => void };

const STATS = ["strength", "endurance", "agility", "discipline"] as const;

export function Home({ character: initial, onOpenWorkout }: Props) {
  const [character, setCharacter] = useState(initial);
  const [paused, setPaused] = useState(false);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [plan, setPlan] = useState<PlanItem[]>([]);

  const load = useCallback(() => {
    getMe()
      .then((me) => {
        if (me.character) setCharacter(me.character);
        setStreak(me.streak);
        setPaused(me.user.mode === "paused");
      })
      .catch(() => undefined);
    getTasks()
      .then(setTasks)
      .catch(() => undefined);
    getPlan()
      .then((p) => setPlan(p.items))
      .catch(() => undefined);
  }, []);

  useEffect(load, [load]);

  async function start() {
    const workout = await createWorkout(t.workout.defaultTitle);
    onOpenWorkout(workout.id);
  }

  async function confirm(task: Task) {
    await completeTask(task.id).catch(() => undefined);
    load();
  }

  const percent = Math.min(100, Math.round((character.xp_in_level / character.xp_to_next) * 100));
  const statMax = Math.max(10, ...STATS.map((stat) => character[stat]));
  const goal = streak?.weekly_goal ?? 0;
  const rankName = t.ranks[character.rank as keyof typeof t.ranks] ?? character.rank;

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
            {rankName} · {t.home.level} {character.level}
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
          <span className="chip">
            {t.home.levelPoints}: {character.level_points}
          </span>
        </div>
      </header>

      {paused && (
        <section>
          <p>{t.home.paused}</p>
        </section>
      )}

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

      {plan.length > 0 && (
        <section>
          <h3>{t.home.planTitle}</h3>
          <ul className="list">
            {plan.map((item) => (
              <li key={item.exercise_id}>
                {item.name}: {targetLine(item)}
              </li>
            ))}
          </ul>
        </section>
      )}

      {(["daily", "weekly"] as const).map((period) => {
        const list = tasks.filter((task) => task.period === period);
        if (list.length === 0) return null;
        return (
          <section key={period}>
            <h3>{period === "daily" ? t.home.tasksDaily : t.home.tasksWeekly}</h3>
            <ul className="list">
              {list.map((task) => (
                <li key={task.id} className={`task-item${task.status === "completed" ? " done" : ""}`}>
                  <div className="row">
                    <span>{t.tasks[task.code as keyof typeof t.tasks] ?? task.code}</span>
                    <span className="xp">
                      +{task.xp_reward} {t.home.xp}
                    </span>
                  </div>
                  <small>{t.taskKinds[task.kind]}</small>
                  {task.kind !== "recovery" && (
                    <div className="bar thin">
                      <i style={{ width: `${Math.round((task.progress / task.target) * 100)}%` }} />
                    </div>
                  )}
                  {task.status === "completed" ? (
                    <small>{t.home.taskDone}</small>
                  ) : task.kind === "recovery" ? (
                    <button type="button" className="ghost" onClick={() => confirm(task)}>
                      {t.home.taskConfirm}
                    </button>
                  ) : (
                    <small>
                      {task.progress}/{task.target}
                    </small>
                  )}
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
