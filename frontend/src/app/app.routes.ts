// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { RoleGuard } from './guards/role.guard';

export const routes: Routes = [
  // Página inicial → login
  { path: '', redirectTo: 'login', pathMatch: 'full' },

  // Login (sin guard)
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/login/login.page').then((m) => m.LoginPage),
  },

  // Gestión de Usuarios → solo Administrador
  {
    path: 'gestion-usuarios',
    loadComponent: () =>
      import('./pages/gestion-usuarios/gestion-usuarios.page').then(
        (m) => m.GestionUsuariosPage
      ),
    canActivate: [RoleGuard],
    data: { roles: ['Administrador'] },
  },

  // Tabla → todos los roles pueden entrar
  {
    path: 'tabla',
    loadComponent: () =>
      import('./pages/tabla/tabla.page').then((m) => m.TablaPage),
    canActivate: [RoleGuard],
    data: { roles: ['Administrador', 'Editor', 'Visualizador'] },
  },

  // Historial de Cambios → todos los roles pueden entrar
  {
    path: 'historial-cambios',
    loadComponent: () =>
      import('./pages/historial-cambios/historial-cambios.page').then(
        (m) => m.HistorialCambiosPage
      ),
    canActivate: [RoleGuard],
    data: { roles: ['Administrador', 'Editor', 'Visualizador'] },
  },

  // Campos Dinámicos → solo Administrador
  {
    path: 'campos-dinamicos',
    loadComponent: () =>
      import('./pages/campos-dinamicos/campos-dinamicos.page').then(
        (m) => m.CamposDinamicosPage
      ),
    canActivate: [RoleGuard],
    data: { roles: ['Administrador'] },
  },

  // Ruta comodín para URLs no válidas
  { path: '**', redirectTo: 'login' },
];
