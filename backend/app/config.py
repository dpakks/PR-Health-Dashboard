from pydantic import BaseSettings


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "PR Health Dashboard"

    # JWT settings
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/pr_dashboard"

    class Config:
        env_file = ".env"


settings = Settings()
