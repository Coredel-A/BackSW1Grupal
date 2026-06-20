from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.usuario import Usuario, Rol
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.paciente_repo import PacienteRepository
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    LoginRequest,
    TokenResponse,
    CambioPasswordRequest,
)

# Roles que exigen número de licencia profesional (spec 7.1)
ROLES_CON_LICENCIA = {"medico", "farmaceutico"}


class UsuarioService:

    @staticmethod
    def registrar_usuario(db: Session, datos_usuario: UsuarioCreate) -> Usuario:
        """Valida duplicados y requisitos por rol, hashea el password y registra."""
        # 1. Verificar si el correo ya existe (409 Conflicto)
        if UsuarioRepository.get_by_correo(db, datos_usuario.correo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya se encuentra registrado.",
            )

        # 2. Verificar que el rol exista
        rol_db = db.query(Rol).filter(Rol.id_rol == datos_usuario.id_rol).first()
        if not rol_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol seleccionado no existe en el sistema.",
            )

        # 3. Validaciones por rol (spec 7.1)
        numero_licencia = None
        id_paciente_vinculado = None

        if rol_db.nombre in ROLES_CON_LICENCIA:
            if not datos_usuario.numero_licencia:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El número de licencia es obligatorio para médicos y farmacéuticos.",
                )
            numero_licencia = datos_usuario.numero_licencia

        elif rol_db.nombre == "paciente":
            if not datos_usuario.ci_paciente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debes vincular la cuenta a un paciente existente mediante su CI.",
                )
            paciente = PacienteRepository.get_by_ci(db, datos_usuario.ci_paciente)
            if not paciente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existe un paciente registrado con ese CI.",
                )
            id_paciente_vinculado = paciente.id_paciente

        # 4. Hashear la contraseña y construir el modelo ORM
        nuevo_usuario = Usuario(
            nombre=datos_usuario.nombre,
            apellido=datos_usuario.apellido,
            correo=datos_usuario.correo,
            contrasena_hash=hash_password(datos_usuario.password),
            numero_licencia=numero_licencia,
            id_paciente_vinculado=id_paciente_vinculado,
            id_rol=datos_usuario.id_rol,
        )

        # 5. Guardar mediante el repositorio
        return UsuarioRepository.create(db, nuevo_usuario)

    @staticmethod
    def login_usuario(db: Session, credenciales: LoginRequest) -> TokenResponse:
        """Autentica las credenciales y genera un Token JWT."""
        usuario = UsuarioRepository.get_by_correo(db, credenciales.correo)
        # Usuario inexistente o desactivado -> 401 (aunque las credenciales sean correctas)
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o usuario inactivo.",
            )

        if not verify_password(credenciales.password, usuario.contrasena_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas.",
            )

        # El id del usuario que actúa siempre se extrae del token en el backend
        payload_data = {"sub": str(usuario.id_usuario), "rol": usuario.rol.nombre}
        token_jwt = create_access_token(data=payload_data)

        return TokenResponse(
            access_token=token_jwt,
            token_type="bearer",
            requiere_cambio_password=usuario.requiere_cambio_password,
        )

    @staticmethod
    def actualizar_usuario(db: Session, db_obj: Usuario, obj_in: UsuarioUpdate) -> Usuario:
        """Modifica dinámicamente un usuario existente (solo los campos enviados)."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for campo in update_data:
            if hasattr(db_obj, campo):
                setattr(db_obj, campo, update_data[campo])

        UsuarioRepository.update(db)
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def cambiar_password(db: Session, usuario: Usuario, datos: CambioPasswordRequest) -> Usuario:
        """Cambia la contraseña del usuario autenticado y limpia el flag de cambio forzado."""
        if not verify_password(datos.password_actual, usuario.contrasena_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta.",
            )

        usuario.contrasena_hash = hash_password(datos.password_nuevo)
        usuario.requiere_cambio_password = False
        UsuarioRepository.update(db)
        db.refresh(usuario)
        return usuario
