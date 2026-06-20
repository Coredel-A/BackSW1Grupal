from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.receta import RecetaOut


class VerificacionOut(BaseModel):
    # valida, anulada, dispensada, integridad_fallida, borrador, no_encontrada
    estado_verificacion: str
    puede_dispensar: bool
    mensaje: str
    hash_receta: Optional[str] = None
    receta: Optional[RecetaOut] = None


class DispensarRequest(BaseModel):
    id_receta: int


class RechazarRequest(BaseModel):
    id_receta: int
    motivo: str = Field(..., min_length=1)


class DispensacionOut(BaseModel):
    id_dispensacion: int
    id_receta: int
    id_usuario: int
    estado: str
    observaciones: Optional[str] = None
    fecha_dispensacion: Optional[datetime] = None

    class Config:
        from_attributes = True
