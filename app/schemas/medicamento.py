from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MedicamentoBase(BaseModel):
    nombre_generico: str = Field(..., min_length=1, max_length=150)
    nombre_comercial: Optional[str] = Field(None, max_length=150)
    grupo_farmacologico: Optional[str] = Field(None, max_length=100)
    presentacion: Optional[str] = Field(None, max_length=100)
    concentracion: Optional[str] = Field(None, max_length=50)
    via_administracion: Optional[str] = Field(None, max_length=50)
    # Texto extenso (contraindicaciones, interacciones, ajustes renales/hepáticos) -> insumo RAG.
    descripcion: Optional[str] = None


class MedicamentoCreate(MedicamentoBase):
    pass


class MedicamentoUpdate(BaseModel):
    nombre_generico: Optional[str] = Field(None, min_length=1, max_length=150)
    nombre_comercial: Optional[str] = Field(None, max_length=150)
    grupo_farmacologico: Optional[str] = Field(None, max_length=100)
    presentacion: Optional[str] = Field(None, max_length=100)
    concentracion: Optional[str] = Field(None, max_length=50)
    via_administracion: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class MedicamentoOut(MedicamentoBase):
    id_medicamento: int
    activo: bool
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True
