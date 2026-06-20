from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class MedicamentoCatalogo(Base):
    __tablename__ = "medicamento_catalogo"

    id_medicamento = Column(Integer, primary_key=True, index=True)
    nombre_generico = Column(String(150), nullable=False)
    nombre_comercial = Column(String(150), nullable=True)
    grupo_farmacologico = Column(String(100), nullable=True)
    presentacion = Column(String(100), nullable=True)
    concentracion = Column(String(50), nullable=True)
    via_administracion = Column(String(50), nullable=True)
    # Texto extenso con contraindicaciones, interacciones y ajustes renales/hepáticos.
    # Insumo del RAG (indexación en ChromaDB se implementa en el Sprint 2).
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    receta_medicamentos = relationship("RecetaMedicamento", back_populates="medicamento")
