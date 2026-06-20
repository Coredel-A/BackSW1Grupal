from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class AudioClinico(Base):
    __tablename__ = "audio_clinico"

    id_audio = Column(Integer, primary_key=True, index=True)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    ruta_archivo = Column(String(255), nullable=False)
    formato = Column(String(10), nullable=True)
    duracion_segundos = Column(Integer, nullable=True)
    transcripcion = Column(Text, nullable=True)
    # pendiente, procesando, completado, error
    estado_procesamiento = Column(String(30), default="pendiente", nullable=False)
    fecha_grabacion = Column(DateTime(timezone=True), server_default=func.now())

    receta = relationship("Receta")
    usuario = relationship("Usuario")
