from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, usuarios, pacientes, diagnosticos, medicamentos, recetas

app = FastAPI(
    title="PHARMAGNOSTIC AI API",
    description="Backend inteligente de validación clínica hospitalaria",
    version="1.0.0",
)

# Configuración de CORS estándar para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar por la URL de React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers (endpoints en español, sin prefijo de versión, según la spec §16)
app.include_router(auth.router)          # /auth
app.include_router(usuarios.router)      # /usuarios
app.include_router(pacientes.router)     # /pacientes
app.include_router(diagnosticos.router)  # /diagnosticos
app.include_router(medicamentos.router)  # /medicamentos
app.include_router(recetas.router)       # /recetas


@app.get("/")
def read_root():
    return {"status": "online", "project": "PHARMAGNOSTIC AI"}
