from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.validacion import ValidacionOut
from app.services.ia_validacion_service import IAValidacionService
from app.ai.ollama_client import ollama_disponible
from app.ai.chroma_client import ping as chroma_ping

router = APIRouter(tags=["Validación IA"])

medico_o_admin = RoleChecker(["medico", "administrador"])


@router.post("/recetas/{id_receta}/validar", response_model=ValidacionOut, status_code=status.HTTP_201_CREATED)
def validar_receta(
    id_receta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Ejecuta la validación farmacoterapéutica con IA (RAG + Llama 3) sobre la receta."""
    return IAValidacionService.ejecutar_validacion(db, id_receta)


@router.get("/recetas/{id_receta}/validaciones", response_model=List[ValidacionOut])
def historial_validaciones(
    id_receta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Historial de validaciones de una receta (se preservan las re-validaciones)."""
    return IAValidacionService.historial_por_receta(db, id_receta)


@router.get("/ia/health")
def ia_health():
    """Estado de los servicios de IA (para que el frontend avise si no están disponibles)."""
    return {"ollama": ollama_disponible(), "chroma": chroma_ping()}
