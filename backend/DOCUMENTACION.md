# Documentación del Sistema de Gestión de Siniestros Laborales

## Descripción General
API REST para gestionar siniestros laborales (accidentes) con autenticación de usuarios, historial de cambios y sincronización con datos externos.

---

## Arquitectura del Proyecto

```
app/
├── main.py                      # Punto de entrada FastAPI
├── db/
│   └── database.py              # Configuración SQLAlchemy + SQL Server
├── models/
│   └── base.py                  # Modelos ORM declarativos
├── routers/
│   ├── login.py                 # Autenticación (correo/password)
│   ├── usuarios.py              # CRUD usuarios
│   ├── tabla.py                 # CRUD accidentes/registros
│   ├── historial.py             # Historial de cambios
│   └── external_import.py        # Importación de datos externos
├── services/
│   ├── login_service.py           # Lógica de autenticación
│   ├── tabla_service.py           # Lógica de accidentes con logging
│   ├── gestion_historial_service.py # Servicio de auditoría
│   ├── gestion_usuarios_service.py  # CRUD usuarios
│   └── external_import_service.py   # Normalización datos externos
└── core/
    └── config.py                # Configuración desde .env
```

---

## Modelos de Base de Datos

### Tablas Principales

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| **User** | Users | Usuarios con roles, contraseñas encriptadas (bcrypt) |
| **Accident** | Accidents | Registro principal de siniestros (40+ campos) |
| **AccidentLog** | AccidentLog | Auditoría de cambios con usuario, acción y valores |
| **Multa** | Multas | Multas asociadas a accidentes |

### Tablas de Catálogo

| Modelo | Tabla | Uso |
|--------|-------|-----|
| Rol | Roles | Roles de usuario (admin, operador, etc.) |
| Country | Countries | Países |
| Company | Companies | Empresas |
| AccidentType | AccidentTypes | Tipos de accidente |
| AccidentState | AccidentStates | Estados del accidente |
| AccidentMatter | AccidentMatters | Materias/temas |
| AccidentCategory | AccidentCategories | Categorías (hasta 3 por accidente) |

### Tablas Normalizadas (Datos Externos)

| Modelo | Tabla | Relación |
|--------|-------|----------|
| Contract | Contracts | Pertenece a Company |
| Installation | Installations | Pertenece a Company |
| Project | Projects | Vincula Contract + Installation |

---

## API Endpoints

### Base URL
`http://localhost:8000/api`

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/login` | Autentica usuario (correo + password) |
| GET | `/login/usuario/{user_id}` | Obtiene datos de usuario por ID |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuarios` | Lista todos los usuarios |
| GET | `/usuarios/{user_id}` | Obtiene usuario por ID |
| POST | `/usuarios` | Crea nuevo usuario |
| PUT | `/usuarios/{user_id}` | Actualiza usuario |
| DELETE | `/usuarios/{user_id}` | Elimina usuario |

### Registros (Accidentes)
| Método | Endpoint | Descripción | Header requerido |
|--------|----------|-------------|------------------|
| GET | `/registros` | Lista todos los accidentes | - |
| GET | `/registros/{id}` | Obtiene accidente por ID | - |
| POST | `/registros` | Crea nuevo accidente | `X-User-Id` |
| PUT | `/registros/{id}` | Actualiza accidente | `X-User-Id` |
| DELETE | `/registros/{id}` | Elimina accidente | `X-User-Id` |

### Historial
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/historial` | Lista todo el historial |
| POST | `/historial` | Crea registro de historial manual |
| GET | `/historial/filtrar` | Filtra por usuario, campo, fechas |
| GET | `/historial/ping` | Healthcheck |

### Importación Externa
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/import/external-projects` | Importa proyectos externos (normaliza Company/Contract/Installation/Project) |
| GET | `/import/ping` | Healthcheck |

---

## Flujo de Trabajo

### 1. Autenticación
```
POST /api/login
{
  "correo": "usuario@empresa.com",
  "password": "****"
}

Respuesta:
{
  "id": 1,
  "nombre": "Juan Pérez",
  "correo": "usuario@empresa.com",
  "rol": "admin"
}
```

### 2. Crear Registro
```
POST /api/registros
Headers: X-User-Id: 1
Body: {
  "JusttimeNumber": "001-2024",
  "InitialDate": "2024-01-15",
  "Company": {"Name": "Empresa XYZ"},
  "Country": {"Name": "España"},
  ...
}
```

### 3. Auditoría Automática
- Cada creación/editado genera logs en `AccidentLog`
- El historial incluye: usuario, campo afectado, valor anterior/nuevo, fecha

---

## Configuración

### Variables de Entorno (.env)
Ver `.env.example` para el formato esperado. Los valores reales viven en un `.env` local que nunca se sube al repositorio.
```env
DATABASE_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=<host>,1433;DATABASE=GestionDatosSiniestros;UID=<usuario>;PWD=<contrasena>;Encrypt=no
```

### Configuración por Defecto (core/config.py)
- **Puerto**: 1433
- **Base de datos**: GestionDatosSiniestros
- **Driver**: ODBC Driver 17 for SQL Server
- El resto de los valores (servidor, usuario, contraseña, clave secreta) se leen exclusivamente del `.env`, sin defaults reales en el código.

---

## Instalación y Ejecución

### Requisitos
- Python 3.10+
- SQL Server con ODBC Driver 17 o 18

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar servidor
```bash
uvicorn app.main:app --reload
```

### Documentación automática
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| FastAPI | 0.115.12 | Framework web |
| SQLAlchemy | 2.0.40 | ORM |
| Pydantic | 2.11.4 | Validación de datos |
| pyodbc | - | Conector SQL Server |
| bcrypt | 4.0.1 | Encriptación contraseñas |
| uvicorn | 0.34.2 | Servidor ASGI |

---

## Notas Importantes

1. **CORS**: Configurado como `allow_origins=["*"]` - restringir en producción
2. **Autenticación**: Las contraseñas usan bcrypt (passlib)
3. **Auditoría**: Se registra automáticamente en `AccidentLog` cada operación
4. **Importación**: Usa estrategia "upsert" (crea o actualiza si existe)
5. **Header X-User-Id**: Obligatorio para operaciones que modifican registros