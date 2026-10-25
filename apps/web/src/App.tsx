import { useEffect, useState } from "react";
import { getMe, login, type Character } from "./api";
import { t } from "./i18n";
import { CreateCharacter } from "./screens/CreateCharacter";
import { Home } from "./screens/Home";
import { Progress } from "./screens/Progress";
import { WorkoutScreen } from "./screens/WorkoutScreen";
import { getInitData } from "./telegram";

type Tab = "home" | "progress";

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
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
      .then((me) =>
        setState(
          me.character
            ? { kind: "tabs", character: me.character, tab: "home" }
            : { kind: "create" },
        ),
      )
      .catch(() => setState({ kind: "error", message: t.authFailed }));
  }, []);

  switch (state.kind) {
    case "loading":
      return <p style={{ padding: 16 }}>{t.loading}</p>;
    case "error":
      return <p style={{ padding: 16 }}>{state.message}</p>;
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
          {tab === "home" ? (
            <Home character={character} onOpenWorkout={open} />
          ) : (
            <Progress onOpenWorkout={open} />
          )}
          <nav style={{ display: "flex", gap: 8, padding: 16 }}>
            {(["home", "progress"] as const).map((name) => (
              <button
                key={name}
                type="button"
                aria-current={tab === name ? "page" : undefined}
                onClick={() => setState({ kind: "tabs", character, tab: name })}
                style={{ flex: 1, fontWeight: tab === name ? "bold" : "normal" }}
              >
                {t.nav[name]}
              </button>
            ))}
          </nav>
        </>
      );
    }
  }
}
