from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./intent_planner.db"
    APP_TITLE: str = "Intent Planner"
    DEBUG: bool = False

    # --- GEO audit / diagnostic settings ---
    # Accept both bare env names (GEMINI_API_KEY) and prefixed ones.
    GEMINI_API_KEY: str = Field(
        "", validation_alias=AliasChoices("GEMINI_API_KEY", "INTENT_PLANNER_GEMINI_API_KEY")
    )
    GEMINI_MODEL: str = Field(
        "gemini-2.5-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "INTENT_PLANNER_GEMINI_MODEL"),
    )
    SERPAPI_API_KEY: str = Field(
        "", validation_alias=AliasChoices("SERPAPI_API_KEY", "INTENT_PLANNER_SERPAPI_API_KEY")
    )
    GEO_HTTP_TIMEOUT: float = Field(
        30.0, validation_alias=AliasChoices("GEO_HTTP_TIMEOUT", "INTENT_PLANNER_GEO_HTTP_TIMEOUT")
    )
    GEO_GL: str = Field(
        "us", validation_alias=AliasChoices("GEO_GL", "INTENT_PLANNER_GEO_GL")
    )
    GEO_HL: str = Field(
        "en", validation_alias=AliasChoices("GEO_HL", "INTENT_PLANNER_GEO_HL")
    )

    model_config = {"env_prefix": "INTENT_PLANNER_"}


settings = Settings()
