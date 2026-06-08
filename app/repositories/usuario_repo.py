from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.usuario import Usuario, Rol

class UsuarioRepository:
    
    @staticmethod
    def get_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca un usuario por su ID primario."""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def get_by_correo(db: Session, correo: str) -> Optional[Usuario]:
        """Busca un usuario por su correo electrónico (útil para login y duplicados)."""
        return db.query(Usuario).filter(Usuario.correo == correo).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Lista todos los usuarios con paginación integrada."""
        return db.query(Usuario).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, usuario_db: Usuario) -> Usuario:
        """Recibe el objeto ORM instanciado, lo persiste en la base de datos y hace el commit."""
        db.add(usuario_db)
        db.commit()
        db.refresh(usuario_db)  # Recarga el objeto para obtener el ID autogenerado
        return usuario_db

    @staticmethod
    def update(db: Session) -> None:
        """Confirma los cambios realizados sobre un objeto ORM existente en la sesión."""
        db.commit()

    @staticmethod
    def toggle_activo(db: Session, usuario_db: Usuario) -> Usuario:
        """Invierte el estado de activación del usuario."""
        usuario_db.activo = not usuario_db.activo
        db.commit()
        db.refresh(usuario_db)
        return usuario_db