from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.diagnostico import Diagnostico


class DiagnosticoRepository:

    @staticmethod
    def get_by_id(db: Session, id_diagnostico: int) -> Optional[Diagnostico]:
        return db.query(Diagnostico).filter(Diagnostico.id_diagnostico == id_diagnostico).first()

    @staticmethod
    def create(db: Session, diagnostico_db: Diagnostico) -> Diagnostico:
        db.add(diagnostico_db)
        db.commit()
        db.refresh(diagnostico_db)
        return diagnostico_db

    @staticmethod
    def update(db: Session) -> None:
        db.commit()

    @staticmethod
    def get_by_paciente(db: Session, id_paciente: int) -> List[Diagnostico]:
        return (
            db.query(Diagnostico)
            .filter(Diagnostico.id_paciente == id_paciente)
            .order_by(Diagnostico.fecha_registro.desc())
            .all()
        )

    @staticmethod
    def get_confirmados_by_paciente(db: Session, id_paciente: int) -> List[Diagnostico]:
        """Diagnósticos confirmados de un paciente (insumo para vincular a una receta)."""
        return (
            db.query(Diagnostico)
            .filter(Diagnostico.id_paciente == id_paciente, Diagnostico.tipo == "confirmado")
            .order_by(Diagnostico.fecha_registro.desc())
            .all()
        )
