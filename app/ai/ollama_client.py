"""Invocación al LLM local (Llama 3) vía LangChain + health-check de Ollama."""
import httpx
from langchain_ollama import OllamaLLM
from app.core.config import settings


def ollama_disponible() -> bool:
    """Verifica que el servicio Ollama responda antes de intentar una validación."""
    try:
        r = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/version", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False


def invocar_llm(prompt: str, timeout: int | None = None) -> str:
    """Invoca a Llama 3 forzando salida JSON. Devuelve el texto (string JSON) crudo.

    Lanza excepción si Ollama no responde dentro del timeout configurado.
    """
    timeout = timeout or settings.LLM_TIMEOUT_SECONDS
    llm = OllamaLLM(
        model=settings.LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        format="json",      # fuerza al modelo a responder JSON válido
        temperature=0,      # determinista, sin creatividad
        client_kwargs={"timeout": timeout},
    )
    return llm.invoke(prompt)
