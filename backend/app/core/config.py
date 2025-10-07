from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Personal Finance API"
    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./finance.db"
    JWT_SECRET: str = "change_me"
    GEMINI_API_KEY: str = ""  # Add your Gemini API key in .env file

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()