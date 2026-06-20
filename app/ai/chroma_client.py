"""Cliente de ChromaDB para el vademécum farmacológico (RAG).

Colección `vademecum_medicamentos`: guarda por cada medicamento del catálogo su
texto descriptivo, el embedding y metadatos. Los embeddings se generan aparte
(ai/embeddings.py) y se pasan ya calculados.
"""
import chromadb
from app.core.config import settings

COLLECTION_NAME = "vademecum_medicamentos"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    return _client


def get_collection():
    # space=cosine -> distancia 0 = idéntico, ~2 = opuesto
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def upsert_medicamento(id_medicamento: int, texto: str, embedding: list[float], metadata: dict) -> None:
    get_collection().upsert(
        ids=[str(id_medicamento)],
        documents=[texto],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def delete_medicamento(id_medicamento: int) -> None:
    get_collection().delete(ids=[str(id_medicamento)])


def query_similar(embedding: list[float], n_results: int = 1) -> dict:
    """Devuelve los resultados más similares: {documents, metadatas, distances}."""
    return get_collection().query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def ping() -> bool:
    try:
        get_client().heartbeat()
        return True
    except Exception:
        return False
