from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    # EMISION_RECETA, VALIDACION_IA, DISPENSACION, MODIFICACION_USUARIO, ANULACION_RECETA, etc.
    accion = Column(String(100), nullable=False)
    tabla_afectada = Column(String(100), nullable=True)
    id_registro = Column(Integer, nullable=True)
    detalle = Column(Text, nullable=True)
    ip_origen = Column(String(45), nullable=True)
    fecha_accion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario")
