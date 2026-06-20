from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import (
    LoginRequest,
    TokenResponse,
    CambioPasswordRequest,
    UsuarioOut,
)
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint público para iniciar sesión y obtener el JWT."""
    return UsuarioService.login_usuario(db, credenciales)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """Endpoint de salida para consistencia académica (el front limpia el token local)."""
    return {"detail": "Sesión cerrada correctamente de forma local."}


@router.get("/me", response_model=UsuarioOut)
def perfil_actual(current_user: Usuario = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado (incluye requiere_cambio_password)."""
    return current_user


@router.post("/cambiar-password", response_model=UsuarioOut)
def cambiar_password(
    datos: CambioPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cambia la contraseña del usuario autenticado (usado en el cambio forzado de primer login)."""
    return UsuarioService.cambiar_password(db, current_user, datos)
