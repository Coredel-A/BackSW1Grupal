"""Indexación y búsqueda del vademécum en ChromaDB (RAG, spec §13).

Todas las operaciones son tolerantes a fallos: si Ollama/ChromaDB no están
disponibles, se registra el error pero NO se rompe el flujo que las invoca
(p. ej. el CRUD del catálogo de medicamentos).
"""
import logging
from typing import Optional

from app.ai import embeddings, chroma_client

logger = logging.getLogger(__name__)

# Umbral de distancia coseno por encima del cual NO se considera confiable el resultado
UMBRAL_DISTANCIA = 0.6


def construir_texto(med) -> str:
    """Texto descriptivo enriquecido que se indexa por cada medicamento (spec §13)."""
    comercial = f" ({med.nombre_comercial})" if med.nombre_comercial else ""
    return (
        f"Medicamento: {med.nombre_generico}{comercial}\n"
        f"Grupo farmacológico: {med.grupo_farmacologico or 'no especificado'}\n"
        f"Presentación: {med.presentacion or 'no especificada'}\n"
        f"Vía de administración: {med.via_administracion or 'no especificada'}\n"
        f"Descripción: {med.descripcion or 'sin descripción'}"
    )


def indexar_medicamento(med) -> bool:
    """Construye el texto, genera el embedding y lo guarda/actualiza en ChromaDB."""
    try:
        texto = construir_texto(med)
        emb = embeddings.embed_text(texto)
        chroma_client.upsert_medicamento(
            med.id_medicamento,
            texto,
            emb,
            {
                "id_medicamento": str(med.id_medicamento),
                "nombre_generico": med.nombre_generico,
                "grupo_farmacologico": med.grupo_farmacologico or "",
            },
        )
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("No se pudo indexar el medicamento %s en ChromaDB: %s", med.id_medicamento, e)
        return False


def eliminar_medicamento(id_medicamento: int) -> bool:
    try:
        chroma_client.delete_medicamento(id_medicamento)
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("No se pudo eliminar el medicamento %s de ChromaDB: %s", id_medicamento, e)
        return False


def buscar_contexto(nombre_medicamento: str) -> Optional[str]:
    """Busca en el vademécum el texto más similar al nombre del medicamento (top 1).

    Devuelve None si no hay resultado confiable (distancia por encima del umbral).
    """
    try:
        emb = embeddings.embed_text(nombre_medicamento)
        res = chroma_client.query_similar(emb, n_results=1)
        docs = (res.get("documents") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        if docs and (not dists or dists[0] <= UMBRAL_DISTANCIA):
            return docs[0]
        return None
    except Exception as e:  # noqa: BLE001
        logger.warning("Búsqueda RAG fallida para '%s': %s", nombre_medicamento, e)
        return None
