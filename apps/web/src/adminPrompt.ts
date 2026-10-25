export const CHANGE_KINDS = [
  { id: "feature", label: "Новая функция" },
  { id: "bug", label: "Исправить ошибку" },
  { id: "text", label: "Изменить тексты" },
  { id: "design", label: "Изменить дизайн" },
  { id: "rules", label: "Правила игры" },
  { id: "ai", label: "Поведение ИИ-тренера" },
];

export const CHANGE_AREAS = [
  { id: "home", label: "Главная" },
  { id: "workout", label: "Экран тренировки" },
  { id: "progress", label: "Прогресс" },
  { id: "profile", label: "Профиль" },
  { id: "onboarding", label: "Онбординг" },
  { id: "bot", label: "Бот и напоминания" },
  { id: "admin", label: "Админ-панель" },
  { id: "other", label: "Другое" },
];

type Draft = { kind: string; area: string; title: string; details: string; result: string };

const label = (list: { id: string; label: string }[], id: string) =>
  list.find((x) => x.id === id)?.label ?? id;

/** Собирает текст запроса для Claude Code; ничего не отправляет. */
export function buildChangePrompt(d: Draft): string {
  const lines = [
    `Проект Levefit (репозиторий в текущей папке). Сначала прочитай docs/handoff.md и docs/decisions.md.`,
    ``,
    `Тип: ${label(CHANGE_KINDS, d.kind)}`,
    `Раздел: ${label(CHANGE_AREAS, d.area)}`,
    `Задача: ${d.title.trim()}`,
    ``,
    `Описание:`,
    d.details.trim(),
  ];
  if (d.result.trim()) lines.push(``, `Ожидаемый результат:`, d.result.trim());
  lines.push(
    ``,
    `Правила работы: делай в новой ветке от main, в main не вливай и на GitHub не пушь без моей просьбы. ` +
      `Перед изменениями схемы базы делай бэкап. Прогони линтеры и тесты (api, bot, web), ` +
      `в конце коротко опиши, что изменено и как проверить.`,
  );
  return lines.join("\n");
}
