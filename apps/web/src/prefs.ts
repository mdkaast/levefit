/** Локальные настройки устройства: «меньше движения» и тактильный отклик. Хранятся только в браузере. */
const KEY = "levefit.prefs";

export type Prefs = { reducedMotion: boolean; haptics: boolean };

const DEFAULTS: Prefs = { reducedMotion: false, haptics: true };

export function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? { ...DEFAULTS, ...(JSON.parse(raw) as Partial<Prefs>) } : DEFAULTS;
  } catch {
    return DEFAULTS;
  }
}

export function savePrefs(prefs: Prefs): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(prefs));
  } catch {
    // хранилище недоступно: настройка действует до перезапуска
  }
  applyPrefs(prefs);
}

/** Выставляет атрибут, по которому CSS гасит анимации. */
export function applyPrefs(prefs: Prefs = loadPrefs()): void {
  document.documentElement.dataset.motion = prefs.reducedMotion ? "reduced" : "full";
}

export function prefersReducedMotion(): boolean {
  const system =
    typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  return Boolean(system) || loadPrefs().reducedMotion;
}

/** Лёгкий тактильный отклик Telegram; отключается в настройках. */
export function haptic(kind: "select" | "light" | "medium" | "success" | "warning" = "select"): void {
  if (!loadPrefs().haptics) return;
  try {
    const h = window.Telegram?.WebApp?.HapticFeedback;
    if (!h) return;
    if (kind === "select") h.selectionChanged();
    else if (kind === "success" || kind === "warning") h.notificationOccurred?.(kind);
    else h.impactOccurred?.(kind);
  } catch {
    // вне Telegram вибрации нет
  }
}
