from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria


class AuditoriaRepository:

    @staticmethod
    def create(db: Session, registro: Auditoria) -> Auditoria:
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    @staticmethod
    def query(
        db: Session,
        id_usuario: Optional[int] = None,
        accion: Optional[str] = None,
        tabla_afectada: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Auditoria]:
        q = db.query(Auditoria)
        if id_usuario is not None:
            q = q.filter(Auditoria.id_usuario == id_usuario)
        if accion:
            q = q.filter(Auditoria.accion == accion)
        if tabla_afectada:
            q = q.filter(Auditoria.tabla_afectada == tabla_afectada)
        if fecha_desde:
            q = q.filter(Auditoria.fecha_accion >= fecha_desde)
        if fecha_hasta:
            q = q.filter(Auditoria.fecha_accion <= fecha_hasta)
        return q.order_by(Auditoria.fecha_accion.desc()).offset(skip).limit(limit).all()
