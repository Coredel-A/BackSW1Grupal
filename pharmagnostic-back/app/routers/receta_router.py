from fastapi import APIRouter, HTTPException, status
from app.schemas.receta_schema import RecetaValidacionIn
from app.services.ia_service import IAService

router = APIRouter(
    prefix="/recetas",
    tags=["Recetas & Validación IA"]
)

# Instanciamos el servicio (Capa de negocio)
ia_service = IAService()

@router.post("/validar", status_code=status.HTTP_200_OK)
async def validar_receta_medica(payload: RecetaValidacionIn):
    try:
        # Pasamos la pelota a la capa de servicios
        resultado = await ia_service.procesar_validacion_clinica(payload)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el motor de IA local: {str(e)}"
        )