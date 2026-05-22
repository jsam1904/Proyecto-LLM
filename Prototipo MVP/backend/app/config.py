from pathlib import Path
from pydantic_settings import BaseSettings

# Busca el .env en la raíz del proyecto (Prototipo MVP/) en lugar de dentro de backend/
# Ruta: backend/app/config.py → sube 3 niveles → Prototipo MVP/.env
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://studyai:studyai_pass@localhost:5432/studyai_db"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 semana
    ALGORITHM: str = "HS256"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"

settings = Settings()
