from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditoriaOut(BaseModel):
    id_auditoria: int
    id_usuario: Optional[int] = None
    accion: str
    tabla_afectada: Optional[str] = None
    id_registro: Optional[int] = None
    detalle: Optional[str] = None
    ip_origen: Optional[str] = None
    fecha_accion: Optional[datetime] = None

    class Config:
        from_attributes = True


class MetricasOut(BaseModel):
    total_recetas: int
    recetas_emitidas: int
    recetas_bloqueadas_riesgo: int  # nivel de riesgo 3
    recetas_dispensadas: int
    recetas_anuladas: int
    total_validaciones_ia: int
    tiempo_promedio_ia_ms: Optional[float] = None
