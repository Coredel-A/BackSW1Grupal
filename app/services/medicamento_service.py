from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.medicamento_catalogo import MedicamentoCatalogo
from app.repositories.medicamento_repo import MedicamentoRepository
from app.schemas.medicamento import MedicamentoCreate, MedicamentoUpdate
from app.ai import vademecum


class MedicamentoService:

    @staticmethod
    def crear_medicamento(db: Session, datos: MedicamentoCreate) -> MedicamentoCatalogo:
        nuevo = MedicamentoCatalogo(**datos.model_dump())
        medicamento = MedicamentoRepository.create(db, nuevo)
        # Indexa en el vademécum vectorial (tolerante a fallos: no rompe el CRUD)
        if medicamento.activo:
            vademecum.indexar_medicamento(medicamento)
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
        # Re-indexa si está activo; si quedó inactivo, lo saca del vademécum
        if medicamento.activo:
            vademecum.indexar_medicamento(medicamento)
        else:
            vademecum.eliminar_medicamento(medicamento.id_medicamento)
        return medicamento

    @staticmethod
    def cambiar_estado(db: Session, id_medicamento: int) -> MedicamentoCatalogo:
        medicamento = MedicamentoService.obtener_medicamento(db, id_medicamento)
        medicamento = MedicamentoRepository.toggle_activo(db, medicamento)
        # Si se reactivó -> re-indexa; si se desactivó -> elimina del vademécum
        if medicamento.activo:
            vademecum.indexar_medicamento(medicamento)
        else:
            vademecum.eliminar_medicamento(medicamento.id_medicamento)
        return medicamento
