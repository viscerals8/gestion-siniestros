# app/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.gestion_usuarios_service import GestionUsuariosService
from ..db.database import get_db
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# Schemas de entrada
class UsuarioRequest(BaseModel):
    nombre: str
    correo: str
    password: str
    rol_id: int
    activo: Optional[bool] = True

class UsuarioUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None
    rol_id: Optional[int] = None
    activo: Optional[bool] = None

# Schema de salida con aliases que apuntan a los atributos del ORM
class UsuarioResponse(BaseModel):
    id: int = Field(alias="UserID")
    nombre: str = Field(alias="Nombre")
    correo: str = Field(alias="Correo")
    rol_id: int = Field(alias="RolID")
    activo: bool = Field(alias="Activo")

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Endpoints (nota: response_model_by_alias=False para devolver id/nombre/... en vez de UserID/Nombre/...)
@router.get("/", response_model=List[UsuarioResponse], response_model_by_alias=False)
def get_usuarios(db: Session = Depends(get_db)):
    return GestionUsuariosService.get_usuarios(db)

@router.get("/{user_id}", response_model=UsuarioResponse, response_model_by_alias=False)
def get_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = GestionUsuariosService.get_usuario(db, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.post("/", response_model=UsuarioResponse, response_model_by_alias=False)
def agregar_usuario(datos: UsuarioRequest, db: Session = Depends(get_db)):
    nuevo_usuario = GestionUsuariosService.agregar_usuario(
        db,
        nombre=datos.nombre,
        correo=datos.correo,
        password=datos.password,
        rol_id=datos.rol_id,
        activo=datos.activo
    )
    return nuevo_usuario

@router.put("/{user_id}", response_model=UsuarioResponse, response_model_by_alias=False)
def editar_usuario(user_id: int, datos: UsuarioUpdateRequest, db: Session = Depends(get_db)):
    usuario_actualizado = GestionUsuariosService.editar_usuario(
        db,
        user_id=user_id,
        nombre=datos.nombre,
        correo=datos.correo,
        password=datos.password,
        rol_id=datos.rol_id,
        activo=datos.activo
    )
    return usuario_actualizado

@router.delete("/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    return GestionUsuariosService.eliminar_usuario(db, user_id)
