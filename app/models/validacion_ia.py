from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class ValidacionIA(Base):
    """Una validación de IA por ejecución (se permiten múltiples por receta -> historial)."""

    __tablename__ = "validacion_ia"

    id_validacion = Column(Integer, primary_key=True, index=True)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    id_audio = Column(Integer, ForeignKey("audio_clinico.id_audio"), nullable=True)
    nivel_riesgo = Column(Integer, nullable=True)
    justificacion = Column(Text, nullable=True)
    # Cada uno guarda el array de hallazgos serializado como JSON (string)
    interacciones = Column(Text, nullable=True)
    contraindicaciones = Column(Text, nullable=True)
    duplicidades = Column(Text, nullable=True)
    errores_dosis = Column(Text, nullable=True)
    coherencia_audio = Column(Numeric(5, 2), nullable=True)
    modelo_usado = Column(String(100), nullable=True)
    tiempo_respuesta_ms = Column(Integer, nullable=True)
    fecha_validacion = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("nivel_riesgo BETWEEN 0 AND 3", name="ck_validacion_nivel_riesgo"),
    )

    receta = relationship("Receta")
    audio = relationship("AudioClinico")
    alertas = relationship("AlertaClinica", back_populates="validacion", cascade="all, delete-orphan")
