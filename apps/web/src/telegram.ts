import { retrieveRawInitData } from "@telegram-apps/sdk";

/** Сырая строка initData от Telegram; вне Telegram — null (в dev можно задать VITE_DEV_INIT_DATA). */
export function getInitData(): string | null {
  try {
    const raw = retrieveRawInitData();
    if (raw) return raw;
  } catch {
    // приложение открыто не из Telegram
  }
  return import.meta.env.DEV ? (import.meta.env.VITE_DEV_INIT_DATA ?? null) : null;
}
