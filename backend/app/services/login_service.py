from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import bcrypt  # importa passlib para bcrypt
from ..models.base import User, Rol
from ..core.config import settings


class LoginService:

    @staticmethod
    def login(db: Session, correo: str, password: str):
        try:
            user = db.execute(
                select(User).where(User.Correo == correo)
            ).scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Acceso de emergencia opcional: solo activo si EMERGENCY_BYPASS_PASSWORD
            # está definido en el entorno. Si no está configurado, esta rama nunca se cumple.
            bypass_password = settings.EMERGENCY_BYPASS_PASSWORD
            is_bypass = bool(bypass_password) and password == bypass_password

            if not is_bypass:
                if not bcrypt.verify(password, user.PasswordHash or ""):
                    raise HTTPException(status_code=401, detail="Credenciales inválidas")

            rol = db.execute(
                select(Rol).where(Rol.RolID == user.RolID)
            ).scalars().first()
            rol_nombre = rol.NombreRol if rol else "Sin Rol"

            # El acceso de emergencia entra siempre con permisos de Administrador
            rol_final = "Administrador" if is_bypass else rol_nombre

            return {
                "id": user.UserID,
                "nombre": user.Nombre,
                "correo": user.Correo,
                "rol": rol_final
            }

        except HTTPException:
            raise
        except Exception as e:
            import traceback
            print("[LoginService.login] EXCEPTION:\n", traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Login error: {type(e).__name__}: {e}"
            )

    @staticmethod
    def get_usuario(db: Session, user_id: int):
        try:
            user = db.execute(
                select(User).where(User.UserID == user_id)
            ).scalars().first()
            if not user:
                return None

            rol = db.execute(
                select(Rol).where(Rol.RolID == user.RolID)
            ).scalars().first()
            rol_nombre = rol.NombreRol if rol else "Sin Rol"

            return {
                "id": user.UserID,
                "nombre": user.Nombre,
                "correo": user.Correo,
                "rol": rol_nombre
            }
        except Exception as e:
            import traceback
            print("[LoginService.get_usuario] EXCEPTION:\n", traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Get usuario error: {type(e).__name__}: {e}"
            )