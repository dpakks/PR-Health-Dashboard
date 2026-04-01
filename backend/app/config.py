from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application info
    APP_NAME: str = "PR Health Dashboard"

    # JWT Configuration
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Database Configuration
    DATABASE_URL: str = ""

    # GitHub
    GITHUB_TOKEN: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_DECODE_RESPONSES: bool = True

    # AWS SES Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    SES_SENDER_EMAIL: str = ""

    # OTP Configuration
    OTP_LENGTH: int = 6
    OTP_EXPIRE_SECONDS: int = 300

    class Config:
        env_file = ".env"


settings = Settings()