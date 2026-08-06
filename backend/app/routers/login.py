# app/routers/login.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.login_service import LoginService
from ..db.database import get_db
from ..utils.security import get_current_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

# Schemas de entrada y salida
class LoginRequest(BaseModel):
    correo: str
    password: str

class LoginResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    token: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str

# Endpoint para login (sin autenticación previa: es el punto de entrada)
@router.post("/", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return LoginService.login(db, datos.correo, datos.password)

# Endpoint para obtener usuario por ID (requiere sesión activa)
@router.get("/usuario/{user_id}", response_model=UsuarioResponse)
def obtener_usuario(user_id: int, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    usuario = LoginService.get_usuario(db, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
