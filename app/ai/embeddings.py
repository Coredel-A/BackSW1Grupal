"""Generación de embeddings con un modelo local vía Ollama (LangChain)."""
from langchain_ollama import OllamaEmbeddings
from app.core.config import settings

_embeddings = None


def _get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
    return _embeddings


def embed_text(texto: str) -> list[float]:
    """Devuelve el vector embedding de un texto."""
    return _get_embeddings().embed_query(texto)
