from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.medicamento import MedicamentoCreate, MedicamentoUpdate, MedicamentoOut
from app.services.medicamento_service import MedicamentoService

router = APIRouter(prefix="/medicamentos", tags=["Catálogo de Medicamentos"])

# El catálogo lo administra el admin; médicos y farmacéuticos lo consultan.
es_admin = RoleChecker(["administrador"])
puede_consultar = RoleChecker(["administrador", "medico", "farmaceutico"])


@router.post("/", response_model=MedicamentoOut, status_code=status.HTTP_201_CREATED)
def crear_medicamento(
    datos: MedicamentoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(es_admin),
):
    return MedicamentoService.crear_medicamento(db, datos)


@router.get("/", response_model=List[MedicamentoOut])
def listar_medicamentos(
    busqueda: Optional[str] = None,
    solo_activos: bool = False,
    db: Session = Depends(get_db),
    _: Usuario = Depends(puede_consultar),
):
    """Lista/busca medicamentos del catálogo (parámetros `busqueda` y `solo_activos`)."""
    return MedicamentoService.listar_medicamentos(db, busqueda=busqueda, solo_activos=solo_activos)


@router.get("/{id_medicamento}", response_model=MedicamentoOut)
def obtener_medicamento(
    id_medicamento: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(puede_consultar),
):
    return MedicamentoService.obtener_medicamento(db, id_medicamento)


@router.put("/{id_medicamento}", response_model=MedicamentoOut)
def actualizar_medicamento(
    id_medicamento: int,
    datos: MedicamentoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(es_admin),
):
    return MedicamentoService.actualizar_medicamento(db, id_medicamento, datos)


@router.patch("/{id_medicamento}/estado", response_model=MedicamentoOut)
def cambiar_estado_medicamento(
    id_medicamento: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(es_admin),
):
    """Activa/desactiva (soft delete) un medicamento del catálogo."""
    return MedicamentoService.cambiar_estado(db, id_medicamento)
