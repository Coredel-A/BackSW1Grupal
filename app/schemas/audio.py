from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AudioOut(BaseModel):
    id_audio: int
    id_receta: int
    id_usuario: int
    formato: Optional[str] = None
    duracion_segundos: Optional[int] = None
    transcripcion: Optional[str] = None
    estado_procesamiento: str
    fecha_grabacion: Optional[datetime] = None

    class Config:
        from_attributes = True
