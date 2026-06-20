from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.portal import RecetaActivaOut, ChatRequest, ChatResponse
from app.services.portal_service import PortalService

router = APIRouter(prefix="/paciente", tags=["Portal del Paciente"])

es_paciente = RoleChecker(["paciente"])


@router.get("/receta-activa", response_model=RecetaActivaOut)
def receta_activa(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(es_paciente),
):
    """Receta activa más reciente del paciente autenticado (validada o dispensada)."""
    return PortalService.obtener_receta_activa(db, current_user)


@router.post("/chatbot", response_model=ChatResponse)
def chatbot(
    datos: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(es_paciente),
):
    """Chatbot restringido al contexto de la receta activa del paciente."""
    respuesta = PortalService.chatbot(db, current_user, datos.pregunta)
    return ChatResponse(respuesta=respuesta)
