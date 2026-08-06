# app/utils/security.py
import bcrypt
from datetime import datetime, timedelta
from typing import Final, Optional
from jose import jwt, JWTError
from ..core.config import settings

# Configuraciones para el hashing de contraseñas
BCRYPT_SALT: Final[bytes] = bcrypt.gensalt()

def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), BCRYPT_SALT)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano con un hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Funciones para JWT (JSON Web Tokens)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decodifica un token JWT y maneja los errores."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None