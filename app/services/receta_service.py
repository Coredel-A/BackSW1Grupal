from datetime import date
from io import BytesIO
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models.receta import Receta
from app.models.receta_medicamento import RecetaMedicamento
from app.repositories.receta_repo import RecetaRepository
from app.repositories.paciente_repo import PacienteRepository
from app.repositories.diagnostico_repo import DiagnosticoRepository
from app.repositories.medicamento_repo import MedicamentoRepository
from app.schemas.receta import (
    RecetaCreate,
    RecetaUpdate,
    RecetaMedicamentoCreate,
    RecetaMedicamentoUpdate,
)


def _calcular_edad(fecha_nacimiento: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


class RecetaService:

    @staticmethod
    def _asegurar_borrador(receta: Receta) -> None:
        """Solo se puede editar una receta mientras está en borrador."""
        if receta.estado != "borrador":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La receta está en estado '{receta.estado}' y ya no puede modificarse.",
            )

    @staticmethod
    def _validar_medicamento(db: Session, id_medicamento: int):
        medicamento = MedicamentoRepository.get_by_id(db, id_medicamento)
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El medicamento {id_medicamento} no existe en el catálogo.",
            )
        if not medicamento.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El medicamento '{medicamento.nombre_generico}' está inactivo en el catálogo.",
            )
        return medicamento

    @staticmethod
    def obtener_receta(db: Session, id_receta: int) -> Receta:
        receta = RecetaRepository.get_by_id(db, id_receta)
        if not receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")
        return receta

    @staticmethod
    def crear_receta(db: Session, datos: RecetaCreate, id_usuario: int) -> Receta:
        if not PacienteRepository.get_by_id(db, datos.id_paciente):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
        if datos.id_diagnostico is not None and not DiagnosticoRepository.get_by_id(db, datos.id_diagnostico):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico no encontrado.")

        receta = Receta(
            id_paciente=datos.id_paciente,
            id_usuario=id_usuario,  # médico emisor, tomado del JWT
            id_diagnostico=datos.id_diagnostico,
            observaciones=datos.observaciones,
            estado="borrador",
        )

        if datos.medicamentos:
            for item in datos.medicamentos:
                RecetaService._validar_medicamento(db, item.id_medicamento)
                receta.medicamentos.append(RecetaMedicamento(**item.model_dump()))

        receta = RecetaRepository.create(db, receta)
        return RecetaService.obtener_receta(db, receta.id_receta)

    @staticmethod
    def listar_por_paciente(db: Session, id_paciente: int) -> List[Receta]:
        return RecetaRepository.get_by_paciente(db, id_paciente)

    @staticmethod
    def listar_por_medico(db: Session, id_usuario: int) -> List[Receta]:
        return RecetaRepository.get_by_medico(db, id_usuario)

    @staticmethod
    def actualizar_receta(db: Session, id_receta: int, datos: RecetaUpdate) -> Receta:
        receta = RecetaService.obtener_receta(db, id_receta)
        RecetaService._asegurar_borrador(receta)
        if datos.id_diagnostico is not None and not DiagnosticoRepository.get_by_id(db, datos.id_diagnostico):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico no encontrado.")
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(receta, campo, valor)
        RecetaRepository.update(db)
        return RecetaService.obtener_receta(db, id_receta)

    # --- Ítems de la receta (solo en borrador) ---
    @staticmethod
    def agregar_medicamento(db: Session, id_receta: int, datos: RecetaMedicamentoCreate) -> Receta:
        receta = RecetaService.obtener_receta(db, id_receta)
        RecetaService._asegurar_borrador(receta)
        RecetaService._validar_medicamento(db, datos.id_medicamento)
        item = RecetaMedicamento(id_receta=id_receta, **datos.model_dump())
        RecetaRepository.add_medicamento(db, item)
        return RecetaService.obtener_receta(db, id_receta)

    @staticmethod
    def editar_medicamento(
        db: Session, id_receta: int, id_receta_med: int, datos: RecetaMedicamentoUpdate
    ) -> Receta:
        receta = RecetaService.obtener_receta(db, id_receta)
        RecetaService._asegurar_borrador(receta)
        item = RecetaRepository.get_medicamento(db, id_receta_med)
        if not item or item.id_receta != id_receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem de receta no encontrado.")
        for campo, valor in datos.model_dump(exclude_unset=True).items():
            setattr(item, campo, valor)
        RecetaRepository.update(db)
        return RecetaService.obtener_receta(db, id_receta)

    @staticmethod
    def eliminar_medicamento(db: Session, id_receta: int, id_receta_med: int) -> Receta:
        receta = RecetaService.obtener_receta(db, id_receta)
        RecetaService._asegurar_borrador(receta)
        item = RecetaRepository.get_medicamento(db, id_receta_med)
        if not item or item.id_receta != id_receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem de receta no encontrado.")
        RecetaRepository.delete_medicamento(db, item)
        return RecetaService.obtener_receta(db, id_receta)

    # --- PDF ---
    @staticmethod
    def generar_pdf(db: Session, id_receta: int) -> BytesIO:
        """Genera el PDF de la receta (sin QR ni hash todavía; eso se agrega al emitir en el Sprint 3)."""
        receta = RecetaService.obtener_receta(db, id_receta)
        paciente = receta.paciente
        medico = receta.usuario
        diagnostico = receta.diagnostico

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
            title=f"Receta {receta.id_receta}",
        )
        styles = getSampleStyleSheet()
        label = ParagraphStyle("label", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#666666"))
        normal = styles["Normal"]
        elementos = []

        elementos.append(Paragraph("PHARMAGNOSTIC AI", styles["Title"]))
        elementos.append(Paragraph("Receta Médica", styles["Heading2"]))
        elementos.append(Spacer(1, 0.3 * cm))

        fecha_doc = receta.fecha_emision or receta.fecha_creacion
        fecha_txt = fecha_doc.strftime("%Y-%m-%d %H:%M") if fecha_doc else "-"
        meta = [
            [Paragraph("N° Receta", label), Paragraph(str(receta.id_receta), normal),
             Paragraph("Fecha", label), Paragraph(fecha_txt, normal)],
            [Paragraph("Estado", label), Paragraph(receta.estado, normal),
             Paragraph("Nivel de riesgo", label),
             Paragraph("No validada" if receta.nivel_riesgo is None else str(receta.nivel_riesgo), normal)],
        ]
        tabla_meta = Table(meta, colWidths=[3 * cm, 5.5 * cm, 3.5 * cm, 4.5 * cm])
        tabla_meta.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        elementos.append(tabla_meta)
        elementos.append(Spacer(1, 0.3 * cm))

        # Médico
        lic = medico.numero_licencia or "—"
        elementos.append(Paragraph("Médico", styles["Heading4"]))
        elementos.append(Paragraph(f"{medico.nombre} {medico.apellido} &nbsp;&nbsp; Licencia: {lic}", normal))
        elementos.append(Spacer(1, 0.2 * cm))

        # Paciente
        elementos.append(Paragraph("Paciente", styles["Heading4"]))
        edad = _calcular_edad(paciente.fecha_nacimiento)
        elementos.append(Paragraph(
            f"{paciente.nombre} {paciente.apellido} &nbsp;&nbsp; CI: {paciente.ci} &nbsp;&nbsp; "
            f"Nac.: {paciente.fecha_nacimiento.isoformat()} ({edad} años)", normal))
        if paciente.alergias:
            elementos.append(Paragraph(f"Alergias: {paciente.alergias}", normal))
        elementos.append(Spacer(1, 0.2 * cm))

        # Diagnóstico
        elementos.append(Paragraph("Diagnóstico", styles["Heading4"]))
        if diagnostico:
            cie = f"[{diagnostico.codigo_cie10}] " if diagnostico.codigo_cie10 else ""
            elementos.append(Paragraph(f"{cie}{diagnostico.descripcion}", normal))
        else:
            elementos.append(Paragraph("Sin diagnóstico asociado.", normal))
        elementos.append(Spacer(1, 0.3 * cm))

        # Medicamentos
        elementos.append(Paragraph("Medicamentos prescritos", styles["Heading4"]))
        data = [["#", "Medicamento", "Dosis", "Frecuencia", "Duración", "Vía"]]
        items = sorted(receta.medicamentos, key=lambda m: (m.orden if m.orden is not None else 0))
        for i, rm in enumerate(items, start=1):
            nombre = rm.medicamento.nombre_generico if rm.medicamento else f"Medicamento {rm.id_medicamento}"
            if rm.medicamento and rm.medicamento.nombre_comercial:
                nombre = f"{nombre} ({rm.medicamento.nombre_comercial})"
            data.append([
                str(i), Paragraph(nombre, normal), rm.dosis, rm.frecuencia, rm.duracion,
                rm.via_administracion or "-",
            ])
        if len(data) == 1:
            data.append(["—", Paragraph("Sin medicamentos.", normal), "", "", "", ""])

        tabla = Table(data, colWidths=[1 * cm, 6 * cm, 2.5 * cm, 3 * cm, 2.5 * cm, 2 * cm], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 0.5 * cm))

        # Nota de firma (QR + hash + firma digital se agregan al emitir en el Sprint 3)
        elementos.append(Paragraph(
            "Documento generado por PHARMAGNOSTIC AI. La firma digital (QR + hash en blockchain) "
            "se incorpora al emitir la receta.", label))

        doc.build(elementos)
        buffer.seek(0)
        return buffer
