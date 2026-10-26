import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "@fontsource-variable/inter";
import "@fontsource-variable/inter-tight";
import "./styles.css";
import { applyPrefs } from "./prefs";

// Сообщаем Telegram, что интерфейс готов, и раскрываем Mini App на всю высоту.
type TelegramWebApp = {
  ready(): void;
  expand(): void;
  setHeaderColor?(color: string): void;
  setBackgroundColor?(color: string): void;
};
const telegram = (window as { Telegram?: { WebApp?: TelegramWebApp } }).Telegram;
telegram?.WebApp?.ready();
telegram?.WebApp?.expand();
telegram?.WebApp?.setHeaderColor?.("#0e0f11");
telegram?.WebApp?.setBackgroundColor?.("#0e0f11");
applyPrefs();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
