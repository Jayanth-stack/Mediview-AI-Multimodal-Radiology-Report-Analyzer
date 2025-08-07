from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+psycopg://mediview:mediview@localhost:5432/mediview"

    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "mediview"
    S3_SECURE: bool = False

    HF_API_TOKEN: str | None = None
    HF_IMG_CLS_MODEL: str | None = None
    HF_IMG_SEG_MODEL: str | None = None
    HF_VQA_MODEL: str | None = None
    HF_DQA_MODEL: str | None = None
    HF_SUMM_MODEL: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()

