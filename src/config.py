from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "near-realtime-scheduling"
    db_url: str = "sqlite:///./data/scheduler.db"
    max_workers: int = 10
    timezone: str = "Asia/Taipei"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
