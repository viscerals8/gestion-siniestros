import { Component, OnInit, OnDestroy, inject } from '@angular/core';
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
  IonButtons,
  IonMenuButton,
} from '@ionic/angular/standalone';

import {
  FormFieldsService,
  FormField,
  FormFieldCreate,
  FormFieldUpdate,
} from '../../services/form-fields.service';
import { LoginService, UsuarioSesion } from '../../services/login.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription } from 'rxjs';

// Tipos de dato soportados hoy por el formulario dinámico de TablaPage.
// Si agregas un tipo nuevo aquí, primero debes agregar su renderizado en tabla.page.html.
const TIPOS_SOPORTADOS: Array<{ label: string; value: string }> = [
  { label: 'Texto', value: 'string' },
  { label: 'Número', value: 'number' },
  { label: 'Sí / No', value: 'boolean' },
];

@Component({
  selector: 'app-campos-dinamicos',
  templateUrl: './campos-dinamicos.page.html',
  styleUrls: ['./campos-dinamicos.page.scss'],
  standalone: true,
  imports: [
    IonButtons,
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
export class CamposDinamicosPage implements OnInit, OnDestroy {
  private formFieldsService = inject(FormFieldsService);
  private loginService = inject(LoginService);
  private notification = inject(NotificationService);

  rolUsuarioLogueado: 'Administrador' | 'Editor' | 'Visualizador' | string = '';
  usuarioActual: UsuarioSesion | null = null;
  private subUsuario!: Subscription;

  tiposDisponibles = TIPOS_SOPORTADOS;

  campos: FormField[] = [];
  camposFiltrados: FormField[] = [];
  filtroEstado: 'todos' | 'activos' | 'inactivos' = 'todos';
  cargando = false;

  nuevoCampo: Partial<FormFieldCreate> = {
    data_type: 'string',
    required: false,
    active: true,
    display_order: 0,
  };

  ngOnInit() {
    this.subUsuario = this.loginService.usuario$.subscribe((user) => {
      this.usuarioActual = user;
      this.rolUsuarioLogueado = user?.rol || '';
    });

    this.cargarCampos();
  }

  ngOnDestroy() {
    if (this.subUsuario) this.subUsuario.unsubscribe();
  }

  // ============================================================
  // CRUD Campos Dinámicos
  // ============================================================
  cargarCampos() {
    this.cargando = true;
    // Se listan todos (activos e inactivos) porque este es el panel de administración,
    // no el formulario de siniestros (ese sigue pidiendo solo los activos).
    this.formFieldsService.getFields(false).subscribe({
      next: (data: FormField[]) => {
        this.campos = data || [];
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err: any) => {
        this.notification.error('Error cargando campos dinámicos: ' + err.message);
        this.cargando = false;
      },
    });
  }

  aplicarFiltro() {
    if (this.filtroEstado === 'activos') {
      this.camposFiltrados = this.campos.filter((c) => c.active);
    } else if (this.filtroEstado === 'inactivos') {
      this.camposFiltrados = this.campos.filter((c) => !c.active);
    } else {
      this.camposFiltrados = [...this.campos];
    }
  }

  agregarCampo() {
    if (!this.puedeAdministrar()) {
      this.notification.error('Solo un Administrador puede crear campos dinámicos.');
      return;
    }

    const nombre = (this.nuevoCampo.name || '').trim();
    if (!nombre) {
      this.notification.error('El nombre del campo es obligatorio.');
      return;
    }

    if (!this.nuevoCampo.data_type) {
      this.notification.error('Debes elegir un tipo de dato.');
      return;
    }

    const yaExiste = this.campos.some(
      (c) => c.name.trim().toLowerCase() === nombre.toLowerCase()
    );
    if (yaExiste) {
      this.notification.error('Ya existe un campo con ese nombre.');
      return;
    }

    const payload: FormFieldCreate = {
      name: nombre,
      data_type: this.nuevoCampo.data_type,
      required: !!this.nuevoCampo.required,
      active: this.nuevoCampo.active !== false,
      display_order: this.nuevoCampo.display_order ?? 0,
    };

    this.formFieldsService.createField(payload).subscribe({
      next: () => {
        this.resetFormulario();
        this.cargarCampos();
        this.notification.success('Campo creado correctamente.');
      },
      error: (err: any) =>
        this.notification.error('Error al crear el campo: ' + err.message),
    });
  }

  editarCampo(id: number, campo: keyof FormFieldUpdate, valor: any) {
    if (!this.puedeAdministrar()) {
      this.notification.error('Solo un Administrador puede editar campos dinámicos.');
      return;
    }

    if (campo === 'name' && !String(valor).trim()) {
      this.notification.error('El nombre del campo no puede quedar vacío.');
      this.cargarCampos();
      return;
    }

    const payload: FormFieldUpdate = { [campo]: valor } as FormFieldUpdate;

    this.formFieldsService.updateField(id, payload).subscribe({
      next: () => this.cargarCampos(),
      error: (err: any) => {
        this.notification.error('Error al editar el campo: ' + err.message);
        this.cargarCampos();
      },
    });
  }

  async eliminarCampo(campo: FormField) {
    if (!this.puedeAdministrar()) {
      this.notification.error('Solo un Administrador puede eliminar campos dinámicos.');
      return;
    }

    const confirmado = await this.notification.confirm(
      `¿Eliminar el campo "${campo.name}"? Los valores ya guardados en registros existentes para este campo dejarán de mostrarse.`,
      'Eliminar campo'
    );
    if (!confirmado) return;

    this.formFieldsService.deleteField(campo.id as number).subscribe({
      next: () => {
        this.cargarCampos();
        this.notification.success('Campo eliminado.');
      },
      error: (err: any) =>
        this.notification.error('Error al eliminar el campo: ' + err.message),
    });
  }

  resetFormulario() {
    this.nuevoCampo = {
      data_type: 'string',
      required: false,
      active: true,
      display_order: 0,
    };
  }

  // ============================================================
  // Permisos
  // ============================================================
  puedeAdministrar(): boolean {
    return this.rolUsuarioLogueado === 'Administrador';
  }

  canAccess(): boolean {
    return this.rolUsuarioLogueado === 'Administrador';
  }

  tipoLabel(value: string): string {
    return this.tiposDisponibles.find((t) => t.value === value)?.label ?? value;
  }
}
