from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Crear el motor de conexión
engine = create_engine(settings.DATABASE_URL)

# 2. Crear la fábrica de sesiones (para hacer consultas)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Clase base de la que heredarán todos nuestros futuros modelos ORM
Base = declarative_base()

# --- IMPORTANTE PARA ALEMBIC ---
# Importamos TODOS los modelos aquí para que se registren en Base.metadata
# (el paquete app.models reexporta cada entidad en su __init__).
import app.models  # noqa: F401,E402

# 4. Función estándar (Dependencia) para abrir y cerrar la BD limpiamente
def get_db():
    db = SessionLocal()
    try:
        yield db  # Cede la sesión al router de FastAPI
    finally:
        db.close()  # Se asegura de cerrar la conexión al terminar la petición HTTP