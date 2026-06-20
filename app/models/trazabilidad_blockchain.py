from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class TrazabilidadBlockchain(Base):
    __tablename__ = "trazabilidad_blockchain"

    id_registro = Column(Integer, primary_key=True, index=True)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    hash_receta = Column(String(255), unique=True, nullable=False)
    bloque_id = Column(String(255), nullable=True)
    direccion_contrato = Column(String(255), nullable=True)
    timestamp_blockchain = Column(DateTime(timezone=True), nullable=True)
    id_usuario_firmante = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    receta = relationship("Receta")
    firmante = relationship("Usuario")
