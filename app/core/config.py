from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    groq_cloud_api_key: str = Field(..., alias="GROQ_CLOUD_API_KEY")
    model: str = Field(default="qwen/qwen3-32b", alias="MODEL")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")
    model_temperature: float = Field(default=0.35, alias="MODEL_TEMPERATURE")
    model_max_tokens: int = Field(default=900, alias="MODEL_MAX_TOKENS")


settings = Settings()