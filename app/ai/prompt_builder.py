"""Construcción del prompt de validación farmacoterapéutica (5 bloques, spec §12.1)."""
from datetime import date
from typing import Optional


SYSTEM_PROMPT = """Eres un sistema de apoyo a la decisión clínica farmacéutica integrado en un
hospital. Tu única función es analizar una prescripción médica junto con el
contexto clínico del paciente y el contexto farmacológico de los medicamentos,
para detectar riesgos antes de que la receta sea emitida.

Reglas estrictas que debes seguir:
1. Responde únicamente con un objeto JSON válido. No incluyas texto antes ni
   después del JSON. No uses markdown ni bloques de código.
2. No inventes información farmacológica que no esté presente en el contexto
   proporcionado. Si no tienes información suficiente sobre un medicamento,
   indícalo explícitamente en tu respuesta.
3. Clasifica el riesgo siguiendo exactamente estos criterios:
   - Nivel 0: sin hallazgos relevantes, prescripción coherente y segura.
   - Nivel 1: hallazgos informativos menores, sin peligro inmediato.
   - Nivel 2: interacciones o condiciones que requieren vigilancia activa.
   - Nivel 3: contraindicación absoluta, interacción potencialmente fatal,
     alergia conocida al fármaco, o error grave de dosificación.
4. El nivel de riesgo final es el nivel más alto encontrado entre todos los
   hallazgos individuales.
5. Nunca sugieras un tratamiento alternativo ni reemplaces la decisión del
   médico. Tu función es alertar, no prescribir."""


OUTPUT_INSTRUCTION = """INSTRUCCIÓN DE SALIDA:
Analiza toda la información anterior y responde exclusivamente con un JSON
con esta estructura exacta:

{
  "nivel_riesgo": 0,
  "justificacion_general": "string",
  "interacciones": [
    {"medicamentos": ["string", "string"], "descripcion": "string", "nivel": 0}
  ],
  "contraindicaciones": [
    {"medicamento": "string", "motivo": "string", "nivel": 0}
  ],
  "duplicidades": [
    {"medicamentos": ["string", "string"], "descripcion": "string", "nivel": 0}
  ],
  "errores_dosis": [
    {"medicamento": "string", "descripcion": "string", "nivel": 0}
  ],
  "coherencia_audio": {
    "evaluado": true,
    "porcentaje_coherencia": 0,
    "observaciones": "string"
  }
}

Si alguna categoría no tiene hallazgos, devuelve un array vacío en esa categoría."""


def _edad(fecha_nacimiento: Optional[date]) -> str:
    if not fecha_nacimiento:
        return "desconocida"
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return str(edad)


def construir_prompt(
    paciente,
    diagnostico,
    medicamentos: list[dict],
    rag_contextos: list[dict],
    transcripcion: Optional[str],
) -> str:
    """Arma el prompt completo.

    medicamentos: [{"nombre", "dosis", "via", "frecuencia", "duracion"}]
    rag_contextos: [{"nombre", "texto"|None}]
    """
    # Bloque 2 — Paciente
    bloque_paciente = f"""DATOS DEL PACIENTE:
- Edad: {_edad(paciente.fecha_nacimiento)} años
- Sexo: {paciente.sexo or 'no especificado'}
- Peso: {paciente.peso_kg if paciente.peso_kg is not None else 'no especificado'} kg
- Función renal: {paciente.funcion_renal or 'no especificada'}
- Función hepática: {paciente.funcion_hepatica or 'no especificada'}
- Alergias conocidas: {paciente.alergias or 'ninguna registrada'}
- Antecedentes relevantes: {paciente.observaciones or 'sin antecedentes registrados'}"""

    # Bloque 3 — Prescripción
    if diagnostico:
        diag = f"""DIAGNÓSTICO:
- Código CIE-10: {diagnostico.codigo_cie10 or 'no especificado'}
- Descripción: {diagnostico.descripcion}
- Tipo: {diagnostico.tipo or 'no especificado'}"""
    else:
        diag = "DIAGNÓSTICO:\n- No se asoció un diagnóstico a esta receta."

    lineas_med = []
    for i, m in enumerate(medicamentos, start=1):
        lineas_med.append(
            f"{i}. {m['nombre']} - {m['dosis']} - {m.get('via') or 'vía no especificada'} "
            f"- {m['frecuencia']} - {m['duracion']}"
        )
    bloque_prescripcion = f"""{diag}

MEDICAMENTOS PRESCRITOS:
{chr(10).join(lineas_med)}"""

    if transcripcion:
        bloque_prescripcion += f"""

TRANSCRIPCIÓN DE AUDIO CLÍNICO (dictado por el médico):
"{transcripcion}\""""
    else:
        bloque_prescripcion += (
            "\n\nNo hay transcripción de audio disponible para este caso, "
            "omite la evaluación de coherencia de audio."
        )

    # Bloque 4 — Contexto RAG
    partes_rag = ["INFORMACIÓN FARMACOLÓGICA RECUPERADA:\n"]
    for ctx in rag_contextos:
        if ctx.get("texto"):
            partes_rag.append(f"[{ctx['nombre']}]\n{ctx['texto']}\n")
        else:
            partes_rag.append(
                f"[{ctx['nombre']}]\nNo se encontró información farmacológica confiable "
                f"para este medicamento en el vademécum.\n"
            )
    bloque_rag = "\n".join(partes_rag)

    return "\n\n".join(
        [SYSTEM_PROMPT, bloque_paciente, bloque_prescripcion, bloque_rag, OUTPUT_INSTRUCTION]
    )
