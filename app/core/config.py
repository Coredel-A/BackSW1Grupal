import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env (no sobreescribe variables ya definidas
# por Docker Compose, así que en contenedor mandan las del compose y en local el .env)
load_dotenv()


class Settings:
    PROJECT_NAME: str = "PHARMAGNOSTIC AI"

    # --- Base de datos PostgreSQL ---
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "SW1Grupal")

    # Formato estándar de URL de conexión para SQLAlchemy
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # --- Seguridad / JWT ---
    # En producción SECRET_KEY debe venir SIEMPRE del entorno; el valor por defecto
    # es solo un fallback de desarrollo.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-insecure-secret-change-me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 horas


settings = Settings()
