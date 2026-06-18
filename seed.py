"""
Seed idempotente de datos iniciales.

Se ejecuta en CADA arranque del contenedor (ver `command` en docker-compose.yml).
Es seguro correrlo muchas veces: solo crea lo que falte; nunca duplica ni pisa
datos existentes (si ya cambiaste la contraseña del admin, NO se resetea).
"""
from app.database.connection import SessionLocal
from app.models.usuario import Rol, Usuario
from app.core.security import hash_password

# Roles institucionales que usa la lógica de negocio (ver usuario_service.py)
ROLES_BASE = ["administrador", "medico", "farmaceutico"]

# Credenciales del administrador inicial (cámbialas luego desde la app si querés)
ADMIN_CORREO = "admin@pharma.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "Sistema"


def seed() -> None:
    db = SessionLocal()
    try:
        # 1. Crear los roles que aún no existan
        for nombre_rol in ROLES_BASE:
            existe = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
            if not existe:
                db.add(Rol(nombre=nombre_rol))
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
                hashed_password=hash_password(ADMIN_PASSWORD),
                numero_licencia=None,
                activo=True,
                id_rol=rol_admin.id,
            )
        )
        db.commit()
        print(f"[seed] Administrador creado -> {ADMIN_CORREO} / {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
