from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ===== Schema para PARSEAR/VALIDAR la respuesta del modelo (spec §12.1) =====
class Interaccion(BaseModel):
    medicamentos: List[str] = []
    descripcion: str
    nivel: int = Field(ge=0, le=3)


class Contraindicacion(BaseModel):
    medicamento: str
    motivo: str
    nivel: int = Field(ge=0, le=3)


class Duplicidad(BaseModel):
    medicamentos: List[str] = []
    descripcion: str
    nivel: int = Field(ge=0, le=3)


class ErrorDosis(BaseModel):
    medicamento: str
    descripcion: str
    nivel: int = Field(ge=0, le=3)


class CoherenciaAudio(BaseModel):
    evaluado: bool = False
    porcentaje_coherencia: float = 0
    observaciones: str = ""


class IARespuesta(BaseModel):
    """Estructura exacta que debe devolver el LLM (validada con Pydantic)."""
    nivel_riesgo: int = Field(ge=0, le=3)
    justificacion_general: str
    interacciones: List[Interaccion] = []
    contraindicaciones: List[Contraindicacion] = []
    duplicidades: List[Duplicidad] = []
    errores_dosis: List[ErrorDosis] = []
    coherencia_audio: Optional[CoherenciaAudio] = None


# ===== Schemas de SALIDA de la API =====
class AlertaOut(BaseModel):
    id_alerta: int
    tipo_alerta: str
    nivel: Optional[int] = None
    descripcion: str
    recomendacion: Optional[str] = None

    class Config:
        from_attributes = True


class ValidacionOut(BaseModel):
    id_validacion: int
    id_receta: int
    id_audio: Optional[int] = None
    nivel_riesgo: Optional[int] = None
    justificacion: Optional[str] = None
    coherencia_audio: Optional[float] = None
    modelo_usado: Optional[str] = None
    tiempo_respuesta_ms: Optional[int] = None
    fecha_validacion: Optional[datetime] = None
    alertas: List[AlertaOut] = []

    class Config:
        from_attributes = True
