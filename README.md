# Gestión de Siniestros

Sistema interno para el registro, seguimiento y auditoría de siniestros laborales: alta de accidentes, gestión de usuarios por rol, historial de cambios y campos personalizables.

## Qué problema resuelve

El seguimiento de siniestros laborales (accidentes, sus datos de contrato, ubicación, costos y estado) se llevaba de forma manual/dispersa. Este sistema centraliza esa información en una base de datos única, con:

- Control de quién puede ver o modificar qué (roles: Administrador, Editor, Visualizador).
- Registro automático de cada cambio realizado sobre un siniestro (quién, qué campo, valor anterior/nuevo, cuándo), para auditoría.
- Campos de formulario configurables sin tocar código (modelo EAV: se pueden agregar campos nuevos a los siniestros desde la propia aplicación).
- Importación de proyectos/contratos desde un sistema externo (Dynamics) para no tener que cargarlos a mano.

## Cómo lo resuelve

- **Backend** (FastAPI + SQLAlchemy sobre SQL Server): expone una API REST que centraliza toda la lógica de negocio, valida datos con Pydantic y deja un log de auditoría en cada escritura sobre un siniestro.
- **Frontend** (Angular + Ionic): aplicación web/móvil (vía Capacitor) que consume esa API, con guards de ruta según el rol del usuario logueado.
- **Historial diferencial**: al editar un siniestro, el backend compara campo por campo el valor anterior contra el nuevo y solo registra los que efectivamente cambiaron.
- **Campos dinámicos (EAV)**: además de los campos fijos del siniestro, se pueden definir campos adicionales desde la sección de administración, que se guardan y consultan sin necesidad de migrar la base de datos por cada campo nuevo.

## Estado del proyecto

Este es un proyecto en desarrollo activo, no una pieza terminada. La siguiente tabla es una foto honesta de en qué estado está cada módulo, no una lista de logros.

| Módulo | Estado | Notas |
|---|---|---|
| Login (backend) | ✅ Completo | Valida contraseña con bcrypt contra el hash guardado. Incluye un acceso de emergencia opcional (deshabilitado si no se configura `EMERGENCY_BYPASS_PASSWORD` en `.env`) — ver [Seguridad](#seguridad-y-limitaciones-conocidas). |
| Autenticación por token (JWT) | 🟡 Sin conectar | Existen funciones para generar/validar JWT (`app/utils/security.py`) y el frontend ya lee un `token` de `localStorage` para mandarlo en cada request, pero el login **no genera ni devuelve ningún token** — la sesión hoy se resuelve guardando el usuario tal cual en `localStorage`, sin verificación de token en cada request. |
| Gestión de usuarios (CRUD) | ✅ Completo | Alta, edición, listado. Solo accesible para rol Administrador. |
| Registro de siniestros (alta/edición/baja) | ✅ Completo | Incluye wizard por pasos en el frontend. |
| Historial de cambios / auditoría | ✅ Completo | Registro diferencial automático + filtros por usuario, campo y rango de fechas. |
| Campos dinámicos (EAV) | ✅ Completo | Alta/baja de campos personalizados y su persistencia junto a los siniestros. |
| Importación desde Dynamics | 🟡 Parcial | El endpoint de importación existe y funciona; la validación de un proyecto contra Dynamics (`GET /validar_dynamics`) depende de un servicio externo cuya disponibilidad no está garantizada ni testeada acá. |
| Roles y permisos en el frontend | ✅ Completo | `RoleGuard` restringe rutas según el rol guardado en sesión. |
| Tests automatizados | ❌ Pendiente | No hay tests (unitarios, de integración ni e2e) en ninguno de los dos proyectos. |
| CI/CD | ❌ Pendiente | No hay pipeline configurado. |
| Build de producción documentado | 🟡 Parcial | `environment.prod.ts` existe pero no define `apiBaseUrl` ni `dynamicsBaseUrl`; hay que completarlo antes de generar un build real de producción. |

**Leyenda:** ✅ Completo · 🟡 En progreso / parcial · ❌ Pendiente

## Seguridad y limitaciones conocidas

- El login tiene un mecanismo de acceso de emergencia (bypass) pensado para desarrollo: si se define `EMERGENCY_BYPASS_PASSWORD` en el `.env`, esa contraseña otorga acceso como Administrador a cualquier cuenta existente sin validar su contraseña real. **Si no se define esa variable, el mecanismo queda completamente deshabilitado.** No debería usarse en un entorno expuesto públicamente.
- No hay autenticación por token verificada en cada request (ver tabla de estado). El control de acceso actual depende de lo que el frontend guarda en `localStorage`, no de una verificación server-side por request.
- CORS está configurado para aceptar cualquier origen (`allow_origins=["*"]`) — pensado para desarrollo, hay que restringirlo antes de exponer el backend fuera de una red controlada.

## Stack técnico

**Backend**
- Python 3.11+, FastAPI, SQLAlchemy 2.x
- SQL Server (vía ODBC / `pyodbc`)
- Autenticación de contraseñas con `bcrypt` / `passlib`
- Pydantic v2 para validación y configuración por entorno

**Frontend**
- Angular 17+ con Ionic (componentes standalone)
- Capacitor (para empaquetar como app móvil)
- RxJS para manejo de estado reactivo de sesión

## Estructura del repositorio

```
gestion-siniestros/
├── backend/     # API FastAPI
└── frontend/    # App Angular/Ionic
```

## Cómo correrlo en local

### Backend

Requisitos: Python 3.11+, acceso a una instancia de SQL Server (o adaptar `DATABASE_URL` a otro motor), y el driver ODBC de SQL Server instalado en el sistema.

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # En Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

copy .env.example .env       # En Linux/Mac: cp .env.example .env
# Editar .env con los datos reales de conexión a la base de datos

uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`, con documentación interactiva en `http://127.0.0.1:8000/docs`.

### Frontend

Requisitos: Node.js 18+ y Angular CLI (`npm install -g @angular/cli`).

```bash
cd frontend
npm install
ionic serve       # o: ng serve
```

Por defecto apunta a `http://127.0.0.1:8000/api` (ver `src/environments/environment.ts`). Si el backend corre en otra URL o el frontend se usa desde un dispositivo móvil, ajustar `apiBaseUrl` en ese archivo.

## Variables de entorno (backend)

Ver `backend/.env.example` para la lista completa. Ninguna variable tiene un valor real por defecto en el código: si `.env` no está presente o incompleto, el backend no va a poder conectarse a la base de datos.
