from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.usuario import Usuario, Rol  # 💡 Importamos también el modelo Rol
from app.repositories.usuario_repo import UsuarioRepository
# 💡 Importamos UsuarioUpdate para la edición de datos
from app.schemas.usuario import UsuarioCreate, LoginRequest, TokenResponse, UsuarioUpdate

class UsuarioService:

    @staticmethod
    def registrar_usuario(db: Session, datos_usuario: UsuarioCreate) -> Usuario:
        """Valida duplicados, genera licencias institucionales, hashea el password y registra."""
        # 1. Verificar si el correo ya existe
        usuario_existente = UsuarioRepository.get_by_correo(db, datos_usuario.correo)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado."
            )
        
        # 2. Buscar el rol en la base de datos para saber su nombre real (médico, farmacéutico, etc.)
        rol_db = db.query(Rol).filter(Rol.id == datos_usuario.id_rol).first()
        if not rol_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="El rol seleccionado no existe en el sistema."
            )

        # 3. ✨ GENERACIÓN AUTOMÁTICA DE LICENCIA CLÍNICA
        licencia_autogenerada = None
        
        # Solo generamos número de licencia si el rol corresponde a personal operativo de salud
        if rol_db.nombre in ["medico", "farmaceutico"]:
            # Contamos cuántos usuarios existen con este rol para armar el correlativo
            conteo_usuarios = db.query(Usuario).filter(Usuario.id_rol == datos_usuario.id_rol).count()
            prefijo = "MED" if rol_db.nombre == "medico" else "FAR"
            
            # Formato automático resultante: MED-2026-001, MED-2026-002, etc.
            licencia_autogenerada = f"{prefijo}-2026-{str(conteo_usuarios + 1).zfill(3)}"

        # 4. Hashear la contraseña en texto plano
        password_hasheado = hash_password(datos_usuario.password)

        # 5. Mapear al Modelo de SQLAlchemy ORM inyectando la licencia calculada
        nuevo_usuario = Usuario(
            nombre=datos_usuario.nombre,
            apellido=datos_usuario.apellido,
            correo=datos_usuario.correo,
            hashed_password=password_hasheado,
            numero_licencia=licencia_autogenerada,  # 💻 ¡Asignado automáticamente aquí!
            id_rol=datos_usuario.id_rol
        )

        # 6. Guardar mediante el repositorio
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

        # 3. Preparar los datos del Payload que irán dentro del JWT
        payload_data = {
            "sub": str(usuario.id),
            "rol": usuario.rol.nombre
        }

        # 4. Crear el token firmado
        token_jwt = create_access_token(data=payload_data)

        return TokenResponse(access_token=token_jwt, token_type="bearer")

    # ✨ MÉTODO COMPLEMENTARIO: Actualización de datos (Requerimiento A-16)
    @staticmethod
    def actualizar_usuario(db: Session, db_obj: Usuario, obj_in: UsuarioUpdate) -> Usuario:
        """
        Modifica dinámicamente un usuario existente.
        Solo actualiza los campos enviados, protegiendo el resto (como las licencias o hashes).
        """
        # Convertimos el esquema de Pydantic a diccionario omitiendo campos no enviados (unset)
        update_data = obj_in.model_dump(exclude_unset=True)

        for campo in update_data:
            if hasattr(db_obj, campo):
                setattr(db_obj, campo, update_data[campo])

        # Persistimos y guardamos los cambios a través del repositorio
        UsuarioRepository.update(db)
        db.refresh(db_obj)
        return db_obj