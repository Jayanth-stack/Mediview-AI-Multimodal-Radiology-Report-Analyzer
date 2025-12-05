from typing import Optional
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
    PUBLIC_S3_ENDPOINT_URL: str = "http://localhost:9000"
    REDIS_URL: str = "redis://redis:6379/0"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_VISION_MODEL: str = "gemini-1.5-flash"

    # RAG Configuration
    RAG_ENABLED: bool = True
    EMBEDDING_MODEL: str = "models/embedding-001"
    VECTOR_DIMENSION: int = 768
    RAG_TOP_K: int = 5

    SECRET_KEY: str = "supersecretkey"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    class Config:
        env_file = ".env"


settings = Settings()

