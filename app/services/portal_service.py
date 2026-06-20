"""Portal del paciente: receta activa y chatbot restrictivo (spec §10)."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.receta import Receta
from app.repositories.receta_repo import RecetaRepository
from app.ai.ollama_client import ollama_disponible, invocar_chat

PROMPT_SISTEMA = """Eres un asistente para el paciente de un hospital. SOLO puedes ayudar con dudas
sobre la receta activa del paciente que se incluye como contexto.

Reglas estrictas:
- No das diagnósticos ni modificas el tratamiento.
- No accedes ni mencionas información de otros pacientes.
- Ante cualquier duda de salud o síntoma, indica SIEMPRE consultar a su médico.
- Si la pregunta no es sobre su receta actual, responde amablemente que solo puedes
  ayudar con su receta activa.
Responde en español, de forma breve y clara."""


class PortalService:

    @staticmethod
    def _receta_activa(db: Session, id_paciente: int):
        """Receta más reciente del paciente en estado validada o dispensada."""
        return (
            db.query(Receta)
            .filter(Receta.id_paciente == id_paciente, Receta.estado.in_(["validada", "dispensada"]))
            .order_by(Receta.fecha_emision.desc().nullslast(), Receta.fecha_creacion.desc())
            .first()
        )

    @staticmethod
    def obtener_receta_activa(db: Session, usuario: Usuario) -> dict:
        if not usuario.id_paciente_vinculado:
            return {
                "vinculado": False,
                "mensaje": "Tu cuenta aún no está vinculada a un expediente clínico. Consulta con el administrador del sistema.",
                "receta": None,
            }
        receta = PortalService._receta_activa(db, usuario.id_paciente_vinculado)
        if not receta:
            return {"vinculado": True, "mensaje": "No tienes recetas activas en este momento.", "receta": None}
        receta = RecetaRepository.get_by_id(db, receta.id_receta)  # carga medicamentos
        return {"vinculado": True, "mensaje": "Receta activa.", "receta": receta}

    @staticmethod
    def _contexto_receta(receta: Receta) -> str:
        if not receta:
            return "El paciente no tiene una receta activa."
        lineas = []
        if receta.diagnostico:
            lineas.append(f"Diagnóstico: {receta.diagnostico.descripcion}")
        lineas.append("Medicamentos recetados:")
        for rm in receta.medicamentos:
            nombre = rm.medicamento.nombre_generico if rm.medicamento else f"Medicamento {rm.id_medicamento}"
            lineas.append(f"- {nombre}: {rm.dosis}, {rm.frecuencia}, durante {rm.duracion}"
                          + (f" ({rm.indicaciones})" if rm.indicaciones else ""))
        return "\n".join(lineas)

    @staticmethod
    def chatbot(db: Session, usuario: Usuario, pregunta: str) -> str:
        if not usuario.id_paciente_vinculado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tu cuenta no está vinculada a un expediente clínico.",
            )
        if not ollama_disponible():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El asistente no está disponible en este momento.",
            )
        receta = PortalService._receta_activa(db, usuario.id_paciente_vinculado)
        if receta:
            receta = RecetaRepository.get_by_id(db, receta.id_receta)
        contexto = PortalService._contexto_receta(receta)

        prompt = (
            f"{PROMPT_SISTEMA}\n\n"
            f"RECETA ACTIVA DEL PACIENTE:\n{contexto}\n\n"
            f'PREGUNTA DEL PACIENTE: "{pregunta}"\n\nRespuesta:'
        )
        try:
            return invocar_chat(prompt).strip()
        except Exception:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="El asistente tardó demasiado en responder. Intenta de nuevo.",
            )
