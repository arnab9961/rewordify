from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    groq_cloud_api_key: str = Field(..., alias="GROQ_CLOUD_API_KEY")
    model: str = Field(default="qwen/qwen3-32b", alias="MODEL")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")
    model_temperature: float = Field(default=0.35, alias="MODEL_TEMPERATURE")
    model_max_tokens: int = Field(default=900, alias="MODEL_MAX_TOKENS")
    mongodb_url: str = Field(..., alias="Database_url")
    mongodb_db_name: str = Field(default="rewordify", alias="MONGODB_DB_NAME")
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    auth_cookie_name: str = Field(default="rewordify_token", alias="AUTH_COOKIE_NAME")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str | None = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from_email: str | None = Field(default=None, alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="ReWordify", alias="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")


settings = Settings()