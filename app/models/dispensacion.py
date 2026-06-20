from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Dispensacion(Base):
    __tablename__ = "dispensacion"

    id_dispensacion = Column(Integer, primary_key=True, index=True)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)  # farmacéutico
    codigo_qr = Column(String(255), unique=True, nullable=True)
    # pendiente, confirmada, rechazada
    estado = Column(String(30), default="pendiente", nullable=False)
    observaciones = Column(Text, nullable=True)  # motivo si fue rechazada
    fecha_dispensacion = Column(DateTime(timezone=True), nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    receta = relationship("Receta")
    usuario = relationship("Usuario")
