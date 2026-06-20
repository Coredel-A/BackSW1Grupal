from typing import List, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.receta import (
    RecetaCreate,
    RecetaUpdate,
    RecetaOut,
    RecetaMedicamentoCreate,
    RecetaMedicamentoUpdate,
)
from app.services.receta_service import RecetaService

router = APIRouter(prefix="/recetas", tags=["Recetas"])

medico_o_admin = RoleChecker(["medico", "administrador"])
# El farmacéutico también necesita ver/descargar la receta al dispensar.
puede_ver = RoleChecker(["medico", "administrador", "farmaceutico"])


@router.post("/", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
def crear_receta(
    datos: RecetaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Crea una receta en borrador (médico emisor tomado del JWT)."""
    return RecetaService.crear_receta(db, datos, current_user.id_usuario)


@router.get("/", response_model=List[RecetaOut])
def listar_recetas(
    id_paciente: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Lista recetas por paciente (`?id_paciente=`) o, sin filtro, las del médico autenticado."""
    if id_paciente is not None:
        return RecetaService.listar_por_paciente(db, id_paciente)
    return RecetaService.listar_por_medico(db, current_user.id_usuario)


@router.get("/{id_receta}", response_model=RecetaOut)
def obtener_receta(
    id_receta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(puede_ver),
):
    return RecetaService.obtener_receta(db, id_receta)


@router.put("/{id_receta}", response_model=RecetaOut)
def actualizar_receta(
    id_receta: int,
    datos: RecetaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Edita la receta (diagnóstico/observaciones) solo mientras está en borrador."""
    return RecetaService.actualizar_receta(db, id_receta, datos)


@router.post("/{id_receta}/medicamentos", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
def agregar_medicamento(
    id_receta: int,
    datos: RecetaMedicamentoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return RecetaService.agregar_medicamento(db, id_receta, datos)


@router.put("/{id_receta}/medicamentos/{id_receta_med}", response_model=RecetaOut)
def editar_medicamento(
    id_receta: int,
    id_receta_med: int,
    datos: RecetaMedicamentoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return RecetaService.editar_medicamento(db, id_receta, id_receta_med, datos)


@router.delete("/{id_receta}/medicamentos/{id_receta_med}", response_model=RecetaOut)
def eliminar_medicamento(
    id_receta: int,
    id_receta_med: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    return RecetaService.eliminar_medicamento(db, id_receta, id_receta_med)


@router.post("/{id_receta}/emitir", response_model=RecetaOut)
def emitir_receta(
    id_receta: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Aprueba y emite la receta: genera hash, lo ancla en blockchain y pasa a 'validada'."""
    return RecetaService.emitir_receta(db, id_receta, current_user.id_usuario)


@router.patch("/{id_receta}/anular", response_model=RecetaOut)
def anular_receta(
    id_receta: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Anula una receta. El médico solo si está validada y no dispensada; el admin en cualquier estado."""
    return RecetaService.anular_receta(db, id_receta, current_user)


@router.get("/{id_receta}/pdf")
def descargar_pdf(
    id_receta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(puede_ver),
):
    """Descarga el PDF de la receta."""
    pdf = RecetaService.generar_pdf(db, id_receta)
    headers = {"Content-Disposition": f'inline; filename="receta_{id_receta}.pdf"'}
    return StreamingResponse(pdf, media_type="application/pdf", headers=headers)
