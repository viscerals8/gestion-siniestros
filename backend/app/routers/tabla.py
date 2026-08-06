from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from typing import List, Dict, Any
from pydantic import RootModel

from ..services.tabla_service import TablaService
from ..db.database import get_db
from ..utils.security import get_current_user

router = APIRouter(
    prefix="/registros",
    tags=["Registros"],
    dependencies=[Depends(get_current_user)],
)

# --------------------------------------------------------------------
# Schemas dinámicos
# --------------------------------------------------------------------
class RegistroRequest(RootModel[Dict[str, Any]]):
    """Permite JSON flexible con campos anidados (Company, Country, etc.)"""
    pass

class RegistroResponse(RootModel[Dict[str, Any]]):
    """Payload dinámico de salida"""
    model_config = {"from_attributes": True}

# --------------------------------------------------------------------
# Utilidad mejorada para convertir ORM a dict serializable
# --------------------------------------------------------------------
def sa_to_dict(obj) -> Dict[str, Any]:
    try:
        mapper = inspect(obj).mapper
        result = {col.key: getattr(obj, col.key) for col in mapper.column_attrs}
    except Exception:
        d = dict(getattr(obj, "__dict__", {}))
        d.pop("_sa_instance_state", None)
        result = d

    # CORRECCIÓN CRÍTICA: Si el objeto trae el diccionario híbrido, incluirlo en la salida
    if hasattr(obj, "custom_fields"):
        result["custom_fields"] = getattr(obj, "custom_fields")
        
    return result

# --------------------------------------------------------------------
# Endpoints principales
# --------------------------------------------------------------------
@router.get("/", response_model=List[RegistroResponse])
def obtener_registros(db: Session = Depends(get_db)):
    """Retorna todos los registros de Accident con sus campos dinámicos."""
    registros = TablaService.obtener_registros(db)
    return [RegistroResponse(root=sa_to_dict(r)) for r in registros]


@router.get("/{registro_id}", response_model=RegistroResponse)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)):
    """Retorna un registro por su ID incluyendo campos dinámicos."""
    registro = TablaService.obtener_registro(db, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return RegistroResponse(root=sa_to_dict(registro))


@router.post("/", response_model=RegistroResponse)
def agregar_registro(
    datos: RegistroRequest,
    db: Session = Depends(get_db),
    x_user_id: int = Header(..., alias="X-User-Id"),
):
    """Inserta un nuevo registro híbrido (fijo + dinámico)."""
    try:
        print("📦 Datos recibidos del frontend:\n", datos.root)
        nuevo = TablaService.agregar_registro(db, datos.root, user_id=x_user_id)
        print("✅ Registro insertado correctamente")
        return RegistroResponse(root=sa_to_dict(nuevo))
    except Exception as e:
        print("❌ ERROR al insertar registro:", str(e))
        raise HTTPException(status_code=400, detail=f"Error al agregar registro: {str(e)}")


@router.put("/{registro_id}", response_model=RegistroResponse)
def actualizar_registro(
    registro_id: int,
    datos: RegistroRequest,
    db: Session = Depends(get_db),
    x_user_id: int = Header(..., alias="X-User-Id"),
):
    """Actualiza un registro existente y sus campos dinámicos."""
    actualizado = TablaService.actualizar_registro(db, registro_id, datos.root, user_id=x_user_id)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return RegistroResponse(root=sa_to_dict(actualizado))


@router.delete("/{registro_id}")
def eliminar_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    x_user_id: int = Header(..., alias="X-User-Id"),
):
    """Elimina un registro por su ID."""
    TablaService.eliminar_registro(db, registro_id, user_id=x_user_id)
    return {"detail": "Registro eliminado correctamente"}