"""
Seed idempotente de datos iniciales.

Se ejecuta en CADA arranque del contenedor (ver `command` en docker-compose.yml).
Es seguro correrlo muchas veces: solo crea lo que falte; nunca duplica ni pisa
datos existentes (si ya cambiaste la contraseña del admin, NO se resetea).
"""
from app.database.connection import SessionLocal
from app.models.usuario import Rol, Usuario
from app.core.security import hash_password

# Los cuatro roles institucionales (spec §5)
ROLES_BASE = [
    ("administrador", "Acceso total: gestiona usuarios, catálogo y auditoría."),
    ("medico", "Gestiona pacientes, diagnósticos y emite recetas."),
    ("farmaceutico", "Verifica integridad y dispensa recetas en farmacia."),
    ("paciente", "Consulta sus recetas activas y usa el chatbot."),
]

# Credenciales del administrador inicial (spec §5). Se fuerza el cambio en el primer login.
ADMIN_CORREO = "admin@pharmagnostic.local"
ADMIN_PASSWORD = "Admin1234"
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "Sistema"


def seed() -> None:
    db = SessionLocal()
    try:
        # 1. Crear los roles que aún no existan
        for nombre_rol, descripcion in ROLES_BASE:
            rol = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
            if not rol:
                db.add(Rol(nombre=nombre_rol, descripcion=descripcion))
                print(f"[seed] Rol creado: {nombre_rol}")
        db.commit()

        # 2. Crear el administrador inicial solo si no existe
        admin = db.query(Usuario).filter(Usuario.correo == ADMIN_CORREO).first()
        if admin:
            print(f"[seed] Administrador ya existe, se respeta: {ADMIN_CORREO}")
            return

        rol_admin = db.query(Rol).filter(Rol.nombre == "administrador").first()
        db.add(
            Usuario(
                nombre=ADMIN_NOMBRE,
                apellido=ADMIN_APELLIDO,
                correo=ADMIN_CORREO,
                contrasena_hash=hash_password(ADMIN_PASSWORD),
                numero_licencia=None,
                activo=True,
                requiere_cambio_password=True,  # fuerza el cambio en el primer ingreso
                id_rol=rol_admin.id_rol,
            )
        )
        db.commit()
        print(f"[seed] Administrador creado -> {ADMIN_CORREO} / {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
