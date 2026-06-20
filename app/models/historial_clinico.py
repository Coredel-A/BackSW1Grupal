from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class HistorialClinico(Base):
    __tablename__ = "historial_clinico"

    id_historial = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    # internacion, alergia_nueva, evento_adverso, cirugia, antecedente, otro
    tipo_evento = Column(String(100), nullable=True)

    paciente = relationship("Paciente", back_populates="historiales")
    usuario = relationship("Usuario")
