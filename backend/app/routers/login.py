# app/routers/login.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.login_service import LoginService
from ..db.database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

# Schemas de entrada y salida
class LoginRequest(BaseModel):
    correo: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str

# Endpoint para login
@router.post("/", response_model=UsuarioResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return LoginService.login(db, datos.correo, datos.password)

# Endpoint para obtener usuario por ID
@router.get("/usuario/{user_id}", response_model=UsuarioResponse)
def obtener_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = LoginService.get_usuario(db, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
