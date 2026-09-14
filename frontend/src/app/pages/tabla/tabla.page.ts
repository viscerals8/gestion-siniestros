import { Component, OnInit, OnDestroy, inject } from '@angular/core'; 
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonFooter,
  IonItem,
  IonLabel,
  IonButton,
  IonInput,
  IonDatetime,
  IonSelect,
  IonSelectOption,
  IonSearchbar,
  IonButtons,
  IonCheckbox,
  IonMenuButton
} from '@ionic/angular/standalone';

import { Subscription } from 'rxjs';
import { LoginService, UsuarioSesion } from '../../services/login.service';
import { TablaService } from '../../services/tabla.service';
import { DynamicsService } from '../../services/dynamics.service';
import { FormFieldsService, FormField } from 'src/app/services/form-fields.service';
import { NotificationService } from '../../services/notification.service';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-tabla',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonFooter,
    IonItem,
    IonLabel,
    IonButton,
    IonInput,
    IonDatetime,
    IonSelect,
    IonSelectOption,
    IonSearchbar,
    IonButtons,
    IonCheckbox,
    IonMenuButton
  ],
  templateUrl: './tabla.page.html',
  styleUrls: ['./tabla.page.scss'],
})
export class TablaPage implements OnInit, OnDestroy {
  private loginService = inject(LoginService);
  private tablaService = inject(TablaService);
  private dynamicsService = inject(DynamicsService);
  private notification = inject(NotificationService);

  // =====================================================
  // Datos de la tabla / formulario
  // =====================================================
  registros: any[] = [];
  registrosFiltrados: any[] = [];
  registroNuevo: any = {};
  filaEditandoId: number | null = null;
  mostrandoFormularioNuevo = false;
  
  // Atributos para la capa dinámica
  camposDinamicos: FormField[] = [];
  valoresDinamicos: { [key: string]: any } = {};

  // Formulario por fases: agrupa los mismos campos en pasos, no elimina ninguno.
  pasoActual = 1;
  pasos: { id: number; label: string }[] = [
    { id: 1, label: '🪪 Identificación' },
    { id: 2, label: '📄 Contrato y Ubicación' },
    { id: 3, label: '💰 Costos' },
    { id: 4, label: '🔒 Cierre y Categorías' },
    { id: 5, label: '🗂️ Gestión y Fiscalización' },
    { id: 6, label: '⚙️ Campos Personalizados' },
  ];

  // Filtros
  busqueda: string = '';
  filtroFecha: 'ultimoMes' | 'todos' = 'ultimoMes';

  // Usuario y rol reactivos
  usuario: UsuarioSesion | null = null;
  rolUsuarioLogueado: 'Administrador' | 'Editor' | 'Visualizador' | string = '';
  private subUsuario!: Subscription;

  // Inyección por propiedad limpia y moderna
  private formFieldsService = inject(FormFieldsService);

  // =====================================================
  // Ciclo de vida
  // =====================================================
  ngOnInit() {
    this.subUsuario = this.loginService.usuario$.subscribe((user) => {
      this.usuario = user;
      this.rolUsuarioLogueado = user?.rol || '';
      console.log('👤 Rol activo (tabla):', this.rolUsuarioLogueado);
    });

    this.resetFormulario();
    this.cargarRegistros(true);
    this.cargarConfiguracionCamposDinamicos(); 
  }

  ngOnDestroy() {
    if (this.subUsuario) this.subUsuario.unsubscribe();
  }

  // =====================================================
  // CAPA DINÁMICA: Metadatos EAV Tipificados
  // =====================================================
  cargarConfiguracionCamposDinamicos() {
    this.formFieldsService.getFields(true).subscribe({
      next: (fields: any[]) => { // Tipado explícito para evitar unknown
        this.camposDinamicos = fields || [];
        this.inicializarValoresDinamicos();
        console.log('⚙️ Campos dinámicos activos cargados:', this.camposDinamicos.length);
      },
      error: (err: any) => console.error('❌ Error al obtener catálogo de campos dinámicos', err)
    });
  }

  inicializarValoresDinamicos() {
    this.valoresDinamicos = {};
    if (this.camposDinamicos && Array.isArray(this.camposDinamicos)) {
      this.camposDinamicos.forEach((field: any) => {
        this.valoresDinamicos[field.name] = field.data_type === 'boolean' ? false : '';
      });
    }
  }

  // =====================================================
  // Wizard del formulario (pasos)
  // =====================================================
  get totalPasosEfectivo(): number {
    // El paso de Campos Personalizados se oculta si aún no existen campos dinámicos activos.
    return this.camposDinamicos.length > 0 ? 6 : 5;
  }

  get pasosVisibles() {
    return this.pasos.filter((p) => p.id <= this.totalPasosEfectivo);
  }

  get esUltimoPaso(): boolean {
    return this.pasoActual === this.totalPasosEfectivo;
  }

  get progresoPct(): number {
    return Math.round((this.pasoActual / this.totalPasosEfectivo) * 100);
  }

  irPaso(id: number) {
    if (id >= 1 && id <= this.totalPasosEfectivo) this.pasoActual = id;
  }

  pasoSiguiente() {
    if (this.pasoActual < this.totalPasosEfectivo) this.pasoActual++;
  }

  pasoAnterior() {
    if (this.pasoActual > 1) this.pasoActual--;
  }

  puedeEditar(): boolean {
    return (
      this.rolUsuarioLogueado === 'Administrador' ||
      this.rolUsuarioLogueado === 'Editor'
    );
  }

  // =====================================================
  // CRUD Y FILTROS
  // =====================================================
  cargarRegistros(filtroUltimoMes: boolean = true) {
    this.tablaService.obtenerRegistros().subscribe({
      next: (data) => {
        const registros = data || [];

        if (filtroUltimoMes) {
          const haceUnMes = new Date();
          haceUnMes.setMonth(haceUnMes.getMonth() - 1);

          this.registros = registros.filter((r) => {
            if (!r.InitialDate) return false;
            const fecha = new Date(r.InitialDate);
            return fecha >= haceUnMes;
          });
        } else {
          this.registros = registros;
        }

        this.registrosFiltrados = [...this.registros];
        console.log('📦 Registros cargados:', this.registrosFiltrados.length);
      },
      error: (err) => console.error('Error cargando registros', err),
    });
  }

  filtrarRegistros() {
    const term = this.busqueda.toLowerCase();

    this.registrosFiltrados = this.registros.filter((r) => {
      const coincideCampoFijo = Object.entries(r).some(
        ([key, v]) =>
          key !== 'custom_fields' &&
          String(v || '').toLowerCase().includes(term)
      );
      if (coincideCampoFijo) return true;

      if (r.custom_fields) {
        return Object.values(r.custom_fields).some((v) =>
          String(v || '').toLowerCase().includes(term)
        );
      }
      return false;
    });
  }

  guardarRegistro() {
    if (!this.puedeEditar()) {
      this.notification.error('Solo Administrador o Editor pueden guardar registros.');
      return;
    }

    const payload = this.limpiarPayload({ ...this.registroNuevo });

    // Inyección híbrida del nodo custom_fields estructurado
    payload.custom_fields = { ...this.valoresDinamicos };

    if (typeof payload.Company === 'string' && payload.Company.trim())
      payload.Company = { Name: payload.Company };

    if (typeof payload.Country === 'string' && payload.Country.trim())
      payload.Country = { Name: payload.Country };

    if (typeof payload.Type === 'string' && payload.Type.trim())
      payload.Type = { Name: payload.Type };

    if (typeof payload.Estado === 'string' && payload.Estado.trim()) {
      payload.State = { Name: payload.Estado };
      delete payload.Estado;
    }

    if (typeof payload.Materia === 'string' && payload.Materia.trim()) {
      payload.Matter = { Name: payload.Materia };
      delete payload.Materia;
    }

    if (this.filaEditandoId !== null) {
      console.log('🛠 Editando registro:', this.filaEditandoId);

      if (payload.AccidentID) delete payload.AccidentID;

      this.tablaService
        .actualizarRegistroFastAPI(this.filaEditandoId, payload)
        .subscribe({
          next: (res) => {
            console.log('✅ Registro actualizado:', res);

            const index = this.registros.findIndex(
              (r) => r.AccidentID === this.filaEditandoId
            );
            if (index !== -1) {
              this.registros[index] = {
                ...this.registros[index],
                ...payload,
              };
            }

            this.cancelarEdicion();
            this.cargarRegistros(this.filtroFecha === 'ultimoMes');
          },
          error: (err) => console.error('❌ Error al actualizar', err),
        });
    } else {
      console.log('🆕 Nuevo registro híbrido listo para enviar:', payload);

      this.tablaService.agregarRegistroFastAPI(payload).subscribe({
        next: (res) => {
          console.log('✅ Registro agregado con éxito:', res);
          this.cargarRegistros(this.filtroFecha === 'ultimoMes');
          this.toggleFormularioNuevo();
        },
        error: (err) => console.error('❌ Error al agregar', err),
      });
    }
  }

  editarRegistro(id: number) {
    if (!this.puedeEditar()) {
      this.notification.error('No tienes permisos para editar.');
      return;
    }

    const registro = this.registros.find(
      (r) => r.AccidentID === id
    );
    if (registro) {
      this.registroNuevo = { ...registro };
      this.filaEditandoId = id;
      this.mostrandoFormularioNuevo = true;
      this.pasoActual = 1;

      this.inicializarValoresDinamicos();
      if (registro.custom_fields) {
        Object.keys(registro.custom_fields).forEach(key => {
          this.valoresDinamicos[key] = registro.custom_fields[key];
        });
      }
    }
  }

  cancelarEdicion() {
    this.filaEditandoId = null;
    this.mostrandoFormularioNuevo = false;
    this.resetFormulario();
  }

  eliminarRegistro(id: number) {
    if (!this.puedeEditar()) {
      this.notification.error('No tienes permisos para eliminar registros.');
      return;
    }

    this.tablaService.eliminarRegistroFastAPI(id).subscribe({
      next: () => {
        this.registros = this.registros.filter(
          (r) => r.AccidentID !== id
        );
        this.filtrarRegistros();
      },
      error: (err) => console.error('❌ Error eliminando', err),
    });
  }

  toggleFormularioNuevo() {
    this.mostrandoFormularioNuevo = !this.mostrandoFormularioNuevo;
    if (!this.mostrandoFormularioNuevo) this.resetFormulario();
  }

  buscarContrato() {
    const idProyecto = this.registroNuevo.JusttimeNumber;
    if (!idProyecto) return;

    this.dynamicsService.getContrato(idProyecto).subscribe({
      next: (data: any) => {
        if (data && data.length > 0) {
          const contrato = data[0];

          this.registroNuevo.Department ||= contrato.NOMBRE_DEPARTAMENTO || '';
          this.registroNuevo.Contrato ||= contrato.NOMBRE_CONTRATO || '';
          this.registroNuevo.Instalacion ||= contrato.NOMBRE_INSTALACION || '';
          this.registroNuevo.Zone ||= contrato.ZONA || '';
          this.registroNuevo.Activity ||= contrato.NOMBRE_CONTRATO || '';
          this.registroNuevo.Company ||= contrato.EMPRESA || '';
          this.registroNuevo.Management ||= contrato.NOMBRE_PROYECTO || '';
          this.registroNuevo.Responsible ||= contrato.NOMBRE_DEPARTAMENTO || '';
          this.registroNuevo.EstadoContrato ||= contrato.ESTADO_CONTRATO || '';
          this.registroNuevo.EstadoInstalacion ||= contrato.ESTADO_INSTALACION || '';
          this.registroNuevo.NombreGrupo ||= contrato.NOMBRE_GRUPO || '';
          this.registroNuevo.NombreInstalacion ||= contrato.NOMBRE_INSTALACION || '';
        }
      },
      error: (err) => console.error('Error consultando Dynamics', err),
    });
  }

  private resetFormulario() {
    this.registroNuevo = {
      AccidentID: null,
      JusttimeNumber: '',
      InitialDate: '',
      Year: null,
      Country: '',
      IDEntidad: '',
      Demandant: '',
      Defendant: '',
      Company: '',
      Dimensions: '',
      Contrato: '',
      Instalacion: '',
      Supervisor: '',
      JOP: '',
      ZonalDelegate: '',
      Zone: '',
      Type: '',
      Activity: '',
      AccountingKey: '',
      BeenProcessing: '',
      Materia: '',
      Motivo: '',
      ClaimedAmount: null,
      EstimatedAmount: null,
      PreviousProvision: null,
      AdditionalDemand: '',
      NonProvisionedAmount: null,
      ReversalAmount: null,
      FinalCost: null,
      FinalAttorneyCost: null,
      OtherExpenses: null,
      CloseDate: '',
      PenaltyNumber: '',
      CloseComment: '',
      FirstAccountingEstimate: null,
      SecondAccountingEstimate: null,
      Category1: '',
      Category2: '',
      Category3: '',
      Management: '',
      Modification: '',
      Categoria: '',
      InspectionDate: '',
      PeriodoFiscalizado: '',
      Department: '',
      Responsible: '',
      AppliedMeasure: '',
      Estado: '',
      DimensionesFinal: '',
      Comentarios: '',
      EstadoContrato: '',
      EstadoInstalacion: '',
      NombreGrupo: '',
      NombreInstalacion: '',
    };
    this.inicializarValoresDinamicos();
    this.pasoActual = 1;
  }

  exportarExcel() {
    if (!this.registros || this.registros.length === 0) {
      console.warn('⚠️ No hay registros para exportar');
      return;
    }

    const datosAplanados = this.registros.map(reg => {
      const { custom_fields, ...resto } = reg;
      const flatObj = { ...resto };
      if (custom_fields) {
        Object.keys(custom_fields).forEach(key => {
          flatObj[`[Dinámico] ${key}`] = custom_fields[key];
        });
      }
      return flatObj;
    });

    const hoja = XLSX.utils.json_to_sheet(datosAplanados);
    const libro = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(libro, hoja, 'Registros');
    const buffer = XLSX.write(libro, { bookType: 'xlsx', type: 'array' });

    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `Registros_${fecha}.xlsx`;

    const blob = new Blob([buffer], {
      type: 'application/octet-stream',
    });

    saveAs(blob, nombreArchivo);
  }

  private limpiarPayload(obj: any) {
    Object.keys(obj).forEach((key) => {
      if (obj[key] === undefined) delete obj[key];
    });
    return obj;
  }

  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
}