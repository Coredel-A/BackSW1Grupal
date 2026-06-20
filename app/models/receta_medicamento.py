from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base


class RecetaMedicamento(Base):
    """Tabla intermedia N:M entre receta y catálogo de medicamentos.

    Guarda los atributos específicos de cada medicamento en esa prescripción.
    """

    __tablename__ = "receta_medicamento"

    id_receta_med = Column(Integer, primary_key=True, index=True)
    id_receta = Column(Integer, ForeignKey("receta.id_receta"), nullable=False)
    id_medicamento = Column(Integer, ForeignKey("medicamento_catalogo.id_medicamento"), nullable=False)
    dosis = Column(String(50), nullable=False)
    frecuencia = Column(String(50), nullable=False)
    duracion = Column(String(50), nullable=False)
    via_administracion = Column(String(50), nullable=True)
    indicaciones = Column(Text, nullable=True)
    orden = Column(Integer, nullable=True)

    receta = relationship("Receta", back_populates="medicamentos")
    medicamento = relationship("MedicamentoCatalogo", back_populates="receta_medicamentos")
