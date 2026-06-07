from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.receta_schema import RecetaValidacionIn
from app.database.connection import get_db
from app.services.ia_service import IAService

router = APIRouter(
    prefix="/recetas",
    tags=["Recetas & Validación IA"]
)

ia_service = IAService()

# NUEVO ENDPOINT: Para verificar si el back se comunica con PostgreSQL
@router.get("/test-db", status_code=status.HTTP_200_OK)
def verificar_conexion_db(db: Session = Depends(get_db)):
    try:
        # Ejecutamos una consulta nativa rápida de control
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Conexión a PostgreSQL establecida correctamente."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con la base de datos: {str(e)}"
        )

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