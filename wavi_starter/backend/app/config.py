from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Wavi Backend"
    environment: str = "development"
    telegram_bot_token: str
    telegram_bot_username: str = "WaviCityVibe_bot"
    telegram_secret_token: str
    public_base_url: str
    miniapp_url: str
    database_url: str
    admin_setup_key: str
    yandex_maps_url: str = "https://yandex.ru/maps/?rtext={user_lat},{user_lon}~{place_lat},{place_lon}&rtt=auto"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
