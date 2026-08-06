import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonInput,
  IonItem,
  IonLabel,
  IonButton,
  IonSelect,
  IonSelectOption,
  IonToggle,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButtons, // necesario para <ion-buttons> en el header
  IonMenuButton,
} from '@ionic/angular/standalone';

import {
  GestionUsuariosService,
  Usuario,
  UsuarioCreate,
  UsuarioUpdate,
} from '../../services/gestion-usuario.service';
import { LoginService, UsuarioSesion } from '../../services/login.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription } from 'rxjs';

type CampoNombre = 'nombre' | 'correo' | 'password' | 'rol_id' | 'activo';

@Component({
  selector: 'app-gestion-usuarios',
  templateUrl: './gestion-usuarios.page.html',
  styleUrls: ['./gestion-usuarios.page.scss'],
  standalone: true,
  imports: [
    IonButtons, // para que no de el error 'ion-buttons is not a known element'
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonInput,
    IonItem,
    IonLabel,
    IonButton,
    IonSelect,
    IonSelectOption,
    IonToggle,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonMenuButton,
  ],
})
export class GestionUsuariosPage implements OnInit, OnDestroy {
  // === Propiedades principales ===
  rolUsuarioLogueado: 'Administrador' | 'Editor' | 'Visualizador' | string = '';
  usuarioActual: UsuarioSesion | null = null;
  private subUsuario!: Subscription;

  usuarios: Usuario[] = [];
  filtroEstado: 'todos' | 'activos' | 'inactivos' = 'todos';
  usuariosFiltrados: Usuario[] = [];

  // === Nuevo usuario ===
  nuevoUsuario: Partial<UsuarioCreate> = { activo: true };

  camposUsuario: {
    nombre: CampoNombre;
    tipo: 'input' | 'password' | 'select' | 'toggle';
    opciones?: Array<{ label: string; value: number }>;
  }[] = [
    { nombre: 'nombre', tipo: 'input' },
    { nombre: 'correo', tipo: 'input' },
    { nombre: 'password', tipo: 'password' },
    {
      nombre: 'rol_id',
      tipo: 'select',
      opciones: [
        { label: 'Administrador', value: 1 },
        { label: 'Editor', value: 2 },
        { label: 'Visualizador', value: 3 },
      ],
    },
    { nombre: 'activo', tipo: 'toggle' },
  ];

  rolLabelMap = new Map<number, string>([
    [1, 'Administrador'],
    [2, 'Editor'],
    [3, 'Visualizador'],
  ]);

  constructor(
    private usuarioService: GestionUsuariosService,
    private loginService: LoginService,
    private notification: NotificationService
  ) {}

  // ============================================================
  // Ciclo de vida
  // ============================================================
  ngOnInit() {
    // Suscribirse a los cambios del usuario en sesión
    this.subUsuario = this.loginService.usuario$.subscribe((user) => {
      this.usuarioActual = user;
      this.rolUsuarioLogueado = user?.rol || '';
      console.log('👤 Rol activo:', this.rolUsuarioLogueado);
    });

    this.cargarUsuarios();
  }

  ngOnDestroy() {
    if (this.subUsuario) this.subUsuario.unsubscribe();
  }

  // ============================================================
  // CRUD Usuarios
  // ============================================================
  rolLabel(id?: number) {
    return id != null ? (this.rolLabelMap.get(id) ?? '—') : '—';
  }

  cargarUsuarios() {
    this.usuarioService.getUsuarios().subscribe({
      next: (data: Usuario[]) => {
        this.usuarios = data;
        this.aplicarFiltro();
      },
      error: (err: any) =>
        this.notification.error('Error cargando usuarios: ' + err.message),
    });
  }

  agregarUsuario() {
    if (!this.puedeAgregar()) {
      this.notification.error('Solo un Administrador puede agregar usuarios.');
      return;
    }

    if (
      !this.nuevoUsuario.nombre ||
      !this.nuevoUsuario.correo ||
      !this.nuevoUsuario.password ||
      !this.nuevoUsuario.rol_id
    ) {
      this.notification.error('Nombre, correo, password y rol son obligatorios.');
      return;
    }

    this.usuarioService
      .agregarUsuario(this.nuevoUsuario as UsuarioCreate)
      .subscribe({
        next: () => {
          this.nuevoUsuario = { activo: true };
          this.cargarUsuarios();
          this.notification.success('Usuario agregado correctamente.');
        },
        error: (err: any) =>
          this.notification.error('Error al agregar usuario: ' + err.message),
      });
  }

  editarCampoUsuario(id: number, campo: any, valor: any) {
    if (!this.puedeEditar()) {
      this.notification.error('Solo un Administrador puede editar usuarios.');
      return;
    }

    const payload: UsuarioUpdate = { [campo]: valor } as UsuarioUpdate;

    this.usuarioService.editarUsuario(id, payload).subscribe({
      next: () => this.cargarUsuarios(),
      error: (err: any) =>
        this.notification.error('Error al editar usuario: ' + err.message),
    });
  }

  // ============================================================
  // Filtro
  // ============================================================
  aplicarFiltro() {
    if (this.filtroEstado === 'activos') {
      this.usuariosFiltrados = this.usuarios.filter((u) => u.activo);
    } else if (this.filtroEstado === 'inactivos') {
      this.usuariosFiltrados = this.usuarios.filter((u) => !u.activo);
    } else {
      this.usuariosFiltrados = [...this.usuarios];
    }
  }

  // ============================================================
  // Permisos
  // ============================================================
  puedeAgregar(): boolean {
    return this.rolUsuarioLogueado === 'Administrador';
  }

  puedeEditar(): boolean {
    return this.rolUsuarioLogueado === 'Administrador';
  }

  canAccess(): boolean {
    return this.rolUsuarioLogueado === 'Administrador';
  }
}
