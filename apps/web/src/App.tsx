import { useEffect, useState } from "react";
import { getMe, login, type Character } from "./api";
import { t } from "./i18n";
import { CreateCharacter } from "./screens/CreateCharacter";
import { Home } from "./screens/Home";
import { WorkoutScreen } from "./screens/WorkoutScreen";
import { getInitData } from "./telegram";

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "create" }
  | { kind: "home"; character: Character }
  | { kind: "workout"; character: Character; workoutId: number };

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
        setState(me.character ? { kind: "home", character: me.character } : { kind: "create" }),
      )
      .catch(() => setState({ kind: "error", message: t.authFailed }));
  }, []);

  switch (state.kind) {
    case "loading":
      return <p style={{ padding: 16 }}>{t.loading}</p>;
    case "error":
      return <p style={{ padding: 16 }}>{state.message}</p>;
    case "create":
      return <CreateCharacter onCreated={(character) => setState({ kind: "home", character })} />;
    case "home":
      return (
        <Home
          character={state.character}
          onOpenWorkout={(workoutId) =>
            setState({ kind: "workout", character: state.character, workoutId })
          }
        />
      );
    case "workout":
      return (
        <WorkoutScreen
          workoutId={state.workoutId}
          onClose={() => setState({ kind: "home", character: state.character })}
        />
      );
  }
}
