from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.paciente import Paciente
from app.models.historial_clinico import HistorialClinico
from app.repositories.paciente_repo import PacienteRepository
from app.repositories.diagnostico_repo import DiagnosticoRepository
from app.schemas.paciente import PacienteCreate, PacienteUpdate, HistorialClinicoCreate


class PacienteService:

    @staticmethod
    def registrar_paciente(db: Session, datos: PacienteCreate) -> Paciente:
        """Registra un paciente validando que el CI sea único."""
        if PacienteRepository.get_by_ci(db, datos.ci):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un paciente registrado con ese CI.",
            )
        nuevo = Paciente(**datos.model_dump())
        return PacienteRepository.create(db, nuevo)

    @staticmethod
    def obtener_paciente(db: Session, id_paciente: int) -> Paciente:
        paciente = PacienteRepository.get_by_id(db, id_paciente)
        if not paciente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
        return paciente

    @staticmethod
    def buscar_pacientes(
        db: Session, busqueda: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Paciente]:
        return PacienteRepository.search(db, busqueda=busqueda, skip=skip, limit=limit)

    @staticmethod
    def actualizar_paciente(db: Session, id_paciente: int, datos: PacienteUpdate) -> Paciente:
        """Edita un paciente. El CI es inmutable (no forma parte de PacienteUpdate)."""
        paciente = PacienteService.obtener_paciente(db, id_paciente)
        update_data = datos.model_dump(exclude_unset=True)
        # Blindaje extra por si alguien fuerza el campo: nunca permitir cambiar el CI.
        update_data.pop("ci", None)
        for campo, valor in update_data.items():
            setattr(paciente, campo, valor)
        PacienteRepository.update(db)
        db.refresh(paciente)
        return paciente

    @staticmethod
    def cambiar_estado(db: Session, id_paciente: int) -> Paciente:
        paciente = PacienteService.obtener_paciente(db, id_paciente)
        return PacienteRepository.toggle_activo(db, paciente)

    # --- Historial clínico ---
    @staticmethod
    def agregar_historial(
        db: Session, id_paciente: int, datos: HistorialClinicoCreate, id_usuario: int
    ) -> HistorialClinico:
        # Verifica que el paciente exista antes de registrar el evento
        PacienteService.obtener_paciente(db, id_paciente)
        evento = HistorialClinico(
            id_paciente=id_paciente,
            id_usuario=id_usuario,  # extraído del JWT, nunca del body
            descripcion=datos.descripcion,
            tipo_evento=datos.tipo_evento,
        )
        return PacienteRepository.add_historial(db, evento)

    @staticmethod
    def obtener_historial(db: Session, id_paciente: int) -> List[HistorialClinico]:
        PacienteService.obtener_paciente(db, id_paciente)
        return PacienteRepository.get_historial(db, id_paciente)

    @staticmethod
    def obtener_diagnosticos(db: Session, id_paciente: int):
        PacienteService.obtener_paciente(db, id_paciente)
        return DiagnosticoRepository.get_by_paciente(db, id_paciente)
