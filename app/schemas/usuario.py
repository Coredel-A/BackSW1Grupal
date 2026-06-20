import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Validación de correo permisiva: a diferencia de EmailStr, acepta dominios internos
# del hospital como `@pharmagnostic.local` (la spec usa admin@pharmagnostic.local).
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --- ESQUEMAS DE ROL ---
class RolBase(BaseModel):
    nombre: str

class RolOut(RolBase):
    id_rol: int
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


# --- ESQUEMAS DE USUARIO ---

# Esquema base con los campos comunes
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: str = Field(..., max_length=150)
    numero_licencia: Optional[str] = Field(None, max_length=50)

    @field_validator("correo")
    @classmethod
    def validar_formato_correo(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("El formato del correo no es válido.")
        return v

# Datos requeridos para el registro (Solo Entrada)
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    id_rol: int
    # Obligatorio solo si el rol es paciente: CI de un paciente existente al que se vincula la cuenta.
    # El service lo resuelve a id_paciente_vinculado. (numero_licencia es obligatorio si médico/farmacéutico)
    ci_paciente: Optional[str] = Field(None, max_length=20)

# Datos permitidos para edición (Campos opcionales)
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    numero_licencia: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None

# Lo que se le devuelve al frontend (Salida segura - No expone contraseña)
class UsuarioOut(UsuarioBase):
    id_usuario: int
    activo: bool
    requiere_cambio_password: bool = False
    id_paciente_vinculado: Optional[int] = None
    rol: RolOut  # Mapea el objeto Rol completo (usuario.rol.nombre)

    class Config:
        from_attributes = True  # Permite a Pydantic leer modelos ORM de SQLAlchemy


# --- ESQUEMAS DE AUTENTICACIÓN ---

# Lo que envía el usuario al iniciar sesión (correo como simple credencial de búsqueda)
class LoginRequest(BaseModel):
    correo: str
    password: str

# Lo que responde el servidor si el login es exitoso
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Indica al frontend que debe forzar el cambio de contraseña antes de continuar
    requiere_cambio_password: bool = False

# Cambio de contraseña (usado en el primer login obligatorio o cuando el usuario lo solicite)
class CambioPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo: str = Field(..., min_length=8)
