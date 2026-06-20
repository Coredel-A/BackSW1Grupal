from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoUpdate, DiagnosticoOut
from app.services.diagnostico_service import DiagnosticoService

router = APIRouter(prefix="/diagnosticos", tags=["Diagnósticos"])

medico_o_admin = RoleChecker(["medico", "administrador"])


@router.post("/", response_model=DiagnosticoOut, status_code=status.HTTP_201_CREATED)
def registrar_diagnostico(
    datos: DiagnosticoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Registra un diagnóstico vinculado a un paciente (id_usuario tomado del JWT)."""
    return DiagnosticoService.registrar_diagnostico(db, datos, current_user.id_usuario)


@router.get("/{id_diagnostico}", response_model=DiagnosticoOut)
def obtener_diagnostico(
    id_diagnostico: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return DiagnosticoService.obtener_diagnostico(db, id_diagnostico)


@router.put("/{id_diagnostico}", response_model=DiagnosticoOut)
def actualizar_diagnostico(
    id_diagnostico: int,
    datos: DiagnosticoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return DiagnosticoService.actualizar_diagnostico(db, id_diagnostico, datos)
