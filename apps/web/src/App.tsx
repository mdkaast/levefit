import { useEffect, useState } from "react";
import { getMe, login, type Character } from "./api";
import { t } from "./i18n";
import { CreateCharacter } from "./screens/CreateCharacter";
import { getInitData } from "./telegram";

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "create" }
  | { kind: "home"; character: Character };

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
        <main style={{ padding: 16 }}>
          <h1>{state.character.name}</h1>
          <p>
            {t.home.level} {state.character.level}
          </p>
          <p>{t.homeStub}</p>
        </main>
      );
  }
}
