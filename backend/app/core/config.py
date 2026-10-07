import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Locate and load the .env file from the backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Aqua Rover Backend")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # PostgreSQL Database URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aqua_rover",
    )

    # CORS Configuration
    @property
    def cors_origins(self) -> List[str]:
        raw_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        )
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


settings = Settings()
