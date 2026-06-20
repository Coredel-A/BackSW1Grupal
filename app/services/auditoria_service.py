from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.receta import Receta
from app.models.validacion_ia import ValidacionIA
from app.repositories.auditoria_repo import AuditoriaRepository


class AuditoriaService:

    @staticmethod
    def listar(
        db: Session,
        id_usuario: Optional[int] = None,
        accion: Optional[str] = None,
        tabla_afectada: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Auditoria]:
        return AuditoriaRepository.query(
            db, id_usuario, accion, tabla_afectada, fecha_desde, fecha_hasta, skip, limit
        )

    @staticmethod
    def metricas(db: Session) -> dict:
        total_recetas = db.query(func.count(Receta.id_receta)).scalar() or 0
        recetas_emitidas = (
            db.query(func.count(Receta.id_receta)).filter(Receta.fecha_emision.isnot(None)).scalar() or 0
        )
        recetas_bloqueadas = (
            db.query(func.count(Receta.id_receta)).filter(Receta.nivel_riesgo == 3).scalar() or 0
        )
        recetas_dispensadas = (
            db.query(func.count(Receta.id_receta)).filter(Receta.estado == "dispensada").scalar() or 0
        )
        recetas_anuladas = (
            db.query(func.count(Receta.id_receta)).filter(Receta.estado == "anulada").scalar() or 0
        )
        total_validaciones = db.query(func.count(ValidacionIA.id_validacion)).scalar() or 0
        tiempo_prom = db.query(func.avg(ValidacionIA.tiempo_respuesta_ms)).scalar()

        return {
            "total_recetas": total_recetas,
            "recetas_emitidas": recetas_emitidas,
            "recetas_bloqueadas_riesgo": recetas_bloqueadas,
            "recetas_dispensadas": recetas_dispensadas,
            "recetas_anuladas": recetas_anuladas,
            "total_validaciones_ia": total_validaciones,
            "tiempo_promedio_ia_ms": float(tiempo_prom) if tiempo_prom is not None else None,
        }
