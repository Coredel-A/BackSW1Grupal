from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.diagnostico import Diagnostico
from app.repositories.diagnostico_repo import DiagnosticoRepository
from app.repositories.paciente_repo import PacienteRepository
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoUpdate


class DiagnosticoService:

    @staticmethod
    def registrar_diagnostico(db: Session, datos: DiagnosticoCreate, id_usuario: int) -> Diagnostico:
        # El paciente debe existir
        if not PacienteRepository.get_by_id(db, datos.id_paciente):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
        nuevo = Diagnostico(
            id_paciente=datos.id_paciente,
            id_usuario=id_usuario,  # extraído del JWT
            codigo_cie10=datos.codigo_cie10,
            descripcion=datos.descripcion,
            tipo=datos.tipo,
            observaciones=datos.observaciones,
        )
        return DiagnosticoRepository.create(db, nuevo)

    @staticmethod
    def obtener_diagnostico(db: Session, id_diagnostico: int) -> Diagnostico:
        diagnostico = DiagnosticoRepository.get_by_id(db, id_diagnostico)
        if not diagnostico:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico no encontrado.")
        return diagnostico

    @staticmethod
    def actualizar_diagnostico(db: Session, id_diagnostico: int, datos: DiagnosticoUpdate) -> Diagnostico:
        diagnostico = DiagnosticoService.obtener_diagnostico(db, id_diagnostico)
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(diagnostico, campo, valor)
        DiagnosticoRepository.update(db)
        db.refresh(diagnostico)
        return diagnostico

    @staticmethod
    def get_confirmados_by_paciente(db: Session, id_paciente: int) -> List[Diagnostico]:
        return DiagnosticoRepository.get_confirmados_by_paciente(db, id_paciente)
