import { t } from "./i18n";

export const NAME_MAX_LEN = 30;

/** Возвращает текст ошибки или null, если имя подходит. Сервер проверяет то же самое. */
export function validateName(raw: string): string | null {
  const name = raw.trim();
  if (!name) return t.create.nameRequired;
  if (name.length > NAME_MAX_LEN) return t.create.nameTooLong;
  return null;
}
