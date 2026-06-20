from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.farmacia import (
    VerificacionOut,
    DispensarRequest,
    RechazarRequest,
    DispensacionOut,
)
from app.services.dispensacion_service import DispensacionService

router = APIRouter(prefix="/farmacia", tags=["Farmacia"])

# La dispensación la realiza el farmacéutico; el administrador puede consultar.
farmaceutico_o_admin = RoleChecker(["farmaceutico", "administrador"])


@router.get("/verificar/{id_receta}", response_model=VerificacionOut)
def verificar(
    id_receta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(farmaceutico_o_admin),
):
    """Escanea/ingresa el código y verifica estado + integridad (blockchain) de la receta."""
    return DispensacionService.verificar(db, id_receta)


@router.post("/dispensar", response_model=DispensacionOut, status_code=status.HTTP_201_CREATED)
def dispensar(
    datos: DispensarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(farmaceutico_o_admin),
):
    """Confirma la dispensación (receta -> dispensada)."""
    return DispensacionService.dispensar(db, datos.id_receta, current_user.id_usuario)


@router.post("/rechazar", response_model=DispensacionOut, status_code=status.HTTP_201_CREATED)
def rechazar(
    datos: RechazarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(farmaceutico_o_admin),
):
    """Rechaza la dispensación con un motivo (la receta sigue validada)."""
    return DispensacionService.rechazar(db, datos.id_receta, current_user.id_usuario, datos.motivo)
