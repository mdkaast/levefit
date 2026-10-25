import { t } from "./i18n";

export function App() {
  return (
    <main style={{ padding: 16 }}>
      <h1>{t.appTitle}</h1>
      <p>{t.stub}</p>
    </main>
  );
}
