# PFO — игровой дневник тренировок (Telegram Mini App)

Монорепозиторий: `apps/web` (React), `apps/api` (FastAPI), `apps/bot` (aiogram). Решения и ТЗ — в `docs/`.

## Запуск

```bash
cp .env.example .env   # заполнить BOT_TOKEN и WEBAPP_URL
docker compose up --build
```

- API: http://localhost:8000/health
- Web: http://localhost:5173

## Проверки без Docker

```bash
cd apps/api && pip install -r requirements-dev.txt && ruff check . && pytest
cd apps/bot && pip install -r requirements-dev.txt && ruff check . && pytest
cd apps/web && npm install && npm run lint && npm run build && npm test
```

## Правила

Игровые правила считает только сервер (`apps/api/app/game_rules`). Миграции — только через Alembic. Секреты — только в `.env`.
