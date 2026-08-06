# app/services/gestion_usuarios_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from ..models.base import User, Rol
from passlib.hash import bcrypt

class GestionUsuariosService:
    """Servicio para manejar usuarios, equivalente a Angular GestionUsuariosService"""

    @staticmethod
    def get_usuarios(db: Session) -> List[User]:
        return db.query(User).all()

    @staticmethod
    def get_usuario(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.UserID == user_id).first()

    @staticmethod
    def agregar_usuario(db: Session, nombre: str, correo: str, password: str, rol_id: int, activo: bool = True) -> User:
        existing_user = db.query(User).filter(User.Correo == correo).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
        hashed_password = bcrypt.hash(password)
        nuevo_usuario = User(
            Nombre=nombre,
            Correo=correo,
            PasswordHash=hashed_password,
            RolID=rol_id,
            Activo=activo
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario

    @staticmethod
    def editar_usuario(db: Session, user_id: int, nombre: Optional[str] = None, correo: Optional[str] = None,
                       password: Optional[str] = None, rol_id: Optional[int] = None, activo: Optional[bool] = None) -> User:
        usuario = db.query(User).filter(User.UserID == user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if nombre:
            usuario.Nombre = nombre
        if correo:
            existing_user = db.query(User).filter(User.Correo == correo, User.UserID != user_id).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")
            usuario.Correo = correo
        if password:
            usuario.PasswordHash = bcrypt.hash(password)
        if rol_id:
            usuario.RolID = rol_id
        if activo is not None:
            usuario.Activo = activo
        
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def eliminar_usuario(db: Session, user_id: int):
        usuario = db.query(User).filter(User.UserID == user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        db.delete(usuario)
        db.commit()
        return {"detail": "Usuario eliminado"}
