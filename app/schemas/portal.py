from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.receta import RecetaOut


class RecetaActivaOut(BaseModel):
    vinculado: bool
    mensaje: str
    receta: Optional[RecetaOut] = None


class ChatRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    respuesta: str
