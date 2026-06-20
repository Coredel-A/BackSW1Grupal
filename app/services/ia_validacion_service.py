"""Servicio orquestador de la validación farmacoterapéutica con IA (spec §8.4, §10, §12, §13).

Flujo: recolecta datos -> RAG por medicamento -> arma prompt -> invoca Llama 3 ->
parsea y valida JSON con Pydantic -> calcula nivel de riesgo -> guarda validación +
desglosa alertas individuales.
"""
import json
import logging
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.models.validacion_ia import ValidacionIA
from app.models.alerta_clinica import AlertaClinica
from app.repositories.receta_repo import RecetaRepository
from app.repositories.validacion_repo import ValidacionRepository
from app.schemas.validacion import IARespuesta
from app.ai import vademecum, prompt_builder
from app.ai.ollama_client import ollama_disponible, invocar_llm
from app.core.config import settings

logger = logging.getLogger(__name__)


class IAValidacionService:

    @staticmethod
    def _nivel_final(ia: IARespuesta) -> int:
        """El nivel final es el más alto entre el global y todos los hallazgos."""
        niveles = [ia.nivel_riesgo]
        niveles += [x.nivel for x in ia.interacciones]
        niveles += [x.nivel for x in ia.contraindicaciones]
        niveles += [x.nivel for x in ia.duplicidades]
        niveles += [x.nivel for x in ia.errores_dosis]
        return max(niveles) if niveles else 0

    @staticmethod
    def _construir_alertas(ia: IARespuesta, id_receta: int) -> list[AlertaClinica]:
        alertas: list[AlertaClinica] = []
        for it in ia.interacciones:
            alertas.append(AlertaClinica(
                id_receta=id_receta, tipo_alerta="interaccion", nivel=it.nivel,
                descripcion=f"{' + '.join(it.medicamentos)}: {it.descripcion}",
            ))
        for c in ia.contraindicaciones:
            alertas.append(AlertaClinica(
                id_receta=id_receta, tipo_alerta="contraindicacion", nivel=c.nivel,
                descripcion=f"{c.medicamento}: {c.motivo}",
            ))
        for d in ia.duplicidades:
            alertas.append(AlertaClinica(
                id_receta=id_receta, tipo_alerta="duplicidad", nivel=d.nivel,
                descripcion=f"{' + '.join(d.medicamentos)}: {d.descripcion}",
            ))
        for e in ia.errores_dosis:
            alertas.append(AlertaClinica(
                id_receta=id_receta, tipo_alerta="dosis", nivel=e.nivel,
                descripcion=f"{e.medicamento}: {e.descripcion}",
            ))
        if ia.coherencia_audio and ia.coherencia_audio.evaluado:
            alertas.append(AlertaClinica(
                id_receta=id_receta, tipo_alerta="coherencia_audio", nivel=0,
                descripcion=(
                    f"Coherencia audio {ia.coherencia_audio.porcentaje_coherencia}%: "
                    f"{ia.coherencia_audio.observaciones}"
                ),
            ))
        return alertas

    @staticmethod
    def _invocar_y_parsear(prompt: str) -> tuple[IARespuesta, int]:
        """Invoca el LLM, mide el tiempo y valida la estructura. Reintenta una vez si falla el parseo."""
        for intento in (1, 2):
            t0 = time.perf_counter()
            try:
                raw = invocar_llm(prompt)
            except Exception as e:  # noqa: BLE001
                logger.error("Fallo al invocar el LLM: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="El servicio de IA no respondió a tiempo. Intenta nuevamente.",
                )
            ms = int((time.perf_counter() - t0) * 1000)
            try:
                return IARespuesta.model_validate_json(raw), ms
            except (ValidationError, ValueError) as e:
                logger.warning("Respuesta IA no parseable (intento %s): %s", intento, e)
                continue
        # Si tras 2 intentos no se pudo parsear, no se guarda nada corrupto
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La IA devolvió una respuesta no válida. La validación no se guardó; reintenta.",
        )

    @staticmethod
    def ejecutar_validacion(db: Session, id_receta: int) -> ValidacionIA:
        receta = RecetaRepository.get_by_id(db, id_receta)
        if not receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")
        if not receta.medicamentos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La receta no tiene medicamentos para validar.",
            )

        # 1. Disponibilidad de Ollama (no dejar la petición colgada)
        if not ollama_disponible():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de IA (Ollama) no está disponible en este momento.",
            )

        # 2. Datos de medicamentos + RAG por cada uno (uno por uno)
        medicamentos = []
        rag_contextos = []
        for rm in receta.medicamentos:
            nombre = rm.medicamento.nombre_generico if rm.medicamento else f"Medicamento {rm.id_medicamento}"
            medicamentos.append({
                "nombre": nombre,
                "dosis": rm.dosis,
                "via": rm.via_administracion,
                "frecuencia": rm.frecuencia,
                "duracion": rm.duracion,
            })
            rag_contextos.append({"nombre": nombre, "texto": vademecum.buscar_contexto(nombre)})

        # 3. Audio (opcional)
        audio = ValidacionRepository.get_ultimo_audio_completado(db, id_receta)
        transcripcion = audio.transcripcion if audio else None

        # 4. Prompt + invocación + parseo validado
        prompt = prompt_builder.construir_prompt(
            receta.paciente, receta.diagnostico, medicamentos, rag_contextos, transcripcion
        )
        ia, ms = IAValidacionService._invocar_y_parsear(prompt)

        # 5. Nivel final + coherencia
        nivel_final = IAValidacionService._nivel_final(ia)
        coherencia = (
            ia.coherencia_audio.porcentaje_coherencia
            if (ia.coherencia_audio and ia.coherencia_audio.evaluado)
            else None
        )

        # 6. Guardar validación
        validacion = ValidacionIA(
            id_receta=id_receta,
            id_audio=audio.id_audio if audio else None,
            nivel_riesgo=nivel_final,
            justificacion=ia.justificacion_general,
            interacciones=json.dumps([x.model_dump() for x in ia.interacciones], ensure_ascii=False),
            contraindicaciones=json.dumps([x.model_dump() for x in ia.contraindicaciones], ensure_ascii=False),
            duplicidades=json.dumps([x.model_dump() for x in ia.duplicidades], ensure_ascii=False),
            errores_dosis=json.dumps([x.model_dump() for x in ia.errores_dosis], ensure_ascii=False),
            coherencia_audio=coherencia,
            modelo_usado=settings.LLM_MODEL,
            tiempo_respuesta_ms=ms,
        )
        validacion = ValidacionRepository.create(db, validacion)

        # 7. Desglosar alertas individuales
        alertas = IAValidacionService._construir_alertas(ia, id_receta)
        for a in alertas:
            a.id_validacion = validacion.id_validacion
        if alertas:
            ValidacionRepository.add_alertas(db, alertas)

        # 8. Reflejar el riesgo en la receta (sigue en borrador; la emisión es Sprint 3)
        receta.nivel_riesgo = nivel_final
        receta.resumen_validacion = ia.justificacion_general
        db.commit()

        return ValidacionRepository.get_by_id(db, validacion.id_validacion)

    @staticmethod
    def historial_por_receta(db: Session, id_receta: int) -> list[ValidacionIA]:
        return ValidacionRepository.get_by_receta(db, id_receta)
