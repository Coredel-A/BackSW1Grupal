from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id_diagnostico = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    codigo_cie10 = Column(String(10), nullable=True)
    descripcion = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=True)  # preliminar, confirmado, diferencial
    observaciones = Column(Text, nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    paciente = relationship("Paciente", back_populates="diagnosticos")
    usuario = relationship("Usuario")
    recetas = relationship("Receta", back_populates="diagnostico")
