# Mapa de Arquitectura - Carpetas, Archivos y Documentos

## Proyecto: gestion-datos

---

## 1. Estructura General del Repositorio

```
gestion-datos/                              (raiz del repositorio)
├─ gestion-datos/                           (proyecto frontend Angular/Ionic)
├─ node_modules/                            (dependencias del proyecto principal)
├─ analisis.docx                            (documento: análisis de factibilidad)
├─ resumen.docx                             (documento: resumen del proyecto)
├─ basescript.ipynb                         (script base de análisis)
└─ .gitattributes                           (configuracion git)
```

### 1.1 gestion-datos/gestion-datos/ (Proyecto Frontend)

```
gestion-datos/gestion-datos/
├─ angular.json                             (configuracion Angular CLI)
├─ package.json                             (dependencias y scripts)
├─ package-lock.json                        (lockfile de dependencias)
├─ capacitor.config.ts                      (configuracion Capacitor - movil/hibrido)
├─ ionic.config.json                        (configuracion Ionic)
├─ tsconfig.json                            (configuracion TypeScript base)
├─ tsconfig.app.json                        (configuracion TypeScript para app)
├─ tsconfig.spec.json                       (configuracion TypeScript para tests)
├─ karma.conf.js                            (configuracion Karma para tests)
├─ .browserslistrc                          (navegadores soportados)
├─ .editorconfig                            (configuracion de editor)
├─ .eslintrc.json                           (reglas ESLint)
├─ .gitignore                               (archivos ignorados por git)
├─ .angular/                                (cache de Angular)
├─ .vscode/                                 (configuracion VS Code)
├─ DOCUMENTACION_FRONTEND.md                (documentacion tecnica frontend)
├─ src/                                     (codigo fuente principal)
│  ├─ main.ts                               (punto de entrada de la app)
│  ├─ index.html                            (HTML base)
│  ├─ polyfills.ts                          (polyfills para compatibilidad)
│  ├─ global.scss                           (estilos globales)
│  ├─ zone-flags.ts                         (configuracion Zone.js)
│  ├─ test.ts                               (configuracion de test environment)
│  ├─ assets/                               (recursos estaticos)
│  │  ├─ logo.png                           (logo de la aplicacion)
│  │  ├─ eulen.jpeg                         (imagen Eulen)
│  │  ├─ shapes.svg                         (formas decorativas SVG)
│  │  ├─ guia.txt                           (guia de referencias)
│  │  └─ icon/                              (iconos)
│  ├─ environments/                         (variables de entorno)
│  │  ├─ environment.ts                     (variables desarrollo)
│  │  └─ environment.prod.ts                (variables produccion)
│  ├─ theme/                                (estilos y temas)
│  │  └─ variables.scss                     (variables SCSS/Ionic)
│  └─ app/                                  (codigo de la aplicacion)
│     ├─ app.component.html                 (template del componente raiz)
│     ├─ app.component.scss                 (estilos del componente raiz)
│     ├─ app.component.spec.ts              (tests del componente raiz)
│     ├─ app.component.ts                   (componente raiz - standalone)
│     ├─ app.routes.ts                      (definicion de rutas)
│     ├─ guards/                             (guards de navegacion)
│     │  ├─ role.guard.ts                   (guard por rol de usuario)
│     │  └─ role.guard.spec.ts               (tests del guard)
│     ├─ pages/                              (paginas/modulos de la app)
│     │  ├─ login/                           (pantalla de autenticacion)
│     │  │  ├─ login.page.html              (template)
│     │  │  ├─ login.page.scss              (estilos)
│     │  │  ├─ login.page.spec.ts           (tests)
│     │  │  └─ login.page.ts                (logica componente)
│     │  ├─ gestion-usuarios/                (administracion de usuarios)
│     │  │  ├─ gestion-usuarios.page.html   (template)
│     │  │  ├─ gestion-usuarios.page.scss   (estilos)
│     │  │  ├─ gestion-usuarios.page.spec.ts (tests)
│     │  │  └─ gestion-usuarios.page.ts     (logica componente)
│     │  ├─ tabla/                           (gestion de registros principales)
│     │  │  ├─ tabla.page.html              (template)
│     │  │  ├─ tabla.page.scss              (estilos)
│     │  │  ├─ tabla.page.spec.ts           (tests)
│     │  │  └─ tabla.page.ts                (logica componente)
│     │  └─ historial-cambios/               (historial de cambios)
│     │     ├─ historial-cambios.page.html  (template)
│     │     ├─ historial-cambios.page.scss  (estilos)
│     │     ├─ historial-cambios.page.spec.ts (tests)
│     │     └─ historial-cambios.page.ts    (logica componente)
│     └─ services/                           (servicios de negocio y API)
│        ├─ api.service.ts                  (servicio HTTP generico)
│        ├─ api.service.spec.ts             (tests)
│        ├─ login.service.ts                (autenticacion y sesion)
│        ├─ tabla.service.ts                (logica de registros)
│        ├─ gestion-usuario.service.ts       (logica de usuarios)
│        ├─ historial-cambios.service.ts     (logica de historial)
│        ├─ dynamics.service.ts              (integracion Dynamics)
│        ├─ external-import.service.ts       (importacion externa)
│        └─ external-import.service.spec.ts  (tests)
└─ node_modules/                             (dependencias del proyecto frontend)
```

---

## 2. Mapa de Dependencias Entre Modulos

```
                        main.ts
                          |
                  bootstrapApplication
                          |
              ┌───────────┴───────────┐
              |                       |
        app.component.html         app.routes.ts
              |                       |
        ion-router-outlet            |
                                      |
                         ┌────────────┼────────────┐
                         |            |             |
                      /login     /gestion-usuarios  /tabla   /historial-cambios
                         |            |             |
                     LoginPage   GestionUsuarios  TablaPage  HistorialCambiosPage
                         |            |             |
                   LoginService  GestionUsuarios  TablaService  HistorialCambiosService
                                         |             |
                                    RoleGuard        ApiService
                                                      |
                                              ┌────────┴────────┐
                                              |                 |
                                        DynamicsService   ExternalImportService
```

---

## 3. Mapa de Servicios y Endpoints Backend

```
ApiService (HTTP generico)
├─ get<T>()        → cualquier GET
├─ post<T>()       → cualquier POST
├─ put<T>()        → cualquier PUT
├─ patch<T>()      → cualquier PATCH
└─ delete<T>()     → cualquier DELETE

LoginService
├─ login()         → POST /login/
└─ obtenerUsuario  → GET /login/usuario/{user_id}

GestionUsuariosService
├─ getUsuarios()           → GET /usuarios/
├─ agregarUsuario()        → POST /usuarios/
├─ editarUsuario()         → PUT /usuarios/{id}
└─ eliminarUsuario()       → DELETE /usuarios/{id}

TablaService
├─ obtenerRegistros()      → GET /registros/
├─ obtenerRegistro()       → GET /registros/{id}
├─ agregarRegistro()       → POST /registros/
├─ actualizarRegistro()    → PUT /registros/{id}
└─ eliminarRegistro()      → DELETE /registros/{id}

HistorialCambiosService
├─ getHistorial()          → GET /historial/
├─ agregarHistorial()      → POST /historial/
└─ filtrarHistorial()      → GET /historial/filtrar

DynamicsService
└─ getContrato()           → GET http://190.4.222.148:1000/validar_dynamics

ExternalImportService
├─ ping()                  → GET /import/ping
└─ importarProyectos()     → POST /import/external-projects
```

---

## 4. Mapa de Rutas y Acceso por Rol

```
/                     → redirige a /login
/login                (publico)
    └─ LoginPage
        └─ LoginService

/gestion-usuarios     (Administrador)
    └─ GestionUsuariosPage
        ├─ GestionUsuariosService
        └─ RoleGuard

/tabla                (Administrador, Editor, Visualizador)
    └─ TablaPage
        ├─ TablaService
        ├─ DynamicsService
        └─ RoleGuard

/historial-cambios    (Administrador, Editor, Visualizador)
    └─ HistorialCambiosPage
        ├─ HistorialCambiosService
        └─ RoleGuard

**                    → redirige a /login
```

---

## 5.Mapa de Estado de la Aplicacion

```
Estado de Sesion (LoginService)
├─ localStorage: 'usuarioSesion'
├─ usuarioSubject: BehaviorSubject<UsuarioSesion | null>
└─ usuario$: Observable<UsuarioSesion | null>

Estado de Registros (TablaService)
├─ registrosSubject: BehaviorSubject<Registro[]>
└─ registros$: Observable<Registro[]>

Estado Local en Paginas
├─ TablaPage: registros[], registrosFiltrados[]
├─ GestionUsuariosPage: usuarios[], usuariosFiltrados[]
├─ HistorialCambiosPage: historialCompleto[], historialFiltrado[]
```

---

## 6. Documentos Externos del Proyecto

```
gestion-datos/
├─ analisis.docx        → Analisis de factibilidad campos dinamicos
│                          Incluye: evaluacion EAV, JSON, ALTER TABLE
│                          Propuesta hibrida (Core + Dinamicos)
│                          Fase 1 y Fase 2
│
└─ resumen.docx         → Resumen ejecutivo del proyecto
                           Stack tecnologico, arquitectura,
                           endpoints, servicios, modelos
```

---

## 7. Stack Tecnologico

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Framework Frontend | Angular | 20 |
| UI Framework | Ionic Angular | 8 |
| Lenguaje | TypeScript | ~5.8.0 |
| Runtime Móvil | Capacitor | 7.x |
| HTTP Client | Angular HttpClient | - |
| Programacion Reactiva | RxJS | ~7.8.0 |
| Estilos | SCSS + Ionic | - |
| Backend | FastAPI | (externo) |
| Base de Datos | SQL Server | (externo) |
| Integracion | Dynamics 365 | - |

---

## 8. Directorios del Proyecto Frontend

| Ruta | Proposito |
|------|-----------|
| `src/` | Codigo fuente raiz |
| `src/app/` | Componentes, paginas, servicios |
| `src/app/pages/` | Paginas principales de la app |
| `src/app/services/` | Servicios HTTP y negocio |
| `src/app/guards/` | Proteccion de rutas |
| `src/assets/` | Imagenes, SVG, recursos estaticos |
| `src/environments/` | Variables de configuracion |
| `src/theme/` | Estilos globales y variables |
| `node_modules/` | Dependencias npm |

---

## 9. Tipos de Archivo por Extension

| Extension | Cantidad | Descripcion |
|-----------|----------|-------------|
| `.ts` | 18 | TypeScript - logica |
| `.html` | 4 | Ionic templates |
| `.scss` | 3 | Estilos |
| `.spec.ts` | 4 | Tests unitarios |
| `.ts` (config) | 5 | Configuracion TypeScript |
| `.json` | 4 | Config JSON (package, angular, tsconfig) |
| `.md` | 2 | Documentacion |
| `.docx` | 2 | Documentos Word (raiz) |
| `.ipynb` | 1 | Script Jupyter (raiz) |
| `.png` | 1 | Imagen logo |
| `.jpeg` | 1 | Imagen Eulen |
| `.svg` | 1 | Formas SVG |
| `.txt` | 1 | Guia de referencias |
