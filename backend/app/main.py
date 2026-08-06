# app/main.py
import sys

# Evita UnicodeEncodeError al hacer print() de emojis en consolas Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base

# Routers
from app.routers import login, usuarios, tabla, historial, external_import, form_fields

# Asegura que los modelos estén importados para que create_all vea todas las tablas
from app.models import base as models  # noqa: F401

app = FastAPI(
    title="Sistema de Gestión de Siniestros Laborales",
    description="API para gestionar usuarios, accidentes, componentes e historial de cambios.",
    version="1.0.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe a tu(s) dominio(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Routers (todos con /api)
# -----------------------
app.include_router(login.router,           prefix="/api", tags=["Login"])
app.include_router(historial.router,       prefix="/api", tags=["Historial"])
app.include_router(external_import.router, prefix="/api", tags=["Importación"])
app.include_router(usuarios.router,        prefix="/api", tags=["Usuarios"])   # trae /usuarios internamente
app.include_router(tabla.router,           prefix="/api", tags=["Registros"])  # trae /registros o /accidentes internamente
app.include_router(form_fields.router,     prefix="/api", tags=["Campos Dinámicos"]) # Registro del nuevo módulo EAV

# -----------------------
# Startup
# -----------------------
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Conectado a la base de datos y tablas listas")
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")

# -----------------------
# Root
# -----------------------
@app.get("/")
def root():
    return {
        "message": "API de Gestión de Siniestros está activa 🚀",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }