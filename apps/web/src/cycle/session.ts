import type { PlanItem } from "../api";

/** Активная тренировка хранится на устройстве: приложение можно свернуть, закрыть и вернуться (K8). */
export type Session = {
  workoutId: number;
  title: string;
  startedAt: number;
  items: PlanItem[];
  /** Момент окончания отдыха (мс) и его длина: таймер идёт по часам, а не по тикам. */
  restEnd?: number;
  restTotal?: number;
};

const KEY = "levefit.session";

export function loadSession(): Session | null {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function saveSession(session: Session): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(session));
  } catch {
    // без хранилища тренировка работает, но не восстановится после перезапуска
  }
}

export function clearSession(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // нечего очищать
  }
}
