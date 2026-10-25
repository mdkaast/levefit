import { useEffect, useState } from "react";
import { getMe, login, patchMe, type Character } from "./api";
import { Icon, type IconName } from "./icons";
import { t } from "./i18n";
import { CreateCharacter } from "./screens/CreateCharacter";
import { Home } from "./screens/Home";
import { Profile } from "./screens/Profile";
import { Progress } from "./screens/Progress";
import { WorkoutScreen } from "./screens/WorkoutScreen";
import { getInitData } from "./telegram";

type Tab = "home" | "progress" | "profile";

const NAV_ICONS: Record<Tab, IconName> = { home: "home", progress: "chart", profile: "user" };

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "deleted" }
  | { kind: "create" }
  | { kind: "tabs"; character: Character; tab: Tab }
  | { kind: "workout"; character: Character; workoutId: number; back: Tab };

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
            ? { kind: "tabs", character: me.character, tab: "home" }
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
        <CreateCharacter
          onCreated={(character) => setState({ kind: "tabs", character, tab: "home" })}
        />
      );
    case "workout":
      return (
        <WorkoutScreen
          workoutId={state.workoutId}
          onClose={() => setState({ kind: "tabs", character: state.character, tab: state.back })}
        />
      );
    case "tabs": {
      const { character, tab } = state;
      const open = (workoutId: number) =>
        setState({ kind: "workout", character, workoutId, back: tab });
      return (
        <>
          {tab === "home" && <Home character={character} onOpenWorkout={open} />}
          {tab === "progress" && <Progress onOpenWorkout={open} />}
          {tab === "profile" && <Profile onDeleted={() => setState({ kind: "deleted" })} />}
          <nav>
            {(["home", "progress", "profile"] as const).map((name) => (
              <button
                key={name}
                type="button"
                aria-current={tab === name ? "page" : undefined}
                onClick={() => setState({ kind: "tabs", character, tab: name })}
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
