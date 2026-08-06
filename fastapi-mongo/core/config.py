# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    SECRET_KEY: str
    FRONTEND_URL: str
    GEMINI_API_KEY: str
    YOUTUBE_API_KEY: str
    CORS_ORIGINS: str

    class Config:
        env_file = ".env"


settings = Settings()
