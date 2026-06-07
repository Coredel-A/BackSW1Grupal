from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import receta_router

app = FastAPI(
    title="PHARMAGNOSTIC AI API",
    description="Backend inteligente de validación clínica hospitalaria",
    version="1.0.0"
)

# Configuración de CORS estándar para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar por la URL de React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers (rutas modulares)
app.include_router(receta_router.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "online", "project": "PHARMAGNOSTIC AI"}