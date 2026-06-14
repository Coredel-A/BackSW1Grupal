from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user, RoleChecker
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate, RolOut
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repo import UsuarioRepository
from app.models.usuario import Usuario, Rol

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])

# Instanciamos los verificadores de roles basados en tu requerimiento A-11
es_admin = RoleChecker(["administrador"])

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(es_admin)])
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario en el sistema. (Solo Administradores)."""
    return UsuarioService.registrar_usuario(db, usuario_in)

@router.get("/", response_model=List[UsuarioOut], dependencies=[Depends(es_admin)])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos los usuarios con paginación. (Solo Administradores)."""
    return UsuarioRepository.get_all(db, skip=skip, limit=limit)

@router.get("/roles", response_model=List[RolOut], dependencies=[Depends(es_admin)])
def obtener_todos_los_roles(db: Session = Depends(get_db)):
    """Obtiene la lista completa de roles institucionales registrados."""
    roles = db.query(Rol).all()
    return roles

@router.get("/{id}", response_model=UsuarioOut)
def obtener_usuario_por_id(id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Obtiene el perfil de un usuario. (Administradores o el propio usuario)."""
    if current_user.rol.nombre != "administrador" and current_user.id != id:
        raise HTTPException(status_code=403, detail="No tienes autorización para ver perfiles ajenos.")
    
    usuario = UsuarioRepository.get_by_id(db, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario

@router.patch("/{id}/estado", response_model=UsuarioOut, dependencies=[Depends(es_admin)])
def cambiar_estado_usuario(id: int, db: Session = Depends(get_db)):
    """Habilita o deshabilita la cuenta de un usuario de forma lógica. (Solo Administradores)."""
    usuario = UsuarioRepository.get_by_id(db, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return UsuarioRepository.toggle_activo(db, usuario)

@router.put("/{id}", response_model=UsuarioOut, dependencies=[Depends(es_admin)])
def actualizar_usuario(id: int, usuario_in: UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualiza los datos del personal clínico (Nombre, Apellido, Licencia o Rol). (Solo Administradores)."""
    # 1. Buscamos el registro a través del repositorio
    usuario = UsuarioRepository.get_by_id(db, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en los registros.")
    
    # 2. Invocamos al service para procesar los cambios de la lógica de negocio
    return UsuarioService.actualizar_usuario(db, db_obj=usuario, obj_in=usuario_in)