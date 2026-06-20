from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database.connection import Base  # Base declarativa de SQLAlchemy


class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)

    # Relación inversa: un rol puede tener muchos usuarios
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    contrasena_hash = Column(String(255), nullable=False)
    # Obligatorio (validado en el service) si el rol es medico o farmaceutico
    numero_licencia = Column(String(50), nullable=True, unique=True)
    # Obligatorio (validado en el service) si el rol es paciente -> conecta la cuenta con su expediente
    id_paciente_vinculado = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=True)
    # Fuerza el cambio de contraseña en el primer ingreso (admin sembrado lo trae en True)
    requiere_cambio_password = Column(Boolean, default=False, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación para acceder directo a `usuario.rol.nombre` sin JOINs manuales
    rol = relationship("Rol", back_populates="usuarios")
    paciente_vinculado = relationship("Paciente", foreign_keys=[id_paciente_vinculado])
