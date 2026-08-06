# ============================================================
# app/services/gestion_historial_service.py
# ============================================================
from typing import List, Optional
from datetime import datetime
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.base import AccidentLog, User, Accident


class GestionHistorialService:
    """
    Servicio para manejar el historial de cambios (tabla AccidentLog).
    Encargado de registrar, listar y filtrar logs de modificaciones en accidentes.
    """

    # ============================================================
    # Obtener historial completo
    # ============================================================
    @staticmethod
    def get_historial(db: Session) -> List[AccidentLog]:
        """
        Retorna todos los registros del historial ordenados por fecha (más recientes primero).
        """
        try:
            return (
                db.query(AccidentLog)
                .join(User, AccidentLog.UserID == User.UserID)
                .order_by(AccidentLog.LogID.desc())
                .all()
            )
        except Exception as e:
            print("⚠️ Error en get_historial:", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno al listar historial")


    # ============================================================
    # Agregar nuevo registro al historial
    # ============================================================
    @staticmethod
    def agregar_historial(
        db: Session,
        user_id: int,
        accident_id: int,
        tipo_accion: str,
        seccion_afectada: Optional[str] = None,
        campo_afectado: Optional[str] = None,
        valor_anterior: Optional[str] = None,
        valor_nuevo: Optional[str] = None,
    ) -> AccidentLog:
        """
        Inserta un nuevo registro en AccidentLog.
        Valida la existencia de User y Accident antes de insertar.
        """
        try:
            # Validar usuario existente
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                raise HTTPException(status_code=422, detail=f"El usuario con ID {user_id} no existe.")

            # Validar accidente existente
            accident = db.query(Accident).filter(Accident.AccidentID == accident_id).first()
            if not accident:
                raise HTTPException(status_code=422, detail=f"El accidente con ID {accident_id} no existe.")

            # Crear nuevo log
            nuevo_log = AccidentLog(
                UserID=user_id,
                AccidentID=accident_id,
                TipoAccion=tipo_accion,
                SeccionAfectada=seccion_afectada,
                CampoAfectado=campo_afectado,
                ValorAnterior=valor_anterior,
                ValorNuevo=valor_nuevo,
                Fecha=datetime.now(),
            )

            db.add(nuevo_log)
            db.flush()  # garantiza que LogID se genere antes del commit
            db.commit()
            db.refresh(nuevo_log)

            print(f"🧾 Log insertado correctamente (LogID={nuevo_log.LogID})")
            return nuevo_log

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            print("⚠️ Error de integridad en AccidentLog:", e)
            raise HTTPException(
                status_code=422,
                detail="Violación de integridad referencial (FK). Verifica user_id o accident_id."
            )
        except Exception as e:
            db.rollback()
            print("❌ Error inesperado al insertar historial:", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno al agregar historial")


    # ============================================================
    # Filtrar historial
    # ============================================================
    @staticmethod
    def filtrar_historial(
        db: Session,
        user_id: Optional[int] = None,
        usuario: Optional[str] = None,
        campo: Optional[str] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
    ) -> List[AccidentLog]:
        """
        Filtra el historial según criterios: usuario, campo afectado, rango de fechas.
        - `user_id`: filtra por ID de usuario.
        - `usuario`: busca por nombre de usuario (LIKE / ILIKE).
        - `campo`: filtra por nombre del campo afectado.
        - `fecha_inicio` y `fecha_fin`: rango de fechas.
        """
        try:
            q = db.query(AccidentLog).join(User, AccidentLog.UserID == User.UserID)

            # Filtros dinámicos
            if user_id is not None:
                q = q.filter(AccidentLog.UserID == user_id)

            if usuario:
                q = q.filter(User.Nombre.ilike(f"%{usuario}%"))

            if campo:
                q = q.filter(AccidentLog.CampoAfectado.ilike(f"%{campo}%"))

            if fecha_inicio:
                q = q.filter(AccidentLog.Fecha >= fecha_inicio)

            if fecha_fin:
                q = q.filter(AccidentLog.Fecha <= fecha_fin)

            resultados = q.order_by(AccidentLog.LogID.desc()).all()
            print(f"🔍 Filtrado completado. Resultados: {len(resultados)} registros encontrados.")
            return resultados

        except Exception as e:
            print("❌ Error interno al filtrar historial:", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno al filtrar historial")
