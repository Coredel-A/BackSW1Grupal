from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.receta_schema import RecetaValidacionIn
from app.database.connection import get_db
from app.services.ia_service import IAService
from app.models.usuario import Rol, Usuario  # Importamos ambos modelos
from app.core.security import hash_password

router = APIRouter(
    prefix="/recetas",
    tags=["Recetas & Validación IA"]
)

ia_service = IAService()

@router.get("/recetas/test-db")
def verificar_conexion_db(db: Session = Depends(get_db)):
    # 1. Crear los roles básicos si no existen
    if not db.query(Rol).filter(Rol.nombre == "administrador").first():
        admin_role = Rol(id=1, nombre="administrador")
        farmaceutico_role = Rol(id=2, nombre="farmaceutico")
        db.add_all([admin_role, farmaceutico_role])
        db.commit()

    # 2. Crear el Usuario Administrador por defecto si no existe
    usuario_existente = db.query(Usuario).filter(Usuario.correo == "admin@pharmagnostic.com").first()
    if not usuario_existente:
        admin_user = Usuario(
            nombre="Admin",
            apellido="Sistema",
            correo="admin@pharmagnostic.com",
            hashed_password=hash_password("admin123456"),  # Contraseña inicial por defecto
            numero_licencia="ADMIN-001",
            id_rol=1,  # ID del rol administrador creado arriba
            activo=True
        )
        db.add(admin_user)
        db.commit()
        return {
            "status": "Base de datos inicializada",
            "usuario_creado": "admin@pharmagnostic.com",
            "password_por_defecto": "admin123456",
            "detalle": "Roles y administrador listos para usar."
        }
        
    return {"status": "Conexión OK", "detalle": "El usuario administrador ya existe en la DB."}

@router.post("/validar", status_code=status.HTTP_200_OK)
async def validar_receta_medica(payload: RecetaValidacionIn, db: Session = Depends(get_db)):
    try:
        # En el futuro, ia_service usará 'db' para consultar el catálogo o guardar la receta
        resultado = await ia_service.procesar_validacion_clinica(payload)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el motor de IA local: {str(e)}"
        )