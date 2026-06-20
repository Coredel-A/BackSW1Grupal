"""Audio clínico: guardado del archivo y transcripción con Faster-Whisper (CPU).

El endpoint responde de inmediato con estado 'procesando' y la transcripción se
ejecuta en segundo plano (BackgroundTasks), actualizando el registro al terminar.
"""
import logging
import os

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.audio_clinico import AudioClinico
from app.repositories.audio_repo import AudioRepository
from app.repositories.receta_repo import RecetaRepository
from app.database.connection import SessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)

# Modelo Whisper cargado de forma perezosa y cacheado (se descarga la 1ª vez)
_whisper_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        logger.info("Cargando modelo Whisper '%s' (CPU/int8)…", settings.WHISPER_MODEL)
        _whisper_model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper_model


class AudioService:

    @staticmethod
    def guardar_audio(db: Session, id_receta: int, id_usuario: int, archivo: UploadFile) -> AudioClinico:
        if not RecetaRepository.get_by_id(db, id_receta):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")

        os.makedirs(settings.AUDIO_DIR, exist_ok=True)
        ext = (os.path.splitext(archivo.filename or "")[1] or ".webm").lstrip(".")

        # 1. Crear el registro (estado procesando) para obtener el id
        audio = AudioClinico(
            id_receta=id_receta,
            id_usuario=id_usuario,
            ruta_archivo="",
            formato=ext,
            estado_procesamiento="procesando",
        )
        audio = AudioRepository.create(db, audio)

        # 2. Guardar el archivo en disco usando el id
        ruta = os.path.join(settings.AUDIO_DIR, f"audio_{audio.id_audio}.{ext}")
        try:
            with open(ruta, "wb") as f:
                f.write(archivo.file.read())
        except Exception as e:  # noqa: BLE001
            audio.estado_procesamiento = "error"
            AudioRepository.update(db)
            raise HTTPException(status_code=500, detail=f"No se pudo guardar el audio: {e}")

        audio.ruta_archivo = ruta
        AudioRepository.update(db)
        return audio

    @staticmethod
    def transcribir_en_background(id_audio: int) -> None:
        """Se ejecuta en segundo plano: abre su propia sesión de BD y transcribe."""
        db = SessionLocal()
        try:
            audio = AudioRepository.get_by_id(db, id_audio)
            if not audio:
                return
            try:
                modelo = _get_whisper()
                segmentos, info = modelo.transcribe(audio.ruta_archivo, language="es")
                texto = " ".join(seg.text.strip() for seg in segmentos).strip()
                audio.transcripcion = texto
                audio.duracion_segundos = int(getattr(info, "duration", 0) or 0)
                audio.estado_procesamiento = "completado"
            except Exception as e:  # noqa: BLE001
                logger.error("Error transcribiendo audio %s: %s", id_audio, e)
                audio.estado_procesamiento = "error"
            AudioRepository.update(db)
        finally:
            db.close()

    @staticmethod
    def obtener_audio(db: Session, id_audio: int) -> AudioClinico:
        audio = AudioRepository.get_by_id(db, id_audio)
        if not audio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio no encontrado.")
        return audio
