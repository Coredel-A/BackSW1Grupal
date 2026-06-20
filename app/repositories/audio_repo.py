from typing import Optional
from sqlalchemy.orm import Session

from app.models.audio_clinico import AudioClinico


class AudioRepository:

    @staticmethod
    def create(db: Session, audio: AudioClinico) -> AudioClinico:
        db.add(audio)
        db.commit()
        db.refresh(audio)
        return audio

    @staticmethod
    def get_by_id(db: Session, id_audio: int) -> Optional[AudioClinico]:
        return db.query(AudioClinico).filter(AudioClinico.id_audio == id_audio).first()

    @staticmethod
    def update(db: Session) -> None:
        db.commit()
