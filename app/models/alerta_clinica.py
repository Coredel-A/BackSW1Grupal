from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class AlertaClinica(Base):
    """Cada hallazgo individual de una validación se materializa como una alerta mostrable."""

    __tablename__ = "alerta_clinica"

    id_alerta = Column(Integer, primary_key=True, index=True)
    id_validacion = Column(Integer, ForeignKey("validacion_ia.id_validacion"), nullable=False)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    # interaccion, contraindicacion, dosis, duplicidad, coherencia_audio, riesgo_general
    tipo_alerta = Column(String(50), nullable=False)
    nivel = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=False)
    recomendacion = Column(Text, nullable=True)
    fecha_generacion = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("nivel BETWEEN 0 AND 3", name="ck_alerta_nivel"),
    )

    validacion = relationship("ValidacionIA", back_populates="alertas")
    receta = relationship("Receta")
