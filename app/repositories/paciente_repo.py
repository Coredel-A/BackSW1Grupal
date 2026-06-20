from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.paciente import Paciente
from app.models.historial_clinico import HistorialClinico


class PacienteRepository:

    @staticmethod
    def get_by_id(db: Session, id_paciente: int) -> Optional[Paciente]:
        return db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()

    @staticmethod
    def get_by_ci(db: Session, ci: str) -> Optional[Paciente]:
        return db.query(Paciente).filter(Paciente.ci == ci).first()

    @staticmethod
    def search(
        db: Session, busqueda: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Paciente]:
        """Búsqueda dinámica por CI, nombre o apellido (parcial, case-insensitive)."""
        query = db.query(Paciente)
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            query = query.filter(
                or_(
                    Paciente.ci.ilike(patron),
                    Paciente.nombre.ilike(patron),
                    Paciente.apellido.ilike(patron),
                )
            )
        return query.order_by(Paciente.apellido, Paciente.nombre).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, paciente_db: Paciente) -> Paciente:
        db.add(paciente_db)
        db.commit()
        db.refresh(paciente_db)
        return paciente_db

    @staticmethod
    def update(db: Session) -> None:
        db.commit()

    @staticmethod
    def toggle_activo(db: Session, paciente_db: Paciente) -> Paciente:
        paciente_db.activo = not paciente_db.activo
        db.commit()
        db.refresh(paciente_db)
        return paciente_db

    # --- Historial clínico ---
    @staticmethod
    def add_historial(db: Session, historial_db: HistorialClinico) -> HistorialClinico:
        db.add(historial_db)
        db.commit()
        db.refresh(historial_db)
        return historial_db

    @staticmethod
    def get_historial(db: Session, id_paciente: int) -> List[HistorialClinico]:
        return (
            db.query(HistorialClinico)
            .filter(HistorialClinico.id_paciente == id_paciente)
            .order_by(HistorialClinico.fecha_registro.desc())
            .all()
        )
