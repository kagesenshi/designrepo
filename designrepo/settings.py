from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str = "sqlite:///reflex.db"
    openai_api_key: str = ""
    oidc_issuer: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_session_secret: str = ""
    oidc_redirect_uri: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DESIGNREPO_", extra="ignore"
    )


settings = Settings()
