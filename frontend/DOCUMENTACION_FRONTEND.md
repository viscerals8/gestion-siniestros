# Documentación del Frontend - Gestión de Datos

Proyecto: `gestion-datos`  
Framework principal: Angular 20 standalone  
UI: Ionic Angular 8  
Móvil/Híbrido: Capacitor  
Lenguaje: TypeScript

Este documento resume la estructura, rutas, servicios, integración con backend, autenticación, estado, modelos y comandos del frontend.

---

## 1. Resumen general

Esta aplicación es un frontend para gestionar datos de registros, usuarios e historial de cambios. Está construida con Angular en modo standalone, Ionic para la interfaz y Capacitor como integración híbrida.

La aplicación se conecta principalmente a un backend FastAPI expuesto en:

```txt
http://127.0.0.1:8000/api
```

También consume una API externa de Dynamics para obtener datos de contrato a partir de un número de proyecto/expediente.

La app tiene tres roles principales:

- `Administrador`
- `Editor`
- `Visualizador`

Cada rol tiene rutas y capacidades diferentes.

---

## 2. Estructura del proyecto

La aplicación frontend está ubicada en:

```txt
gestion-datos/gestion-datos
```

Estructura principal:

```txt
gestion-datos/
└─ gestion-datos/
   ├─ angular.json
   ├─ package.json
   ├─ package-lock.json
   ├─ capacitor.config.ts
   ├─ ionic.config.json
   ├─ tsconfig.json
   ├─ src/
   │  ├─ main.ts
   │  ├─ index.html
   │  ├─ global.scss
   │  ├─ assets/
   │  │  ├─ logo.png
   │  │  ├─ icon/favicon.png
   │  │  └─ shapes.svg
   │  ├─ environments/
   │  │  ├─ environment.ts
   │  │  └─ environment.prod.ts
   │  └─ app/
   │     ├─ app.component.ts
   │     ├─ app.component.html
   │     ├─ app.routes.ts
   │     ├─ guards/
   │     │  └─ role.guard.ts
   │     ├─ pages/
   │     │  ├─ login/
   │     │  ├─ gestion-usuarios/
   │     │  ├─ tabla/
   │     │  └─ historial-cambios/
   │     └─ services/
   │        ├─ api.service.ts
   │        ├─ login.service.ts
   │        ├─ tabla.service.ts
   │        ├─ gestion-usuario.service.ts
   │        ├─ historial-cambios.service.ts
   │        ├─ external-import.service.ts
   │        ├─ dynamics.service.ts
   │        └─ form-fields.service.ts
```

---

## 3. Archivos clave

### `src/main.ts`

Inicializa la aplicación Angular usando `bootstrapApplication`.

Registra:

- Router de Angular.
- Ionic Angular.
- HttpClient.

Archivo: `src/main.ts`

---

### `src/app/app.component.ts`

Componente raíz de la aplicación.

Usa:

```html
<ion-app>
  <ion-router-outlet></ion-router-outlet>
</ion-app>
```

Archivo: `src/app/app.component.html`

---

### `src/app/app.routes.ts`

Define las rutas de la aplicación.

Archivo: `src/app/app.routes.ts`

---

### `src/environments/environment.ts`

Define la configuración del entorno de desarrollo.

Contiene:

```ts
apiBaseUrl: 'http://127.0.0.1:8000/api'
```

Archivo: `src/environments/environment.ts`

---

## 4. Rutas y páginas

Rutas definidas en `src/app/app.routes.ts`.

| Ruta | Componente | Guard | Roles permitidos |
|---|---|---|---|
| `/` | Redirección | No | No aplica |
| `/login` | `LoginPage` | No | Público |
| `/gestion-usuarios` | `GestionUsuariosPage` | `RoleGuard` | `Administrador` |
| `/tabla` | `TablaPage` | `RoleGuard` | `Administrador`, `Editor`, `Visualizador` |
| `/historial-cambios` | `HistorialCambiosPage` | `RoleGuard` | `Administrador`, `Editor`, `Visualizador` |
| `**` | Redirección | No | Redirige a `/login` |

---

## 5. Páginas principales

### 5.1 `LoginPage`

Archivos:

- `src/app/pages/login/login.page.ts`
- `src/app/pages/login/login.page.html`

Función:

- Muestra el formulario de inicio de sesión.
- Recibe correo y contraseña.
- Llama a `LoginService.login()`.
- Si el login falla, muestra una alerta.
- Si el login tiene éxito, el servicio redirige según el rol del usuario.

Campos principales:

- `email`
- `password`
- `loading`

---

### 5.2 `GestionUsuariosPage`

Archivos:

- `src/app/pages/gestion-usuarios/gestion-usuarios.page.ts`
- `src/app/pages/gestion-usuarios/gestion-usuarios.page.html`

Función:

- Administrar usuarios.
- Crear usuarios.
- Editar usuarios.
- Listar usuarios.
- Filtrar usuarios activos/inactivos.
- Mostrar/ocultar menú de navegación colapsable.
- Cerrar sesión.

Acciones principales:

- `cargarUsuarios()`
- `agregarUsuario()`
- `editarCampoUsuario()`
- `aplicarFiltro()`
- `puedeAgregar()`
- `puedeEditar()`
- `toggleMenu()`
- `irTabla()` / `irHistorialCambios()` / `irGestionUsuarios()`
- `cerrarSesion()`

Restricción funcional:

- Solo el rol `Administrador` puede agregar o editar usuarios.

Estado reactivo:

- La página ya no fija `rolUsuarioLogueado` de forma estática. Se suscribe a `LoginService.usuario$` en `ngOnInit()` (y se desuscribe en `ngOnDestroy()`), de modo que el rol y el usuario actual se actualizan en tiempo real si cambia la sesión.
- El menú de navegación (`showMenu`) ahora está oculto por defecto y se despliega con el botón `☰ Menú` del header.
- `cerrarSesion()` ahora invoca `LoginService.logout()` (antes solo redirigía a `/login` sin limpiar la sesión).

---

### 5.3 `TablaPage`

Archivos:

- `src/app/pages/tabla/tabla.page.ts`
- `src/app/pages/tabla/tabla.page.html`

Función:

- Gestionar registros principales.
- Cargar registros desde backend.
- Crear registros.
- Editar registros.
- Eliminar registros.
- Filtrar por búsqueda.
- Filtrar por último mes.
- Consultar datos de contrato en Dynamics.
- Exportar registros a Excel.
- Gestionar campos personalizados/dinámicos por registro (capa EAV).
- Mostrar/ocultar menú de navegación colapsable.

Acciones principales:

- `cargarRegistros()`
- `filtrarRegistros()`
- `guardarRegistro()`
- `editarRegistro()`
- `cancelarEdicion()`
- `eliminarRegistro()`
- `buscarContrato()`
- `exportarExcel()`
- `cargarConfiguracionCamposDinamicos()`
- `inicializarValoresDinamicos()`
- `toggleMenu()`
- `irTabla()` / `irHistorialCambios()` / `irGestionUsuarios()`
- `cerrarSesion()`

Permisos:

- `Administrador` y `Editor` pueden crear, editar y eliminar registros.
- `Visualizador` puede ver registros.

Estado reactivo:

- Igual que en las otras páginas, `usuario` y `rolUsuarioLogueado` ahora se derivan de la suscripción a `LoginService.usuario$` en vez de leerse una sola vez con `getUsuarioSesion()`.
- El menú de navegación incluye un ítem "👥 Gestión de Usuarios" visible solo si `rolUsuarioLogueado === 'Administrador'`.

Campos dinámicos (EAV):

- En `ngOnInit()` se llama a `cargarConfiguracionCamposDinamicos()`, que consulta `FormFieldsService.getFields(true)` para traer el catálogo de campos activos (`camposDinamicos: FormField[]`).
- `inicializarValoresDinamicos()` construye `valoresDinamicos: { [key]: any }` con un valor por defecto según `data_type` (`false` para `boolean`, `''` para el resto).
- El formulario renderiza dinámicamente un `ion-input`/`ion-checkbox` por cada campo activo (tipos soportados: `string`, `number`, `boolean`), usando `[(ngModel)]="valoresDinamicos[campo.name]"`.
- Al guardar, `guardarRegistro()` agrega `payload.custom_fields = { ...valoresDinamicos }` al cuerpo enviado al backend.
- Al editar (`editarRegistro()`), si el registro trae `custom_fields`, sus valores se vuelcan sobre `valoresDinamicos` para precargar el formulario.
- La columna `custom_fields` se oculta en la tabla principal (`[class.ion-hide]`) porque es un objeto anidado, no un valor escalar.
- `exportarExcel()` aplana `custom_fields` antes de exportar: cada clave se agrega como una columna nueva con el prefijo `[Dinámico] `.

Nota: el método `eliminarRegistro(id)` existe en el componente (llama a `TablaService.eliminarRegistroFastAPI`), pero actualmente no hay un botón "Eliminar" cableado en `tabla.page.html`; solo se expone el botón "Editar" en la tabla.

---

### 5.4 `HistorialCambiosPage`

Archivos:

- `src/app/pages/historial-cambios/historial-cambios.page.ts`
- `src/app/pages/historial-cambios/historial-cambios.page.html`

Función:

- Mostrar historial de cambios.
- Filtrar historial localmente.
- Filtrar historial usando backend.
- Exportar historial a CSV.
- Mostrar/ocultar menú de navegación colapsable.

Acciones principales:

- `cargarHistorial()`
- `aplicarFiltros()`
- `aplicarFiltrosBackend()`
- `limpiarFiltros()`
- `exportarCSV()`
- `formatValueForDisplay()`
- `toggleMenu()`
- `irTabla()` / `irHistorialCambios()` / `irGestionUsuarios()`
- `cerrarSesion()`

Permisos:

- Todos los roles pueden ver historial.
- Solo `Administrador` y `Editor` pueden exportar CSV.

Cambio importante — datos reales en vez de mock:

- Antes la página definía su propia interfaz local `HistorialEntry` (con campos `usuario`, `tipoAccion`, `seccionAfectada`, etc.) y se inicializaba con datos de ejemplo hardcodeados en el constructor.
- Ahora importa `HistorialEntry` directamente desde `HistorialCambiosService` (el modelo real alineado al backend: `user_id`, `tipo_accion`, `seccion_afectada`, `campo_afectado`, `valor_anterior`, `valor_nuevo`) y `cargarHistorial()` llama a `HistorialCambiosService.getHistorial()` en `ngOnInit()`.
- `usuariosDisponibles` y `camposDisponibles` (listas para los selects de filtro) ya no están hardcodeadas: se calculan dinámicamente a partir de los datos recibidos (`user_id` únicos y `campo_afectado` únicos).
- Los filtros locales (`aplicarFiltros()`) ahora comparan por `user_id` en vez de por nombre de usuario (`entry.usuario`), ya que el backend no expone el nombre, solo el ID.
- El export CSV incluye la columna "Usuario (ID)" en vez de un nombre de usuario legible.
- Se agregó `cargando: boolean` para reflejar el estado de carga durante las peticiones al backend.
- Igual que en las otras páginas, el rol/usuario activo ahora proviene de la suscripción a `LoginService.usuario$` en vez de una lectura única con `getUsuarioSesion()`.

---

## 6. Servicios principales

### 6.1 `ApiService`

Archivo: `src/app/services/api.service.ts`

Es el servicio HTTP base.

Responsabilidades:

- Centralizar llamadas HTTP.
- Agregar headers comunes.
- Manejar errores HTTP.
- Adjuntar token de autorización si existe en `localStorage`.

Métodos:

- `get<T>()`
- `post<T>()`
- `put<T>()`
- `patch<T>()`
- `delete<T>()`

Headers:

- `Content-Type: application/json`
- `Authorization: Bearer <token>` si existe `localStorage.getItem('token')`.

Error devuelto:

```ts
{
  status: number;
  message: string;
  timestamp: string;
  url: string | null;
}
```

---

### 6.2 `LoginService`

Archivo: `src/app/services/login.service.ts`

Responsabilidades:

- Autenticar usuario.
- Guardar sesión.
- Exponer sesión como observable reactivo.
- Restaurar sesión desde `localStorage` al iniciar la app.
- Redirigir según rol.
- Cerrar sesión.

Métodos:

- `login(datos)`
- `obtenerUsuario(userId)`
- `logout()`
- `getUsuarioSesion()`
- `getRol()`
- `estaAutenticado()`

Observable de sesión:

```ts
usuario$ // Observable<UsuarioSesion | null>, respaldado por un BehaviorSubject
```

Almacena la sesión en:

```ts
localStorage.setItem('usuarioSesion', JSON.stringify(user));
```

Comportamiento reactivo (cambio reciente):

- `usuario$` es ahora un `BehaviorSubject<UsuarioSesion | null>` expuesto como observable, en vez de calcularse bajo demanda. Todas las páginas (`TablaPage`, `GestionUsuariosPage`, `HistorialCambiosPage`) y el `RoleGuard` se suscriben a él para reaccionar a cambios de sesión en tiempo real.
- En el `constructor`, si existe `usuarioSesion` en `localStorage`, se restaura en memoria y se emite por `usuario$`. Esto permite que la sesión sobreviva a un refresco de página (F5).
- `login()` ahora, además de guardar el usuario en memoria, lo persiste en `localStorage` y emite el nuevo valor por `usuario$` antes de navegar según el rol.
- `logout()` limpia la sesión en memoria, elimina `usuarioSesion` de `localStorage` y emite `null` por `usuario$`.
- Se agregó `getRol()` como atajo para obtener `usuarioSesion?.rol` sin pasar por `getUsuarioSesion()`.

---

### 6.3 `GestionUsuariosService`

Archivo: `src/app/services/gestion-usuario.service.ts`

Responsabilidades:

- Consumir endpoints de usuarios.

Métodos:

- `getUsuarios()`
- `agregarUsuario(usuario)`
- `editarUsuario(id, usuario)`
- `eliminarUsuario(id)`

---

### 6.4 `TablaService`

Archivo: `src/app/services/tabla.service.ts`

Responsabilidades:

- Consumir endpoints de registros.
- Normalizar datos de backend.
- Serializar datos hacia backend.
- Mantener un `BehaviorSubject` de registros.
- Adjuntar el ID del usuario logueado en cada operación de escritura.

Métodos:

- `obtenerRegistros()`
- `obtenerRegistro(id)`
- `agregarRegistroFastAPI(registro)`
- `actualizarRegistroFastAPI(id, registro)`
- `eliminarRegistroFastAPI(id)`

Header especial:

```http
X-User-Id: <id_usuario_actual>
```

Se envía en operaciones de registros (POST, PUT y ahora también DELETE).

Cambio reciente — origen del header `X-User-Id`:

- `TablaService` ahora inyecta `LoginService` en el constructor y define un método privado `authHeaders()` que lee el usuario activo con `loginService.getUsuarioSesion()` y arma `{ 'X-User-Id': <id> }` (soporta tanto `u.id` como `u.UserID`).
- Antes, el header `X-User-Id` solo se enviaba en `POST` y `PUT`. Ahora `eliminarRegistroFastAPI()` también lo incluye, para que el backend pueda registrar quién eliminó un registro en el historial de cambios.
- Si no hay usuario en sesión, `authHeaders()` devuelve un objeto vacío `{}` (no se envía el header).

---

### 6.5 `HistorialCambiosService`

Archivo: `src/app/services/historial-cambios.service.ts`

Responsabilidades:

- Consumir endpoints de historial de cambios.

Métodos:

- `getHistorial()`
- `agregarHistorial(entry)`
- `filtrarHistorial(filtros)`

Filtros soportados:

```ts
{
  usuario?: string;
  campo?: string;
  id?: number;
  fechaInicio?: string;
  fechaFin?: string;
}
```

El filtro `id` se envía al backend como `user_id`.

---

### 6.6 `DynamicsService`

Archivo: `src/app/services/dynamics.service.ts`

Responsabilidades:

- Consultar datos de contrato en Dynamics.

Endpoint:

```txt
GET http://190.4.222.148:1000/validar_dynamics?id=<idProyecto>
```

Método:

- `getContrato(idProyecto)`

---

### 6.7 `FormFieldsService` (nuevo)

Archivo: `src/app/services/form-fields.service.ts`

Responsabilidades:

- Consultar el catálogo de "campos personalizados" (capa dinámica/EAV) que se muestran en el formulario de `TablaPage`.
- Permitir crear nuevos campos personalizados (pensado para una futura pantalla de administración).

Métodos:

- `getFields(soloActivos = true)`
- `createField(field)`

Endpoint:

```txt
GET  http://127.0.0.1:8000/api/form-fields/?active=true
POST http://127.0.0.1:8000/api/form-fields
```

Interfaz `FormField`:

```ts
FormField {
  id?: number;
  name: string;
  data_type: string;    // 'string' | 'number' | 'boolean' (usados hoy en el formulario)
  required: boolean;
  active: boolean;
  display_order: number;
}
```

Importante para backend/integración:

- A diferencia del resto de servicios, `FormFieldsService` **no usa `ApiService`** ni `environment.apiBaseUrl`. Usa `HttpClient` directamente y tiene la URL base `http://127.0.0.1:8000/api/form-fields` **hardcodeada**. Esto significa que no respeta la configuración de entorno (`environment.prod.ts`) y habría que corregirlo antes de un despliegue a producción.
- Los valores que el usuario ingresa para estos campos se envían dentro de `registro.custom_fields` al crear/editar un registro en `/registros/` (ver `TablaService` y `TablaPage`), no a través de este servicio. Este servicio solo trae la *definición* de los campos (metadatos), no guarda sus valores.

---

### 6.8 `ExternalImportService`

Archivo: `src/app/services/external-import.service.ts`

Responsabilidades:

- Validar ruta de importación.
- Importar proyectos externos.

Endpoints:

- `GET /import/ping`
- `POST /import/external-projects`

Este servicio existe, pero no se encontró uso desde las páginas actuales.

---

## 7. Integración con backend FastAPI

URL base de desarrollo:

```txt
http://127.0.0.1:8000/api
```

Configurada en:

```txt
src/environments/environment.ts
```

### Endpoints consumidos

#### Login

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/login/` | Iniciar sesión |
| `GET` | `/login/usuario/{user_id}` | Obtener usuario por ID |

Payload de login:

```ts
{
  correo: string;
  password: string;
}
```

---

#### Usuarios

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/usuarios/` | Listar usuarios |
| `POST` | `/usuarios/` | Crear usuario |
| `PUT` | `/usuarios/{id}` | Editar usuario |
| `DELETE` | `/usuarios/{id}` | Eliminar usuario |

---

#### Registros

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/registros/` | Listar registros |
| `GET` | `/registros/{id}` | Obtener registro |
| `POST` | `/registros/` | Crear registro |
| `PUT` | `/registros/{id}` | Actualizar registro |
| `DELETE` | `/registros/{id}` | Eliminar registro |

Cambios recientes que afectan al backend:

- `POST`, `PUT` y `DELETE` ahora envían el header `X-User-Id` con el ID del usuario logueado (antes solo `POST`/`PUT` lo enviaban). Ver [`TablaService`](#64-tablaservice).
- El body de `POST`/`PUT` ahora puede incluir un nodo adicional `custom_fields: { [nombreCampo]: valor }` con los valores de los campos dinámicos definidos en `form-fields`. El backend debe poder aceptar y persistir este nodo (pensado como estructura EAV/JSON flexible).

---

#### Campos personalizados / dinámicos (`form-fields`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/form-fields/?active=true` | Listar catálogo de campos activos |
| `POST` | `/form-fields` | Crear un nuevo campo personalizado |

Nota: el frontend llama a esta API con la URL absoluta `http://127.0.0.1:8000/api/form-fields` hardcodeada (no usa `environment.apiBaseUrl`). Ver [`FormFieldsService`](#67-formfieldsservice-nuevo).

---

#### Historial

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/historial/` | Obtener historial completo |
| `POST` | `/historial/` | Agregar entrada de historial |
| `GET` | `/historial/filtrar` | Filtrar historial en backend |

---

#### Importación externa

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/import/ping` | Validar ruta |
| `POST` | `/import/external-projects` | Importar proyectos externos |

---

## 8. Integración con Dynamics

La app consulta Dynamics desde la página de registros.

Cuando el usuario ingresa `JusttimeNumber`, se ejecuta `buscarContrato()`.

Endpoint:

```txt
GET http://190.4.222.148:1000/validar_dynamics?id=<JusttimeNumber>
```

Campos que se rellenan desde la respuesta:

- `Department`
- `Contrato`
- `Instalacion`
- `Zone`
- `Activity`
- `Company`
- `Management`
- `Responsible`
- `EstadoContrato`
- `EstadoInstalacion`
- `NombreGrupo`
- `NombreInstalacion`

---

## 9. Autenticación y flujo de login

El flujo de login es:

1. El usuario entra a `/login`.
2. Ingresa correo y contraseña.
3. `LoginPage` llama a `LoginService.login()`.
4. `LoginService` hace `POST /login/`.
5. Si el backend responde correctamente, se guarda `usuarioSesion`.
6. El usuario es redirigido según su rol:

| Rol | Redirección |
|---|---|
| `Administrador` | `/gestion-usuarios` |
| `Editor` | `/tabla` |
| `Visualizador` | `/historial-cambios` |

7. Al cerrar sesión, se elimina `usuarioSesion` de `localStorage`.

Cambio reciente: la sesión ahora también se restaura automáticamente si el usuario recarga la página (F5) o vuelve a abrir la app, porque `LoginService` lee `localStorage` en su `constructor` y repuebla `usuario$`. Antes, un refresco de página podía dejar a las páginas sin usuario en memoria hasta la próxima navegación.

---

## 10. Guard de roles

Archivo: `src/app/guards/role.guard.ts`

El guard usa `LoginService.usuario$` para validar el rol del usuario contra `route.data.roles`.

Si el usuario no tiene permiso, lo redirige:

| Rol | Redirección |
|---|---|
| `Administrador` | `/gestion-usuarios` |
| `Editor` | `/tabla` |
| `Visualizador` | `/historial-cambios` |
| Sin sesión | `/login` |

Cambio reciente:

- Antes, `canActivate()` era síncrono: leía `getUsuarioSesion()` una sola vez y devolvía `boolean` (si no tenía permiso, siempre redirigía a `/login`).
- Ahora `canActivate()` devuelve `Observable<boolean | UrlTree>` y se suscribe a `LoginService.usuario$` con `map()`. Esto lo hace reactivo a cambios de sesión (por ejemplo, justo después de un `login()` o `logout()`) sin depender de que Angular vuelva a evaluar el guard manualmente.
- Cuando el usuario no tiene el rol permitido para la ruta, en vez de mandarlo siempre a `/login`, ahora lo redirige según **su propio rol actual** (misma tabla de arriba). Solo si no hay sesión (`usuario` es `null`) cae a `/login`.

---

## 11. Estado y gestión de datos

La app no usa Redux, NgRx ni un store global formal.

### Estado de sesión

Administrado por `LoginService`.

Usa:

- `localStorage`
- `BehaviorSubject`

Observable:

```ts
usuario$
```

Clave de localStorage:

```txt
usuarioSesion
```

Cambio reciente: `usuario$` pasó de ser un observable poco usado a ser la fuente de verdad reactiva de la sesión. Ahora `RoleGuard`, `TablaPage`, `GestionUsuariosPage` y `HistorialCambiosPage` se suscriben todos a `usuario$` (en vez de llamar a `getUsuarioSesion()` una sola vez en `ngOnInit()`), por lo que el rol mostrado/usado en cada página se actualiza automáticamente si la sesión cambia.

---

### Estado de registros

Administrado parcialmente por `TablaService`.

Usa:

```ts
BehaviorSubject<Registro[]>
```

Observable:

```ts
registros$
```

Aunque existe este observable, las páginas trabajan principalmente con arrays locales:

- `registros`
- `registrosFiltrados`
- `historialCompleto`
- `historialFiltrado`
- `usuarios`
- `usuariosFiltrados`

---

## 12. Modelos e interfaces principales

### 12.1 Login

Archivo: `src/app/services/login.service.ts`

```ts
UsuarioLogin {
  correo: string;
  password: string;
}

UsuarioSesion {
  id: number;
  nombre: string;
  correo: string;
  rol: 'Administrador' | 'Editor' | 'Visualizador' | string;
}
```

---

### 12.2 Usuarios

Archivo: `src/app/services/gestion-usuario.service.ts`

```ts
Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol_id: number;
  activo: boolean;
}

UsuarioCreate {
  nombre: string;
  correo: string;
  password: string;
  rol_id: number;
  activo?: boolean;
}

UsuarioUpdate {
  nombre?: string;
  correo?: string;
  password?: string;
  rol_id?: number;
  activo?: boolean;
}
```

---

### 12.3 Registros

Archivo: `src/app/services/tabla.service.ts`

```ts
Registro
```

Campos principales:

- `AccidentID`
- `Unico`
- `JusttimeNumber`
- `InitialDate`
- `Year`
- `IDEntidad`
- `Demandant`
- `Defendant`
- `Supervisor`
- `JOP`
- `ZonalDelegate`
- `Zone`
- `Activity`
- `AccountingKey`
- `ClaimedAmount`
- `EstimatedAmount`
- `PreviousProvision`
- `AdditionalDemand`
- `NonProvisionedAmount`
- `ReversalAmount`
- `FinalCost`
- `FinalAttorneyCost`
- `OtherExpenses`
- `CloseDate`
- `CloseComment`
- `Management`
- `Responsible`
- `AppliedMeasure`
- `Dimensions`
- `BeenProcessing`
- `PenaltyNumber`
- `Categoria`
- `InspectionDate`
- `PeriodoFiscalizado`
- `Department`
- `DimensionesFinal`
- `Comentarios`
- `EstadoContrato`
- `EstadoInstalacion`
- `NombreGrupo`
- `NombreInstalacion`

Relaciones anidadas:

- `Company`
- `Country`
- `Type`
- `State`
- `Matter`
- `Category1`
- `Category2`
- `Category3`

Normalización:

- El frontend convierte objetos relacionales como `{ Name: 'X' }` a strings.

Serialización:

- El frontend convierte strings relacionales a objetos como `{ Name: 'X' }` antes de enviar al backend.

Campo nuevo — `custom_fields`:

- Al guardar un registro, el frontend agrega `custom_fields: { [nombreCampo]: valor }` con los valores capturados para los campos dinámicos definidos en `FormFieldsService` (ver sección 6.7). El backend debe soportar persistir y devolver este nodo tal cual.

---

### 12.4 Historial

Archivo: `src/app/services/historial-cambios.service.ts`

```ts
HistorialEntry {
  id: number;
  user_id: number;
  accident_id: number;
  tipo_accion: string;
  seccion_afectada?: string | null;
  campo_afectado?: string | null;
  valor_anterior?: string | null;
  valor_nuevo?: string | null;
  fecha: string;
}

HistorialCreate {
  user_id: number;
  accident_id: number;
  tipo_accion: string;
  seccion_afectada?: string;
  campo_afectado?: string;
  valor_anterior?: string;
  valor_nuevo?: string;
}
```

---

### 12.5 Campos personalizados (nuevo)

Archivo: `src/app/services/form-fields.service.ts`

```ts
FormField {
  id?: number;
  name: string;
  data_type: string; // 'string' | 'number' | 'boolean'
  required: boolean;
  active: boolean;
  display_order: number;
}
```

---

## 13. Dependencias

Archivo: `package.json`

### Dependencias principales

- `@angular/animations`
- `@angular/common`
- `@angular/compiler`
- `@angular/core`
- `@angular/forms`
- `@angular/platform-browser`
- `@angular/platform-browser-dynamic`
- `@angular/router`
- `@capacitor/app`
- `@capacitor/core`
- `@capacitor/haptics`
- `@capacitor/keyboard`
- `@capacitor/status-bar`
- `@ionic/angular`
- `ionicons`
- `rxjs`
- `tslib`
- `zone.js`

### Dependencias de desarrollo

- `@angular-devkit/build-angular`
- `@angular-eslint/builder`
- `@angular-eslint/eslint-plugin`
- `@angular-eslint/eslint-plugin-template`
- `@angular-eslint/schematics`
- `@angular-eslint/template-parser`
- `@angular/cli`
- `@angular/compiler-cli`
- `@angular/language-service`
- `@capacitor/cli`
- `@ionic/angular-toolkit`
- `@types/jasmine`
- `@typescript-eslint/eslint-plugin`
- `@typescript-eslint/parser`
- `eslint`
- `eslint-plugin-import`
- `eslint-plugin-jsdoc`
- `eslint-plugin-prefer-arrow`
- `jasmine-core`
- `jasmine-spec-reporter`
- `karma`
- `karma-chrome-launcher`
- `karma-coverage`
- `karma-jasmine`
- `karma-jasmine-html-reporter`
- `typescript`

---

## 14. Comandos

Desde la carpeta del frontend:

```bash
cd gestion-datos/gestion-datos
```

### Instalar dependencias

```bash
npm install
```

### Iniciar servidor de desarrollo

```bash
npm start
```

Equivale a:

```bash
ng serve
```

### Build de producción

```bash
npm run build
```

Equivale a:

```bash
ng build
```

### Watch mode

```bash
npm run watch
```

Equivale a:

```bash
ng build --watch --configuration development
```

### Tests

```bash
npm test
```

Equivale a:

```bash
ng test
```

### Lint

```bash
npm run lint
```

Equivale a:

```bash
ng lint
```

---

## 15. Observaciones importantes

- La app usa Angular standalone, no `AppModule`.
- No usa NgRx ni Redux.
- La sesión se guarda en `localStorage`.
- `ApiService` intenta usar un token desde `localStorage`, pero el login actual solo guarda `usuarioSesion`, no guarda `token`.
- `environment.prod.ts` no define `apiBaseUrl`, por lo que la URL base del backend puede faltar en builds de producción.
- La URL de Dynamics está hardcodeada.
- `ExternalImportService` existe, pero no está usado por las páginas actuales.
- Las páginas usan arrays locales para mostrar datos, aunque algunos servicios exponen observables.
- **(Nuevo)** `FormFieldsService` tiene su URL base (`http://127.0.0.1:8000/api/form-fields`) hardcodeada y usa `HttpClient` en vez de `ApiService`, por lo que no respeta `environment.apiBaseUrl` — hay que alinearlo con el resto de servicios antes de producción.
- **(Nuevo)** `TablaPage.eliminarRegistro(id)` está implementado en el `.ts` y llama al backend, pero no hay botón "Eliminar" en `tabla.page.html` todavía; solo hay botón "Editar".
- **(Nuevo)** La sesión (`usuario$`) ahora es reactiva y se restaura desde `localStorage` al recargar la página; antes se leía una sola vez por página vía `getUsuarioSesion()`.
- **(Nuevo)** El `RoleGuard` ahora es asíncrono (`Observable<boolean | UrlTree>`) y redirige según el rol real del usuario en vez de mandar siempre a `/login` cuando no tiene permiso.
- **(Nuevo)** Se agregó la capa de "campos personalizados" (EAV): catálogo vía `FormFieldsService`/`GET /form-fields`, valores capturados en `registroNuevo.custom_fields` y enviados junto con el resto del payload de `/registros/`. El backend debe soportar este nodo en el modelo de `Registro`.
- Se eliminaron `package.json`/`package-lock.json` duplicados que existían en la raíz del repositorio (fuera de la carpeta del proyecto Angular); las dependencias reales del frontend siguen viviendo en `gestion-datos/gestion-datos/package.json`.
