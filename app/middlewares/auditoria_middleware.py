"""Middleware de auditoría automática (spec §11).

Intercepta los endpoints de acción crítica; si la respuesta fue exitosa (2xx),
registra en la tabla `auditoria` quién hizo qué, sobre qué registro y desde qué IP.
Nunca rompe la petición: si la auditoría falla, solo se registra una advertencia.
"""
import logging
import re

from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import SECRET_KEY, ALGORITHM
from app.database.connection import SessionLocal
from app.models.auditoria import Auditoria
from app.repositories.auditoria_repo import AuditoriaRepository

logger = logging.getLogger(__name__)

# (método, regex sobre el path, acción, tabla_afectada). El grupo (\d+) es el id_registro.
REGLAS = [
    ("POST", re.compile(r"^/usuarios/?$"), "CREACION_USUARIO", "usuario"),
    ("PUT", re.compile(r"^/usuarios/(\d+)$"), "MODIFICACION_USUARIO", "usuario"),
    ("PATCH", re.compile(r"^/usuarios/(\d+)/estado$"), "CAMBIO_ESTADO_USUARIO", "usuario"),
    ("POST", re.compile(r"^/recetas/(\d+)/validar$"), "VALIDACION_IA", "validacion_ia"),
    ("POST", re.compile(r"^/recetas/(\d+)/emitir$"), "EMISION_RECETA", "receta"),
    ("PATCH", re.compile(r"^/recetas/(\d+)/anular$"), "ANULACION_RECETA", "receta"),
    ("POST", re.compile(r"^/farmacia/dispensar$"), "DISPENSACION", "dispensacion"),
    ("POST", re.compile(r"^/farmacia/rechazar$"), "RECHAZO_DISPENSACION", "dispensacion"),
    ("POST", re.compile(r"^/medicamentos/?$"), "CREACION_MEDICAMENTO", "medicamento_catalogo"),
    ("PUT", re.compile(r"^/medicamentos/(\d+)$"), "MODIFICACION_MEDICAMENTO", "medicamento_catalogo"),
    ("PATCH", re.compile(r"^/medicamentos/(\d+)/estado$"), "CAMBIO_ESTADO_MEDICAMENTO", "medicamento_catalogo"),
]


class AuditoriaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        try:
            if 200 <= response.status_code < 300:
                self._registrar(request)
        except Exception as e:  # noqa: BLE001
            logger.warning("Auditoría no registrada: %s", e)
        return response

    def _registrar(self, request) -> None:
        metodo, path = request.method, request.url.path
        for m, rx, accion, tabla in REGLAS:
            if m != metodo:
                continue
            match = rx.match(path)
            if not match:
                continue
            id_registro = int(match.group(1)) if match.groups() else None
            id_usuario = self._id_usuario(request)
            ip = request.client.host if request.client else None
            db = SessionLocal()
            try:
                AuditoriaRepository.create(db, Auditoria(
                    id_usuario=id_usuario,
                    accion=accion,
                    tabla_afectada=tabla,
                    id_registro=id_registro,
                    detalle=f"{metodo} {path}",
                    ip_origen=ip,
                ))
            finally:
                db.close()
            return

    @staticmethod
    def _id_usuario(request):
        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            return None
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            return int(sub) if sub else None
        except (JWTError, ValueError):
            return None
