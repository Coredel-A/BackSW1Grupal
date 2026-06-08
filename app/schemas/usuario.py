from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# --- ESQUEMAS DE ROL ---
class RolBase(BaseModel):
    nombre: str

class RolOut(RolBase):
    id: int
    
    class Config:
        from_attributes = True


# --- ESQUEMAS DE USUARIO ---

# Esquema base con los campos comunes
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr  # Valida automáticamente formato de email (ejemplo@dominio.com)
    numero_licencia: Optional[str] = Field(None, max_length=50)

# Datos requeridos estrictamente para el registro (Solo Entrada)
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    id_rol: int

# Datos permitidos para edición (Campos opcionales)
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    numero_licencia: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None

# Lo que se le devuelve al frontend (Salida segura - No expone contraseña)
class UsuarioOut(UsuarioBase):
    id: int
    activo: bool
    rol: RolOut  # Esto permite mapear el objeto Rol completo (usuario.rol.nombre)

    class Config:
        from_attributes = True  # Permite a Pydantic leer modelos ORM de SQLAlchemy


# --- ESQUEMAS DE AUTENTICACIÓN ---

# Lo que envía el usuario al iniciar sesión
class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

# Lo que responde el servidor si el login es exitoso
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"