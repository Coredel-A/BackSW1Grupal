"""Indexación masiva inicial del vademécum en ChromaDB.

Recorre todos los medicamentos ACTIVOS del catálogo y los (re)indexa en la
colección `vademecum_medicamentos`. Útil para sincronizar el catálogo existente
con el vector store (Sprint 2.2).

Uso: docker compose exec backend python reindex_vademecum.py
"""
from app.database.connection import SessionLocal
from app.repositories.medicamento_repo import MedicamentoRepository
from app.ai import vademecum


def main() -> None:
    db = SessionLocal()
    try:
        meds = MedicamentoRepository.search(db, solo_activos=True, limit=100000)
        ok = 0
        for m in meds:
            if vademecum.indexar_medicamento(m):
                ok += 1
        print(f"[reindex] Indexados {ok}/{len(meds)} medicamentos activos en ChromaDB.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
