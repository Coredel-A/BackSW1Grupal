"""Módulo de farmacia: verificación de integridad (blockchain) y dispensación (spec §9)."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.dispensacion import Dispensacion
from app.repositories.receta_repo import RecetaRepository
from app.repositories.trazabilidad_repo import TrazabilidadRepository
from app.repositories.dispensacion_repo import DispensacionRepository
from app.schemas.receta import RecetaOut
from app.services import blockchain_service


class DispensacionService:

    @staticmethod
    def verificar(db: Session, id_receta: int) -> dict:
        """Sigue el orden de verificación de la spec §9 y devuelve el veredicto."""
        receta = RecetaRepository.get_by_id(db, id_receta)
        if not receta:
            return {
                "estado_verificacion": "no_encontrada",
                "puede_dispensar": False,
                "mensaje": "No existe una receta con ese código.",
            }

        receta_out = RecetaOut.model_validate(receta)

        # 1. Anulada
        if receta.estado == "anulada":
            return {
                "estado_verificacion": "anulada",
                "puede_dispensar": False,
                "mensaje": "Esta receta fue anulada por el médico emisor.",
                "receta": receta_out,
            }

        # 2. Ya dispensada
        if receta.estado == "dispensada":
            disp = DispensacionRepository.get_confirmada_by_receta(db, id_receta)
            cuando = disp.fecha_dispensacion.strftime("%Y-%m-%d %H:%M") if (disp and disp.fecha_dispensacion) else "—"
            return {
                "estado_verificacion": "dispensada",
                "puede_dispensar": False,
                "mensaje": f"Esta receta ya fue dispensada el {cuando}.",
                "receta": receta_out,
            }

        # 3. Validada -> verificar integridad contra blockchain
        if receta.estado == "validada":
            traza = TrazabilidadRepository.get_by_receta(db, id_receta)
            if not traza:
                return {
                    "estado_verificacion": "integridad_fallida",
                    "puede_dispensar": False,
                    "mensaje": "No se encontró registro de trazabilidad para esta receta.",
                    "receta": receta_out,
                }
            try:
                hash_actual = blockchain_service.generar_hash_receta(receta)
                hash_chain = blockchain_service.obtener_hash_blockchain(id_receta)
            except Exception:  # noqa: BLE001
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No se pudo consultar la blockchain para verificar la integridad.",
                )
            integro = (hash_actual == traza.hash_receta) and (hash_chain == traza.hash_receta)
            if not integro:
                return {
                    "estado_verificacion": "integridad_fallida",
                    "puede_dispensar": False,
                    "mensaje": "Alerta de seguridad: esta receta no supera la verificación de integridad.",
                    "hash_receta": traza.hash_receta,
                    "receta": receta_out,
                }
            return {
                "estado_verificacion": "valida",
                "puede_dispensar": True,
                "mensaje": "Integridad verificada correctamente contra la blockchain.",
                "hash_receta": traza.hash_receta,
                "receta": receta_out,
            }

        # Borrador u otro estado no emitido
        return {
            "estado_verificacion": "borrador",
            "puede_dispensar": False,
            "mensaje": "La receta aún no fue emitida por el médico.",
            "receta": receta_out,
        }

    @staticmethod
    def dispensar(db: Session, id_receta: int, id_usuario: int) -> Dispensacion:
        verif = DispensacionService.verificar(db, id_receta)
        if not verif["puede_dispensar"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=verif["mensaje"])

        receta = RecetaRepository.get_by_id(db, id_receta)
        traza = TrazabilidadRepository.get_by_receta(db, id_receta)
        disp = Dispensacion(
            id_receta=id_receta,
            id_usuario=id_usuario,
            codigo_qr=f"{id_receta}|{traza.hash_receta}" if traza else None,
            estado="confirmada",
            fecha_dispensacion=datetime.now(timezone.utc),
        )
        disp = DispensacionRepository.create(db, disp)
        receta.estado = "dispensada"
        RecetaRepository.update(db)
        return disp

    @staticmethod
    def rechazar(db: Session, id_receta: int, id_usuario: int, motivo: str) -> Dispensacion:
        receta = RecetaRepository.get_by_id(db, id_receta)
        if not receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")
        if receta.estado != "validada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede rechazar una receta emitida (validada).",
            )
        disp = Dispensacion(
            id_receta=id_receta,
            id_usuario=id_usuario,
            estado="rechazada",
            observaciones=motivo,
            fecha_dispensacion=datetime.now(timezone.utc),
        )
        # La receta permanece 'validada' (el médico puede emitir una nueva).
        return DispensacionRepository.create(db, disp)
