from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.validacion_ia import ValidacionIA
from app.models.alerta_clinica import AlertaClinica
from app.models.audio_clinico import AudioClinico


class ValidacionRepository:

    @staticmethod
    def create(db: Session, validacion: ValidacionIA) -> ValidacionIA:
        db.add(validacion)
        db.commit()
        db.refresh(validacion)
        return validacion

    @staticmethod
    def add_alertas(db: Session, alertas: List[AlertaClinica]) -> None:
        db.add_all(alertas)
        db.commit()

    @staticmethod
    def get_by_id(db: Session, id_validacion: int) -> Optional[ValidacionIA]:
        return (
            db.query(ValidacionIA)
            .options(joinedload(ValidacionIA.alertas))
            .filter(ValidacionIA.id_validacion == id_validacion)
            .first()
        )

    @staticmethod
    def get_by_receta(db: Session, id_receta: int) -> List[ValidacionIA]:
        """Todas las validaciones de una receta (historial), de la más reciente a la más antigua."""
        return (
            db.query(ValidacionIA)
            .options(joinedload(ValidacionIA.alertas))
            .filter(ValidacionIA.id_receta == id_receta)
            .order_by(ValidacionIA.fecha_validacion.desc())
            .all()
        )

    @staticmethod
    def get_ultimo_audio_completado(db: Session, id_receta: int) -> Optional[AudioClinico]:
        return (
            db.query(AudioClinico)
            .filter(
                AudioClinico.id_receta == id_receta,
                AudioClinico.estado_procesamiento == "completado",
            )
            .order_by(AudioClinico.fecha_grabacion.desc())
            .first()
        )
