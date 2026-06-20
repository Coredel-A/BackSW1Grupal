from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.medicamento_catalogo import MedicamentoCatalogo
from app.repositories.medicamento_repo import MedicamentoRepository
from app.schemas.medicamento import MedicamentoCreate, MedicamentoUpdate


class MedicamentoService:

    @staticmethod
    def crear_medicamento(db: Session, datos: MedicamentoCreate) -> MedicamentoCatalogo:
        nuevo = MedicamentoCatalogo(**datos.model_dump())
        medicamento = MedicamentoRepository.create(db, nuevo)
        # TODO Sprint 2: construir texto descriptivo e indexar en ChromaDB (colección vademecum_medicamentos)
        return medicamento

    @staticmethod
    def obtener_medicamento(db: Session, id_medicamento: int) -> MedicamentoCatalogo:
        medicamento = MedicamentoRepository.get_by_id(db, id_medicamento)
        if not medicamento:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento no encontrado.")
        return medicamento

    @staticmethod
    def listar_medicamentos(
        db: Session, busqueda: Optional[str] = None, solo_activos: bool = False
    ) -> List[MedicamentoCatalogo]:
        return MedicamentoRepository.search(db, busqueda=busqueda, solo_activos=solo_activos)

    @staticmethod
    def actualizar_medicamento(
        db: Session, id_medicamento: int, datos: MedicamentoUpdate
    ) -> MedicamentoCatalogo:
        medicamento = MedicamentoService.obtener_medicamento(db, id_medicamento)
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(medicamento, campo, valor)
        MedicamentoRepository.update(db)
        db.refresh(medicamento)
        # TODO Sprint 2: re-indexar en ChromaDB; si quedó inactivo, eliminar su entrada del vademécum
        return medicamento

    @staticmethod
    def cambiar_estado(db: Session, id_medicamento: int) -> MedicamentoCatalogo:
        medicamento = MedicamentoService.obtener_medicamento(db, id_medicamento)
        medicamento = MedicamentoRepository.toggle_activo(db, medicamento)
        # TODO Sprint 2: si se desactivó, eliminar su entrada de ChromaDB; si se reactivó, re-indexar
        return medicamento
