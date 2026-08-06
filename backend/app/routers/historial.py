# ============================================================
# app/routers/historial.py
# ============================================================
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from ..db.database import get_db
from ..services.gestion_historial_service import GestionHistorialService

# ============================================================
# Configuración del Router
# ============================================================
router = APIRouter(
    prefix="/historial",
    tags=["Historial"]
)

# ============================================================
# Schemas (Request / Response)
# ============================================================
class HistorialRequest(BaseModel):
    """Estructura del body al crear un registro de historial."""
    user_id: int
    accident_id: int
    tipo_accion: str
    seccion_afectada: Optional[str] = None
    campo_afectado: Optional[str] = None
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None


class HistorialResponse(BaseModel):
    """Estructura del response devuelto al frontend."""
    id: int = Field(..., validation_alias="LogID")
    user_id: int = Field(..., validation_alias="UserID")
    accident_id: int = Field(..., validation_alias="AccidentID")
    tipo_accion: str = Field(..., validation_alias="TipoAccion")
    seccion_afectada: Optional[str] = Field(None, validation_alias="SeccionAfectada")
    campo_afectado: Optional[str] = Field(None, validation_alias="CampoAfectado")
    valor_anterior: Optional[str] = Field(None, validation_alias="ValorAnterior")
    valor_nuevo: Optional[str] = Field(None, validation_alias="ValorNuevo")
    fecha: datetime = Field(..., validation_alias="Fecha")

    # Config para permitir conversión directa desde ORM
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Endpoints
# ============================================================

@router.get("/", response_model=List[HistorialResponse])
def get_historial(db: Session = Depends(get_db)):
    """
    Obtiene todo el historial (ordenado por fecha descendente).
    """
    historial = GestionHistorialService.get_historial(db)
    if not historial:
        return []  # Evita devolver None
    return historial


@router.post("/", response_model=HistorialResponse, status_code=201)
def agregar_historial(entry: HistorialRequest, db: Session = Depends(get_db)):
    """
    Crea un nuevo registro de historial.
    Se valida que existan los IDs de usuario y accidente antes de insertar.
    """
    try:
        nuevo_log = GestionHistorialService.agregar_historial(
            db=db,
            user_id=entry.user_id,
            accident_id=entry.accident_id,
            tipo_accion=entry.tipo_accion,
            seccion_afectada=entry.seccion_afectada,
            campo_afectado=entry.campo_afectado,
            valor_anterior=entry.valor_anterior,
            valor_nuevo=entry.valor_nuevo
        )
        return nuevo_log
    except HTTPException as e:
        # Propaga errores de validación o integridad
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al crear historial: {str(e)}")


@router.get("/filtrar", response_model=List[HistorialResponse])
def filtrar_historial(
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    usuario: Optional[str] = Query(None, description="Filtrar por nombre de usuario"),
    campo: Optional[str] = Query(None, description="Filtrar por campo afectado"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial del rango"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final del rango"),
    db: Session = Depends(get_db)
):
    """
    Filtra el historial según los parámetros enviados.
    Todos los filtros son opcionales.
    """
    try:
        resultados = GestionHistorialService.filtrar_historial(
            db=db,
            user_id=user_id,
            usuario=usuario,
            campo=campo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return resultados
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al filtrar historial: {str(e)}")


# ============================================================
# Ping / Healthcheck
# ============================================================
@router.get("/ping")
def ping_historial():
    """
    Endpoint de prueba para validar conectividad.
    """
    return {"ok": True, "path": "/api/historial/ping", "message": "Historial router activo ✅"}
