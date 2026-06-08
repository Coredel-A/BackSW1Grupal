from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.usuario import LoginRequest, TokenResponse
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