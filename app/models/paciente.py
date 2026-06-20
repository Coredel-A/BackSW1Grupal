from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False, index=True)  # único e inmutable
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(10), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(150), nullable=True)
    funcion_renal = Column(String(50), nullable=True)      # normal, leve, moderada, severa
    funcion_hepatica = Column(String(50), nullable=True)   # normal, leve, moderada, severa
    peso_kg = Column(Numeric(5, 2), nullable=True)
    alergias = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True, nullable=False)

    historiales = relationship("HistorialClinico", back_populates="paciente")
    diagnosticos = relationship("Diagnostico", back_populates="paciente")
    recetas = relationship("Receta", back_populates="paciente")
