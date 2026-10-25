import { t } from "./i18n";

export const NAME_MAX_LEN = 30;

/** Возвращает текст ошибки или null, если имя подходит. Сервер проверяет то же самое. */
export function validateName(raw: string): string | null {
  const name = raw.trim();
  if (!name) return t.create.nameRequired;
  if (name.length > NAME_MAX_LEN) return t.create.nameTooLong;
  return null;
}

const toNumber = (raw: string): number | null => {
  const value = Number(raw.trim().replace(",", "."));
  return raw.trim() !== "" && Number.isFinite(value) ? value : null;
};

/** Диапазоны совпадают с серверными (game_rules/config.py). */
export function parseAge(raw: string): number | null {
  const value = toNumber(raw);
  return value !== null && Number.isInteger(value) && value >= 12 && value <= 100 ? value : null;
}

export function parseHeight(raw: string): number | null {
  const value = toNumber(raw);
  return value !== null && Number.isInteger(value) && value >= 120 && value <= 230 ? value : null;
}

export function parseWeight(raw: string): number | null {
  const value = toNumber(raw);
  return value !== null && value >= 20 && value <= 500 ? value : null;
}
