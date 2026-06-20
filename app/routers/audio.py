from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, RoleChecker
from app.models.usuario import Usuario
from app.schemas.audio import AudioOut
from app.services.audio_service import AudioService

router = APIRouter(prefix="/audio", tags=["Audio Clínico"])

medico_o_admin = RoleChecker(["medico", "administrador"])


@router.post("/recetas/{id_receta}", response_model=AudioOut, status_code=status.HTTP_201_CREATED)
def subir_audio(
    id_receta: int,
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(medico_o_admin),
):
    """Recibe el dictado, responde 'procesando' y transcribe en segundo plano."""
    audio = AudioService.guardar_audio(db, id_receta, current_user.id_usuario, archivo)
    background_tasks.add_task(AudioService.transcribir_en_background, audio.id_audio)
    return audio


@router.get("/{id_audio}", response_model=AudioOut)
def estado_audio(
    id_audio: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(medico_o_admin),
):
    """Consulta el estado y la transcripción de un audio (para el polling del frontend)."""
    return AudioService.obtener_audio(db, id_audio)
