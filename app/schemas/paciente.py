from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- PACIENTE ---
class PacienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    fecha_nacimiento: date
    sexo: Optional[str] = Field(None, max_length=10)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=150)
    funcion_renal: Optional[str] = Field(None, max_length=50)      # normal, leve, moderada, severa
    funcion_hepatica: Optional[str] = Field(None, max_length=50)   # normal, leve, moderada, severa
    peso_kg: Optional[float] = None
    alergias: Optional[str] = None
    observaciones: Optional[str] = None


class PacienteCreate(PacienteBase):
    ci: str = Field(..., min_length=1, max_length=20)  # único e inmutable tras el registro


class PacienteUpdate(BaseModel):
    # El CI NO se incluye: es inmutable una vez registrado.
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = Field(None, max_length=10)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=150)
    funcion_renal: Optional[str] = Field(None, max_length=50)
    funcion_hepatica: Optional[str] = Field(None, max_length=50)
    peso_kg: Optional[float] = None
    alergias: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class PacienteOut(PacienteBase):
    id_paciente: int
    ci: str
    activo: bool
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- HISTORIAL CLÍNICO ---
class HistorialClinicoCreate(BaseModel):
    descripcion: str = Field(..., min_length=1)
    # internacion, alergia_nueva, evento_adverso, cirugia, antecedente, otro
    tipo_evento: Optional[str] = Field(None, max_length=100)


class HistorialClinicoOut(BaseModel):
    id_historial: int
    id_paciente: int
    id_usuario: int
    descripcion: str
    tipo_evento: Optional[str] = None
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True
