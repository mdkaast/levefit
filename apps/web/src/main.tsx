import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

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
telegram?.WebApp?.setHeaderColor?.("#0a0c07");
telegram?.WebApp?.setBackgroundColor?.("#0a0c07");

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
