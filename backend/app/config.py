from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application info
    APP_NAME: str = "PR Health Dashboard"

    # JWT Configuration
    JWT_SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/pr_dashboard"

    class Config:
        env_file = ".env"


settings = Settings()
