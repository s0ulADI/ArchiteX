from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    github_client_id: str | None = Field(default=None, alias="GITHUB_CLIENT_ID")
    github_client_secret: str | None = Field(default=None, alias="GITHUB_CLIENT_SECRET")
    vercel_access_token: str | None = Field(default=None, alias="VERCEL_ACCESS_TOKEN")
    scraper_timeout_seconds: int = Field(default=10, alias="SCRAPER_TIMEOUT_SECONDS")
    max_services: int = Field(default=10, alias="MAX_SERVICES")
    vision_model: str = Field(default="gemini", alias="VISION_MODEL")
    repo_ttl_seconds: int = Field(default=3600, alias="REPO_TTL_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
