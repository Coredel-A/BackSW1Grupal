from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.medicamento import MedicamentoOut


# --- RECETA_MEDICAMENTO (ítems de la receta) ---
class RecetaMedicamentoBase(BaseModel):
    id_medicamento: int
    dosis: str = Field(..., min_length=1, max_length=50)
    frecuencia: str = Field(..., min_length=1, max_length=50)
    duracion: str = Field(..., min_length=1, max_length=50)
    via_administracion: Optional[str] = Field(None, max_length=50)
    indicaciones: Optional[str] = None
    orden: Optional[int] = None


class RecetaMedicamentoCreate(RecetaMedicamentoBase):
    pass


class RecetaMedicamentoUpdate(BaseModel):
    dosis: Optional[str] = Field(None, max_length=50)
    frecuencia: Optional[str] = Field(None, max_length=50)
    duracion: Optional[str] = Field(None, max_length=50)
    via_administracion: Optional[str] = Field(None, max_length=50)
    indicaciones: Optional[str] = None
    orden: Optional[int] = None


class RecetaMedicamentoOut(RecetaMedicamentoBase):
    id_receta_med: int
    id_receta: int
    medicamento: Optional[MedicamentoOut] = None  # datos del catálogo para mostrar

    class Config:
        from_attributes = True


# --- RECETA ---
class RecetaCreate(BaseModel):
    id_paciente: int
    id_diagnostico: Optional[int] = None
    observaciones: Optional[str] = None
    # Opcional: crear la receta ya con su lista de medicamentos en una sola petición.
    medicamentos: Optional[List[RecetaMedicamentoCreate]] = None


class RecetaUpdate(BaseModel):
    id_diagnostico: Optional[int] = None
    observaciones: Optional[str] = None


class RecetaOut(BaseModel):
    id_receta: int
    id_paciente: int
    id_usuario: int
    id_diagnostico: Optional[int] = None
    estado: str
    nivel_riesgo: Optional[int] = None
    resumen_validacion: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_emision: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    medicamentos: List[RecetaMedicamentoOut] = []

    class Config:
        from_attributes = True
