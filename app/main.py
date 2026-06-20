from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth, usuarios, pacientes, diagnosticos, medicamentos, recetas,
    validaciones, audio, farmacia, admin, paciente,
)
from app.middlewares.auditoria_middleware import AuditoriaMiddleware

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

# Auditoría automática de acciones críticas (spec §11)
app.add_middleware(AuditoriaMiddleware)

# Registro de routers (endpoints en español, sin prefijo de versión, según la spec §16)
app.include_router(auth.router)          # /auth
app.include_router(usuarios.router)      # /usuarios
app.include_router(pacientes.router)     # /pacientes
app.include_router(diagnosticos.router)  # /diagnosticos
app.include_router(medicamentos.router)  # /medicamentos
app.include_router(recetas.router)       # /recetas
app.include_router(validaciones.router)  # /recetas/{id}/validar, /ia/health
app.include_router(audio.router)         # /audio
app.include_router(farmacia.router)      # /farmacia
app.include_router(admin.router)         # /admin (auditoría, métricas)
app.include_router(paciente.router)      # /paciente (portal, chatbot)


@app.get("/")
def read_root():
    return {"status": "online", "project": "PHARMAGNOSTIC AI"}
