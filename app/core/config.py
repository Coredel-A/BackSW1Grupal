import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "PHARMAGNOSTIC AI"
    
    # Construcción de la URL de conexión para PostgreSQL
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "SW1Grupal")
    
    # Formato estándar de URL de conexión para SQLAlchemy
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

settings = Settings()