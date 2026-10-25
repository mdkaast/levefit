from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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


settings = Settings()
