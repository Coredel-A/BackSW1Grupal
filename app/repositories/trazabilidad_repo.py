from typing import Optional
from sqlalchemy.orm import Session

from app.models.trazabilidad_blockchain import TrazabilidadBlockchain


class TrazabilidadRepository:

    @staticmethod
    def create(db: Session, registro: TrazabilidadBlockchain) -> TrazabilidadBlockchain:
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    @staticmethod
    def get_by_receta(db: Session, id_receta: int) -> Optional[TrazabilidadBlockchain]:
        return (
            db.query(TrazabilidadBlockchain)
            .filter(TrazabilidadBlockchain.id_receta == id_receta)
            .order_by(TrazabilidadBlockchain.fecha_registro.desc())
            .first()
        )
