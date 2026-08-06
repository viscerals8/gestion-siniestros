# Mapa de Archivos y Carpetas - Sistema de Gestión de Siniestros Laborales

## 1. Estructura del Proyecto

```
FastApi_Gestion_Datos/
├── .env                          # Variables de entorno (DATABASE_URL, etc.)
├── .git/                         # Repositorio Git
├── .gitattributes                # Configuración Git (line endings)
├── .vscode/
│   └── settings.json             # Configuración del editor VS Code
├── app/                          # Código fuente de la aplicación
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada FastAPI
│   ├── schemas.py                # Esquemas Pydantic (validación)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py             # Configuración centralizada (.env)
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py           # Motor SQLAlchemy + sesión BD
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py               # Modelos ORM (tablas)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── login.py              # Auth (correo/password)
│   │   ├── usuarios.py           # CRUD usuarios
│   │   ├── tabla.py              # CRUD accidentes
│   │   ├── historial.py          # Auditoría / cambios
│   │   └── external_import.py    # Importación datos externos
│   ├── services/
│   │   ├── __init__.py
│   │   ├── login_service.py           # Lógica autenticación
│   │   ├── tabla_service.py           # Lógica accidentes + logging
│   │   ├── gestion_historial_service.py # Auditoría automática
│   │   ├── gestion_usuarios_service.py  # Lógica CRUD usuarios
│   │   └── external_import_service.py   # Normalización datos externos
│   └── utils/
│       ├── __init__.py
│       └── security.py           # Hash bcrypt / JWT helpers
│   └── __pycache__/              # Bytecode Python (generado)
├── DOCUMENTACION.md              # Documentación técnica del sistema
└── requirements.txt              # Dependencias Python
```

---

## 2. Matriz de Componentes y Documentos

| Ruta / Archivo | Tipo | Descripción breve | Documento relacionado |
|----------------|------|-------------------|----------------------|
| `.env` | Config | Credenciales y URL de SQL Server | `DOCUMENTACION.md` → Configuración |
| `.gitattributes` | Config | Normalización de fin de línea Git | N/A |
| `.vscode/settings.json` | Config | Ajustes del editor (Python, Pylance) | N/A |
| `app/__init__.py` | Código | Marca `app` como paquete Python | N/A |
| `app/main.py` | Código | Instancia FastAPI, CORS, routers, startup | `DOCUMENTACION.md` → Arquitectura |
| `app/schemas.py` | Código | Modelos Pydantic (entrada/salida API) | `DOCUMENTACION.md` → API |
| `app/core/config.py` | Código | Carga `.env`, constantes globales | `DOCUMENTACION.md` → Configuración |
| `app/db/database.py` | Código | Engine SQLAlchemy, `SessionLocal`, `Base` | `DOCUMENTACION.md` → Modelos |
| `app/models/base.py` | Código | Declarative Base + tablas ORM | `DOCUMENTACION.md` → Modelos |
| `app/routers/login.py` | Código | Endpoints POST `/api/login` | `DOCUMENTACION.md` → API |
| `app/routers/usuarios.py` | Código | Endpoints CRUD `/api/usuarios` | `DOCUMENTACION.md` → API |
| `app/routers/tabla.py` | Código | Endpoints CRUD `/api/registros` | `DOCUMENTACION.md` → API |
| `app/routers/historial.py` | Código | Endpoints `/api/historial` | `DOCUMENTACION.md` → API |
| `app/routers/external_import.py` | Código | Endpoints `/api/import` | `DOCUMENTACION.md` → API |
| `app/services/login_service.py` | Código | Auth: validar credenciales, generar respuesta | `DOCUMENTACION.md` → Flujo |
| `app/services/tabla_service.py` | Código | Lógica accidentes + registro automático en log | `DOCUMENTACION.md` → Flujo |
| `app/services/gestion_historial_service.py` | Código | Servicio de auditoría y filtrado | `DOCUMENTACION.md` → Flujo |
| `app/services/gestion_usuarios_service.py` | Código | Operaciones CRUD sobre usuarios | `DOCUMENTACION.md` → Flujo |
| `app/services/external_import_service.py` | Código | Normalización y upsert de datos externos | `DOCUMENTACION.md` → Flujo |
| `app/utils/security.py` | Código | Hash bcrypt, verificación contraseñas | `DOCUMENTACION.md` → Notas |
| `DOCUMENTACION.md` | Documento | Documentación técnica completa | N/A (este doc lo complementa) |
| `requirements.txt` | Config | Dependencias del proyecto | `DOCUMENTACION.md` → Instalación |

---

## 3. Diagrama de Dependencias (por capa)

```
Cliente HTTP
    │
    ▼
app/main.py  (FastAPI + CORS)
    │
    ▼
app/routers/*.py  (rutas, validación Pydantic)
    │
    ▼
app/services/*.py  (lógica de negocio)
    │
    ├──► app/models/base.py   (acceso a tablas)
    ├──► app/db/database.py   (sesión SQLAlchemy)
    └──► app/utils/security.py  (hash bcrypt)
    │
    ▼
SQL Server  (GestionDatosSiniestros)
```

---

## 4. Relación con Documentos Externos

| Documento | Ruta | Propósito |
|------------|------|-----------|
| Documentación técnica | `DOCUMENTACION.md` | Arquitectura, API, modelos, instalación y notas |
| Mapa de archivos | `MAPA_DE_ARCHIVOS.md` | Este documento: estructura física del proyecto |

---

## 5. Notas

- Los archivos `__pycache__/` se generan automáticamente en tiempo de ejecución y no se versionan.
- El archivo `.env` **no debe** subirse a Git (contiene credenciales).
- Consulte `DOCUMENTACION.md` para detalles de endpoints, modelos de datos y configuración.
