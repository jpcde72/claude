from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./intent_planner.db"
    APP_TITLE: str = "Intent Planner"
    DEBUG: bool = False
    GEO_MODEL: str = "claude-opus-5"
    GEO_MAX_TOKENS: int = 32000

    model_config = {"env_prefix": "INTENT_PLANNER_"}


settings = Settings()
