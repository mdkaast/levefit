from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env ищем рядом с приложением, а не в текущей папке запуска.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str = "postgresql+psycopg://pfo:change-me@localhost:5432/pfo"
    bot_token: str = ""
    # Ключ подписи собственных токенов API; обязателен в продакшене.
    app_secret: str = ""
    # Через сколько секунд после выдачи initData считается устаревшим.
    init_data_max_age_s: int = 3600
    access_token_ttl_s: int = 3600
    cors_origins: str = "http://localhost:5173"
    # Ключ для внутренних запросов бота к API; пусто — внутренние эндпоинты отключены.
    internal_api_key: str = ""
    # Модель для ИИ-корректировки; ключ API читается SDK из ANTHROPIC_API_KEY.
    llm_model: str = "claude-opus-5-5"
    anthropic_api_key: str = ""
    llm_timeout_s: float = 90.0
    # Ключ владельца для /admin/coach/*; пусто — эндпоинты отключены.
    admin_api_key: str = ""


settings = Settings()
