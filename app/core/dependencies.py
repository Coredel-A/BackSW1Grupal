from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal  # Tu generador de sesiones local
from app.core.config import settings
from app.core.security import SECRET_KEY, ALGORITHM
from app.repositories.usuario_repo import UsuarioRepository
from app.models.usuario import Usuario

# Indica a FastAPI de dónde extraer el token en las peticiones HTTP Header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    """Generador de sesión de Base de Datos para inyectar en los endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Valida el JWT y retorna el usuario autenticado actual."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el token cryptográficamente
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Buscar el usuario dueño del token en la base de datos
    usuario = UsuarioRepository.get_by_id(db, usuario_id=int(usuario_id))
    if usuario is None or not usuario.activo:
        raise credentials_exception
        
    return usuario

class RoleChecker:
    """Verificador Dinámico de Roles para autorizar accesos (A-11)."""
    def __init__(self, roles_permitidos: list[str]):
        self.roles_permitidos = roles_permitidos

    def __call__(self, current_user: Usuario = Depends(get_current_user)):
        if current_user.rol.nombre not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes los permisos necesarios para realizar esta acción."
            )
        return current_user