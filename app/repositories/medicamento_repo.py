from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.medicamento_catalogo import MedicamentoCatalogo


class MedicamentoRepository:

    @staticmethod
    def get_by_id(db: Session, id_medicamento: int) -> Optional[MedicamentoCatalogo]:
        return (
            db.query(MedicamentoCatalogo)
            .filter(MedicamentoCatalogo.id_medicamento == id_medicamento)
            .first()
        )

    @staticmethod
    def search(
        db: Session,
        busqueda: Optional[str] = None,
        solo_activos: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> List[MedicamentoCatalogo]:
        query = db.query(MedicamentoCatalogo)
        if solo_activos:
            query = query.filter(MedicamentoCatalogo.activo.is_(True))
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            query = query.filter(
                or_(
                    MedicamentoCatalogo.nombre_generico.ilike(patron),
                    MedicamentoCatalogo.nombre_comercial.ilike(patron),
                    MedicamentoCatalogo.grupo_farmacologico.ilike(patron),
                )
            )
        return query.order_by(MedicamentoCatalogo.nombre_generico).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, medicamento_db: MedicamentoCatalogo) -> MedicamentoCatalogo:
        db.add(medicamento_db)
        db.commit()
        db.refresh(medicamento_db)
        return medicamento_db

    @staticmethod
    def update(db: Session) -> None:
        db.commit()

    @staticmethod
    def toggle_activo(db: Session, medicamento_db: MedicamentoCatalogo) -> MedicamentoCatalogo:
        medicamento_db.activo = not medicamento_db.activo
        db.commit()
        db.refresh(medicamento_db)
        return medicamento_db
