from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaOut, MetricasOut
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/admin", tags=["Administración"])

es_admin = RoleChecker(["administrador"])


@router.get("/auditoria", response_model=List[AuditoriaOut])
def listar_auditoria(
    id_usuario: Optional[int] = None,
    accion: Optional[str] = None,
    tabla_afectada: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(es_admin),
):
    """Log de auditoría con filtros por usuario, acción, tabla y rango de fechas."""
    return AuditoriaService.listar(
        db, id_usuario, accion, tabla_afectada, fecha_desde, fecha_hasta, skip, limit
    )


@router.get("/metricas", response_model=MetricasOut)
def metricas(db: Session = Depends(get_db), _: Usuario = Depends(es_admin)):
    """Métricas del sistema: recetas emitidas/bloqueadas/dispensadas/anuladas y tiempo medio de la IA."""
    return AuditoriaService.metricas(db)
