import { useEffect, useState } from "react";
import {
  createWorkout,
  getMe,
  getPlan,
  login,
  patchMe,
  type Character,
  type Plan,
  type Reward,
} from "./api";
import { clearSession, saveSession, type Session } from "./cycle/session";
import { Icon, type IconName } from "./icons";
import { t } from "./i18n";
import { ActiveWorkout } from "./screens/ActiveWorkout";
import { Athlete } from "./screens/Athlete";
import { Home } from "./screens/Home";
import { Missed } from "./screens/Missed";
import { Nutrition } from "./screens/Nutrition";
import { Onboarding } from "./screens/Onboarding";
import { Progress } from "./screens/Progress";
import { Ready } from "./screens/Ready";
import { Summary } from "./screens/Summary";
import { WorkoutScreen } from "./screens/WorkoutScreen";
import { Workouts } from "./screens/Workouts";
import { getInitData } from "./telegram";

/** Пять вкладок из макетов: Сегодня, Тренировки, Питание, Прогресс, Атлет. */
const TABS = ["today", "workouts", "nutrition", "progress", "athlete"] as const;
type Tab = (typeof TABS)[number];

const NAV_ICONS: Record<Tab, IconName> = {
  today: "sun",
  workouts: "calendar",
  nutrition: "fork",
  progress: "chart",
  athlete: "athlete",
};

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "deleted" }
  | { kind: "create" }
  | { kind: "tabs"; character: Character; tab: Tab; admin: boolean }
  | { kind: "workout"; character: Character; workoutId: number; back: Tab; admin: boolean }
  | { kind: "ready"; character: Character; admin: boolean; plan: Plan }
  | { kind: "active"; character: Character; admin: boolean; session: Session }
  | { kind: "summary"; character: Character; admin: boolean; session: Session; reward: Reward }
  | { kind: "missed"; character: Character; admin: boolean };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    const initData = getInitData();
    if (!initData) {
      setState({ kind: "error", message: t.notInTelegram });
      return;
    }
    login(initData)
      .then(getMe)
      .then((me) => {
        if (!me.user.timezone) {
          // Часовой пояс нужен для напоминаний в заданное местное время.
          patchMe({ timezone: Intl.DateTimeFormat().resolvedOptions().timeZone }).catch(
            () => undefined,
          );
        }
        setState(
          me.character
            ? { kind: "tabs", character: me.character, tab: "today", admin: me.is_admin }
            : { kind: "create" },
        );
      })
      .catch(() => setState({ kind: "error", message: t.authFailed }));
  }, []);

  switch (state.kind) {
    case "loading":
      return <p className="status-screen">{t.loading}</p>;
    case "error":
      return <p className="status-screen">{state.message}</p>;
    case "deleted":
      return <p className="status-screen">{t.deleted}</p>;
    case "create":
      return (
        <Onboarding
          onCreated={(character) =>
            setState({ kind: "tabs", character, tab: "today", admin: false })
          }
        />
      );
    case "workout":
      return (
        <WorkoutScreen
          workoutId={state.workoutId}
          onClose={() =>
            setState({
              kind: "tabs",
              character: state.character,
              tab: state.back,
              admin: state.admin,
            })
          }
        />
      );
    case "ready": {
      const { character, admin, plan } = state;
      const home = () => setState({ kind: "tabs", character, tab: "today", admin });
      return (
        <Ready
          plan={plan}
          onBack={home}
          onStarted={(workoutId, items) => {
            const session: Session = {
              workoutId,
              title: t.workout.defaultTitle,
              startedAt: Date.now(),
              items,
            };
            saveSession(session);
            setState({ kind: "active", character, admin, session });
          }}
        />
      );
    }
    case "active": {
      const { character, admin, session } = state;
      return (
        <ActiveWorkout
          session={session}
          onExit={() => setState({ kind: "tabs", character, tab: "today", admin })}
          onFinished={(reward) => setState({ kind: "summary", character, admin, session, reward })}
        />
      );
    }
    case "summary": {
      const { character, admin, session, reward } = state;
      return (
        <Summary
          session={session}
          reward={reward}
          onDone={() => {
            clearSession();
            setState({ kind: "tabs", character, tab: "today", admin });
          }}
        />
      );
    }
    case "missed": {
      const { character, admin } = state;
      const home = () => setState({ kind: "tabs", character, tab: "today", admin });
      return <Missed onClose={home} onApplied={home} />;
    }
    case "tabs": {
      const { character, tab, admin } = state;
      const open = (workoutId: number) =>
        setState({ kind: "workout", character, workoutId, back: tab, admin });
      const startWith = (plan: Plan) => {
        if (plan.items.length > 0) {
          setState({ kind: "ready", character, admin, plan });
        } else {
          // плана нет (например, нет подходящих упражнений): свободная запись тренировки
          createWorkout(t.workout.defaultTitle)
            .then((workout) => open(workout.id))
            .catch(() => undefined);
        }
      };
      return (
        <>
          {tab === "today" && (
            <Home
              character={character}
              onSkip={() => setState({ kind: "missed", character, admin })}
              onResume={(session) => setState({ kind: "active", character, admin, session })}
              onStart={startWith}
              onOpenNutrition={() => setState({ kind: "tabs", character, tab: "nutrition", admin })}
            />
          )}
          {tab === "workouts" && (
            <Workouts
              onOpenWorkout={open}
              onStart={() => void getPlan().then(startWith).catch(() => undefined)}
            />
          )}
          {tab === "nutrition" && <Nutrition />}
          {tab === "progress" && <Progress />}
          {tab === "athlete" && (
            <Athlete isAdmin={admin} onDeleted={() => setState({ kind: "deleted" })} />
          )}
          <nav aria-label={t.nav.label}>
            {TABS.map((name) => (
              <button
                key={name}
                type="button"
                aria-current={tab === name ? "page" : undefined}
                onClick={() => setState({ kind: "tabs", character, tab: name, admin })}
              >
                <Icon name={NAV_ICONS[name]} />
                {t.nav[name]}
              </button>
            ))}
          </nav>
        </>
      );
    }
  }
}
