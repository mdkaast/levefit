// Все тексты интерфейса — здесь, на русском.
export const t = {
  appTitle: "Дневник тренировок",
  loading: "Загрузка…",
  notInTelegram: "Откройте приложение из Telegram.",
  authFailed: "Не удалось войти. Попробуйте открыть приложение заново.",
  homeStub: "Главный экран появится на следующих этапах.",
  home: {
    level: "Уровень",
  },
  create: {
    title: "Создайте персонажа",
    name: "Имя",
    namePlaceholder: "Например, Бодрый",
    appearance: "Внешний вид",
    goal: "Цель",
    goalNone: "Пока не выбрана",
    workoutsPerWeek: "Тренировок в неделю",
    equipment: "Оборудование",
    submit: "Начать",
    saving: "Сохраняем…",
    error: "Не удалось создать персонажа. Попробуйте ещё раз.",
    nameRequired: "Введите имя",
    nameTooLong: "Имя не длиннее 30 символов",
  },
  appearances: { warrior: "Воин", runner: "Бегун", sage: "Мудрец" },
  goals: { mass: "Набор массы", strength: "Сила", shape: "Форма" },
  equipment: { gym: "Спортзал", home: "Дом", none: "Без оборудования" },
} as const;
