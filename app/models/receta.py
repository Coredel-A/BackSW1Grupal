from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Receta(Base):
    __tablename__ = "receta"

    id_receta = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)  # médico emisor
    id_diagnostico = Column(Integer, ForeignKey("diagnostico.id_diagnostico"), nullable=True)
    # borrador, validada, bloqueada, dispensada, anulada
    estado = Column(String(30), default="borrador", nullable=False)
    nivel_riesgo = Column(Integer, nullable=True)
    resumen_validacion = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    fecha_emision = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("nivel_riesgo BETWEEN 0 AND 3", name="ck_receta_nivel_riesgo"),
    )

    paciente = relationship("Paciente", back_populates="recetas")
    usuario = relationship("Usuario")
    diagnostico = relationship("Diagnostico", back_populates="recetas")
    medicamentos = relationship(
        "RecetaMedicamento", back_populates="receta", cascade="all, delete-orphan"
    )
