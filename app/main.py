from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import receta_router
from app.routers import auth, usuarios

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

# 3. REGISTRO DE TODAS LAS RUTAS EN EL SERVIDOR
# Tus rutas de recetas existentes:
app.include_router(receta_router.router) 

# Tus nuevas rutas de autenticación y gestión de usuarios:
app.include_router(auth.router, prefix="/api/v1")
app.include_router(usuarios.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "online", "project": "PHARMAGNOSTIC AI"}