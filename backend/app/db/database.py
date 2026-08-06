# app/db/database.py
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Si usas settings, lo intentamos leer; si no, tomamos env var
try:
    from app.core.config import settings
    DATABASE_URL = getattr(settings, "DATABASE_URL", "") or os.getenv("DATABASE_URL", "")
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL", "")

Base = declarative_base()

def _engine_from_odbc_string(odbc_str: str):
    # Aquí SÍ se usa odbc_connect + quote_plus
    odbc_url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)
    return create_engine(odbc_url, fast_executemany=True, pool_pre_ping=True)

def make_engine():
    url = (DATABASE_URL or "").strip()

    # --- Caso C: no hay DATABASE_URL -> construir desde variables sueltas
    if not url:
        server   = os.getenv("SQL_SERVER", "localhost")
        port     = os.getenv("SQL_PORT", "1433")
        db       = os.getenv("SQL_DATABASE", "GestionDatosSiniestros")
        driver   = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")  # o 17 si es tu caso
        user     = os.getenv("SQL_USER")
        pwd      = os.getenv("SQL_PASSWORD")
        encrypt  = os.getenv("SQL_ENCRYPT", "yes")
        trust    = os.getenv("SQL_TRUST_CERT", "yes")
        trusted  = os.getenv("SQL_TRUSTED_CONNECTION", "no")

        parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={server}",
            f"DATABASE={db}",
            f"Encrypt={encrypt}",
            f"TrustServerCertificate={trust}",
        ]

        # Si no es instancia con backslash, agrega puerto host,port
        if "\\" not in server and port:
            parts[1] = f"SERVER={server},{port}"

        if trusted.lower() in ("yes", "true", "1"):
            parts.append("Trusted_Connection=yes")
        else:
            parts += [f"UID={user or ''}", f"PWD={pwd or ''}"]

        odbc_str = ";".join(parts)
        return _engine_from_odbc_string(odbc_str)

    # --- Caso B: te pasan una cadena ODBC pura (empieza con DRIVER=)
    if url.upper().startswith("DRIVER="):
        return _engine_from_odbc_string(url)

    # --- Caso A: te pasan una URL completa SQLAlchemy para pyodbc
    if url.startswith("mssql+pyodbc://"):
        return create_engine(url, fast_executemany=True, pool_pre_ping=True)

    # Otros motores (sqlite/postgres/mysql, etc.)
    return create_engine(url, pool_pre_ping=True)

engine = make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
