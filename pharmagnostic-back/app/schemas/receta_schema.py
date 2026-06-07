from pydantic import BaseModel
from typing import List, Optional

# Esquema para recibir los medicamentos dentro de una receta
class MedicamentoPrescrito(BaseModel):
    id_medicamento: int
    dosis: str
    frecuencia: str
    duracion: str

# Esquema estándar de entrada cuando el médico da "Validar" en React
class RecetaValidacionIn(BaseModel):
    id_paciente: int
    id_usuario: int  # ID del Médico
    id_diagnostico: Optional[int] = None
    medicamentos: List[MedicamentoPrescrito]