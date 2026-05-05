from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./intent_planner.db"
    APP_TITLE: str = "Intent Planner"
    DEBUG: bool = False
    META_ACCESS_TOKEN: str = Field(default="", alias="META_ACCESS_TOKEN")

    model_config = {"env_prefix": "INTENT_PLANNER_", "populate_by_name": True}


settings = Settings()
