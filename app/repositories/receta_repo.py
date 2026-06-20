from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.receta import Receta
from app.models.receta_medicamento import RecetaMedicamento


class RecetaRepository:

    @staticmethod
    def get_by_id(db: Session, id_receta: int) -> Optional[Receta]:
        """Receta con sus relaciones cargadas (medicamentos + catálogo, paciente, médico, diagnóstico)."""
        return (
            db.query(Receta)
            .options(
                joinedload(Receta.medicamentos).joinedload(RecetaMedicamento.medicamento),
                joinedload(Receta.paciente),
                joinedload(Receta.usuario),
                joinedload(Receta.diagnostico),
            )
            .filter(Receta.id_receta == id_receta)
            .first()
        )

    @staticmethod
    def create(db: Session, receta_db: Receta) -> Receta:
        db.add(receta_db)
        db.commit()
        db.refresh(receta_db)
        return receta_db

    @staticmethod
    def update(db: Session) -> None:
        db.commit()

    @staticmethod
    def get_by_paciente(db: Session, id_paciente: int) -> List[Receta]:
        return (
            db.query(Receta)
            .options(joinedload(Receta.medicamentos).joinedload(RecetaMedicamento.medicamento))
            .filter(Receta.id_paciente == id_paciente)
            .order_by(Receta.fecha_creacion.desc())
            .all()
        )

    @staticmethod
    def get_by_medico(db: Session, id_usuario: int) -> List[Receta]:
        return (
            db.query(Receta)
            .options(joinedload(Receta.medicamentos).joinedload(RecetaMedicamento.medicamento))
            .filter(Receta.id_usuario == id_usuario)
            .order_by(Receta.fecha_creacion.desc())
            .all()
        )

    # --- Ítems receta_medicamento ---
    @staticmethod
    def add_medicamento(db: Session, item_db: RecetaMedicamento) -> RecetaMedicamento:
        db.add(item_db)
        db.commit()
        db.refresh(item_db)
        return item_db

    @staticmethod
    def get_medicamento(db: Session, id_receta_med: int) -> Optional[RecetaMedicamento]:
        return (
            db.query(RecetaMedicamento)
            .filter(RecetaMedicamento.id_receta_med == id_receta_med)
            .first()
        )

    @staticmethod
    def delete_medicamento(db: Session, item_db: RecetaMedicamento) -> None:
        db.delete(item_db)
        db.commit()
