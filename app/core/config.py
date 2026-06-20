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

    # --- IA local (Sprint 2) ---
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3:8b")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    # Timeout alto para tolerar el arranque en frío (carga del modelo a VRAM la 1ª vez)
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
    # Carpeta donde se guardan los audios clínicos subidos
    AUDIO_DIR: str = os.getenv("AUDIO_DIR", "/app/audios")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # --- Blockchain (Sprint 3) ---
    BLOCKCHAIN_URL: str = os.getenv("BLOCKCHAIN_URL", "http://localhost:8545")
    CONTRACT_ADDRESS: str = os.getenv(
        "CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    )
    BLOCKCHAIN_PRIVATE_KEY: str = os.getenv(
        "BLOCKCHAIN_PRIVATE_KEY",
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    )


settings = Settings()
