from typing import Optional
from sqlalchemy.orm import Session

from app.models.dispensacion import Dispensacion


class DispensacionRepository:

    @staticmethod
    def create(db: Session, disp: Dispensacion) -> Dispensacion:
        db.add(disp)
        db.commit()
        db.refresh(disp)
        return disp

    @staticmethod
    def update(db: Session) -> None:
        db.commit()

    @staticmethod
    def get_confirmada_by_receta(db: Session, id_receta: int) -> Optional[Dispensacion]:
        return (
            db.query(Dispensacion)
            .filter(Dispensacion.id_receta == id_receta, Dispensacion.estado == "confirmada")
            .order_by(Dispensacion.fecha_dispensacion.desc())
            .first()
        )
