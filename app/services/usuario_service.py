from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, LoginRequest, TokenResponse

class UsuarioService:

    @staticmethod
    def registrar_usuario(db: Session, datos_usuario: UsuarioCreate) -> Usuario:
        """Valida duplicados, hashea el password y registra al usuario."""
        # 1. Verificar si el correo ya existe
        usuario_existente = UsuarioRepository.get_by_correo(db, datos_usuario.correo)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado."
            )
        
        # 2. Hashear la contraseña en texto plano
        password_hasheado = hash_password(datos_usuario.password)

        # 3. Mapear el Schema de Pydantic al Modelo de SQLAlchemy ORM
        nuevo_usuario = Usuario(
            nombre=datos_usuario.nombre,
            apellido=datos_usuario.apellido,
            correo=datos_usuario.correo,
            hashed_password=password_hasheado,
            numero_licencia=datos_usuario.numero_licencia,
            id_rol=datos_usuario.id_rol
        )

        # 4. Guardar mediante el repositorio
        return UsuarioRepository.create(db, nuevo_usuario)

    @staticmethod
    def login_usuario(db: Session, credenciales: LoginRequest) -> TokenResponse:
        """Autentica las credenciales y genera un Token JWT."""
        # 1. Buscar que el usuario exista
        usuario = UsuarioRepository.get_by_correo(db, credenciales.correo)
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o usuario inactivo."
            )

        # 2. Verificar la contraseña cryptográficamente
        if not verify_password(credenciales.password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas."
            )

        # 3. Preparar los datos del Payload que irán dentro del JWT (sub indispensable)
        payload_data = {
            "sub": str(usuario.id),
            "rol": usuario.rol.nombre  # Gracias a SQLAlchemy accedemos directo sin JOINS
        }

        # 4. Crear el token firmado
        token_jwt = create_access_token(data=payload_data)

        return TokenResponse(access_token=token_jwt, token_type="bearer")