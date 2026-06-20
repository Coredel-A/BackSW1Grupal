from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DiagnosticoBase(BaseModel):
    codigo_cie10: Optional[str] = Field(None, max_length=10)
    descripcion: str = Field(..., min_length=1)
    tipo: Optional[str] = Field(None, max_length=50)  # preliminar, confirmado, diferencial
    observaciones: Optional[str] = None


class DiagnosticoCreate(DiagnosticoBase):
    id_paciente: int
    # id_usuario NO se recibe del body: se extrae del JWT en el backend.


class DiagnosticoUpdate(BaseModel):
    codigo_cie10: Optional[str] = Field(None, max_length=10)
    descripcion: Optional[str] = Field(None, min_length=1)
    tipo: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None


class DiagnosticoOut(DiagnosticoBase):
    id_diagnostico: int
    id_paciente: int
    id_usuario: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True
