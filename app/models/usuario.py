from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.connection import Base  # Tu Base declarativa de SQLAlchemy

class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)

    # Relación inversa: Un rol puede tener muchos usuarios
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    numero_licencia = Column(String(50), nullable=True, unique=True)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Clave foránea hacia la tabla de roles
    id_rol = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # Relación para acceder directo a `usuario.rol.nombre` sin JOINS manuales
    rol = relationship("Rol", back_populates="usuarios")