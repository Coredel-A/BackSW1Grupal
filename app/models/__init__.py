"""Modelos ORM de PHARMAGNOSTIC AI.

Importar todos aquí asegura que queden registrados en ``Base.metadata`` para que
Alembic (autogenerate) los detecte y para poder hacer ``from app.models import Paciente``.
"""
from app.models.usuario import Rol, Usuario
from app.models.paciente import Paciente
from app.models.historial_clinico import HistorialClinico
from app.models.diagnostico import Diagnostico
from app.models.medicamento_catalogo import MedicamentoCatalogo
from app.models.receta import Receta
from app.models.receta_medicamento import RecetaMedicamento

__all__ = [
    "Rol",
    "Usuario",
    "Paciente",
    "HistorialClinico",
    "Diagnostico",
    "MedicamentoCatalogo",
    "Receta",
    "RecetaMedicamento",
]
