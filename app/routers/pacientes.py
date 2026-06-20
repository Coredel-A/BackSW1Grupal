from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.paciente import (
    PacienteCreate,
    PacienteUpdate,
    PacienteOut,
    HistorialClinicoCreate,
    HistorialClinicoOut,
)
from app.schemas.diagnostico import DiagnosticoOut
from app.services.paciente_service import PacienteService

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# El flujo clínico de pacientes lo realizan médicos; el administrador también tiene acceso.
medico_o_admin = RoleChecker(["medico", "administrador"])


@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def registrar_paciente(
    datos: PacienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Registra un paciente nuevo (CI único e inmutable)."""
    return PacienteService.registrar_paciente(db, datos)


@router.get("/", response_model=List[PacienteOut])
def listar_pacientes(
    busqueda: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Lista/busca pacientes por CI, nombre o apellido (parámetro `busqueda`)."""
    return PacienteService.buscar_pacientes(db, busqueda=busqueda, skip=skip, limit=limit)


@router.get("/{id_paciente}", response_model=PacienteOut)
def obtener_paciente(
    id_paciente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return PacienteService.obtener_paciente(db, id_paciente)


@router.put("/{id_paciente}", response_model=PacienteOut)
def actualizar_paciente(
    id_paciente: int,
    datos: PacienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Edita un paciente (el CI no es editable)."""
    return PacienteService.actualizar_paciente(db, id_paciente, datos)


@router.patch("/{id_paciente}/estado", response_model=PacienteOut)
def cambiar_estado_paciente(
    id_paciente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Activa/desactiva (soft delete) un paciente."""
    return PacienteService.cambiar_estado(db, id_paciente)


# --- Historial clínico ---
@router.post("/{id_paciente}/historial", response_model=HistorialClinicoOut, status_code=status.HTTP_201_CREATED)
def agregar_historial(
    id_paciente: int,
    datos: HistorialClinicoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Agrega un evento al historial clínico (id_usuario tomado del JWT)."""
    return PacienteService.agregar_historial(db, id_paciente, datos, current_user.id_usuario)


@router.get("/{id_paciente}/historial", response_model=List[HistorialClinicoOut])
def obtener_historial(
    id_paciente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return PacienteService.obtener_historial(db, id_paciente)


@router.get("/{id_paciente}/diagnosticos", response_model=List[DiagnosticoOut])
def obtener_diagnosticos(
    id_paciente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return PacienteService.obtener_diagnosticos(db, id_paciente)
