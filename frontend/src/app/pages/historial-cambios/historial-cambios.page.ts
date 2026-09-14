import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonItem,
  IonLabel,
  IonButton,
  IonList,
  IonDatetime,
  IonDatetimeButton,
  IonModal,
  IonSelect,
  IonSelectOption,
  IonInput,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButtons, // necesario para <ion-buttons> en el header
  IonMenuButton,
} from '@ionic/angular/standalone';

import { Subscription } from 'rxjs';
import { LoginService, UsuarioSesion } from '../../services/login.service';
import { HistorialCambiosService, HistorialEntry } from '../../services/historial-cambios.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-historial-cambios',
  templateUrl: './historial-cambios.page.html',
  styleUrls: ['./historial-cambios.page.scss'],
  standalone: true,
  imports: [
    IonButtons, // para que Angular reconozca <ion-buttons>
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonItem,
    IonLabel,
    IonButton,
    IonList,
    IonDatetime,
    IonDatetimeButton,
    IonModal,
    IonSelect,
    IonSelectOption,
    IonInput,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonMenuButton
  ],
})
export class HistorialCambiosPage implements OnInit, OnDestroy {
  private loginService = inject(LoginService);
  private historialService = inject(HistorialCambiosService);
  private notification = inject(NotificationService);

  // ============================================================
  // Variables base
  // ============================================================
  historialCompleto: HistorialEntry[] = [];
  historialFiltrado: HistorialEntry[] = [];

  filtroUsuario: string = '';
  filtroFechaInicio: string | null = null;
  filtroFechaFin: string | null = null;
  filtroCampo: string = '';
  filtroId: number | null = null;

  usuario: UsuarioSesion | null = null;
  rolUsuarioLogueado: 'Administrador' | 'Editor' | 'Visualizador' | string = '';

  private subUsuario!: Subscription;

  // Listas dinámicas para selectores
  usuariosDisponibles: string[] = [];
  camposDisponibles: string[] = [];

  cargando: boolean = false;

  // ============================================================
  // Ciclo de vida
  // ============================================================
  ngOnInit() {
    // Suscribirse a los cambios de sesión de usuario
    this.subUsuario = this.loginService.usuario$.subscribe((user) => {
      this.usuario = user;
      this.rolUsuarioLogueado = user?.rol || '';
      console.log('👤 Rol activo (historial):', this.rolUsuarioLogueado);
    });

    this.cargarHistorial();
  }

  ngOnDestroy() {
    if (this.subUsuario) this.subUsuario.unsubscribe();
  }

  // ============================================================
  // Permisos
  // ============================================================
  puedeEditar(): boolean {
    return (
      this.rolUsuarioLogueado === 'Administrador' ||
      this.rolUsuarioLogueado === 'Editor'
    );
  }

  // ============================================================
  // Cargar historial desde backend
  // ============================================================
  cargarHistorial() {
    this.cargando = true;
    this.historialService.getHistorial().subscribe({
      next: (data) => {
        this.historialCompleto = data;
        this.historialFiltrado = [...data];
        this.cargando = false;

        this.usuariosDisponibles = [
          ...new Set(data.map((d) => String(d.user_id))),
        ];

        this.camposDisponibles = [
          ...new Set(
            data
              .map((d) => d.campo_afectado)
              .filter((c) => !!c)
          ),
        ] as string[];

        console.log(
          '✅ Historial cargado:',
          this.historialCompleto.length,
          'registros'
        );
      },
      error: (err) => {
        console.error('❌ Error al cargar historial:', err);
        this.cargando = false;
      },
    });
  }

  // ============================================================
  // Aplicar filtros locales (frontend)
  // ============================================================
  aplicarFiltros() {
    let tempHistorial = [...this.historialCompleto];

    if (this.filtroId) {
      tempHistorial = tempHistorial.filter(
        (entry) => entry.user_id === this.filtroId
      );
    }

    if (this.filtroUsuario) {
      tempHistorial = tempHistorial.filter(
        (entry) => String(entry.user_id) === this.filtroUsuario
      );
    }

    if (this.filtroFechaInicio && this.filtroFechaFin) {
      const start = new Date(this.filtroFechaInicio).setHours(0, 0, 0, 0);
      const end = new Date(this.filtroFechaFin).setHours(23, 59, 59, 999);

      tempHistorial = tempHistorial.filter((entry) => {
        const entryDate = new Date(entry.fecha).getTime();
        return entryDate >= start && entryDate <= end;
      });
    }

    if (this.filtroCampo) {
      tempHistorial = tempHistorial.filter((entry) =>
        entry.campo_afectado
          ?.toLowerCase()
          .includes(this.filtroCampo.toLowerCase())
      );
    }

    this.historialFiltrado = tempHistorial;
  }

  // ============================================================
  // Aplicar filtros al backend (opcional)
  // ============================================================
  aplicarFiltrosBackend() {
    const filtros = {
      usuario: this.filtroUsuario || undefined,
      campo: this.filtroCampo || undefined,
      id: this.filtroId || undefined,
      fechaInicio: this.filtroFechaInicio || undefined,
      fechaFin: this.filtroFechaFin || undefined,
    };

    this.cargando = true;

    this.historialService.filtrarHistorial(filtros).subscribe({
      next: (data) => {
        this.historialFiltrado = data;
        this.cargando = false;
        console.log(
          '🔍 Filtro backend aplicado:',
          data.length,
          'resultados'
        );
      },
      error: (err) => {
        console.error('❌ Error al filtrar historial:', err);
        this.cargando = false;
      },
    });
  }

  // ============================================================
  // Limpiar filtros
  // ============================================================
  limpiarFiltros() {
    this.filtroUsuario = '';
    this.filtroFechaInicio = null;
    this.filtroFechaFin = null;
    this.filtroCampo = '';
    this.filtroId = null;
    this.historialFiltrado = [...this.historialCompleto];
  }

  // ============================================================
  // Exportar CSV
  // ============================================================
  exportarCSV() {
    if (this.historialFiltrado.length === 0) {
      this.notification.info('No hay datos para exportar.');
      return;
    }

    const headers = [
      'ID',
      'Fecha',
      'Usuario (ID)',
      'Tipo de Acción',
      'Sección',
      'Campo',
      'Valor Anterior',
      'Valor Nuevo',
    ];

    let csvContent = headers.map((h) => `"${h}"`).join(',') + '\n';

    this.historialFiltrado.forEach((entry) => {
      const row = [
        entry.id,
        new Date(entry.fecha).toLocaleString('es-CL'),
        entry.user_id,
        entry.tipo_accion,
        entry.seccion_afectada || '',
        entry.campo_afectado || '',
        this.formatValueForDisplay(entry.valor_anterior),
        this.formatValueForDisplay(entry.valor_nuevo),
      ].map((item) => `"${String(item).replace(/"/g, '""')}"`);

      csvContent += row.join(',') + '\n';
    });

    const blob = new Blob([csvContent], {
      type: 'text/csv;charset=utf-8;',
    });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'historial_cambios.csv');
    link.click();
    document.body.removeChild(link);
    this.notification.success('Historial exportado a CSV.');
  }

  // ============================================================
  // Utilidad: formatear valores para vista/exportación
  // ============================================================
  formatValueForDisplay(value: any): string {
    if (value === undefined || value === null || value === '') return '-';
    if (typeof value === 'object') {
      try {
        return JSON.stringify(value);
      } catch {
        return String(value);
      }
    }
    return String(value);
  }
}
