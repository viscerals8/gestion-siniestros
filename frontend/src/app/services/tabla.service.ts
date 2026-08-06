// ===============================================================
// src/app/services/tabla.service.ts
// Servicio Angular para CRUD de Accident (con relaciones anidadas)
// Autor: Javier Soto
// Fecha: 2025-10-16 (versión estable y corregida)
// ===============================================================

import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { ApiService } from './api.service';
// NUEVO: tomamos el usuario activo para enviar su ID al backend
import { LoginService } from './login.service';

// ===============================================================
// Interface principal alineada al modelo FastAPI
// ===============================================================
export interface Registro {
  AccidentID?: number;
  Unico?: number;
  JusttimeNumber?: string;
  InitialDate?: string;
  Year?: number;
  IDEntidad?: string;
  Demandant?: string;
  Defendant?: string;
  Supervisor?: string;
  JOP?: string;
  ZonalDelegate?: string;
  Zone?: string;
  Activity?: string;
  AccountingKey?: string;
  ClaimedAmount?: number;
  EstimatedAmount?: number;
  PreviousProvision?: number;
  AdditionalDemand?: string;
  NonProvisionedAmount?: number;
  ReversalAmount?: number;
  FinalCost?: number;
  FinalAttorneyCost?: number;
  OtherExpenses?: number;
  CloseDate?: string;
  CloseComment?: string;
  Management?: string;
  Responsible?: string;
  AppliedMeasure?: string;
  Dimensions?: string;

  // Nuevos campos extendidos
  BeenProcessing?: string;
  PenaltyNumber?: string;
  Categoria?: string;
  InspectionDate?: string;
  PeriodoFiscalizado?: string;
  Department?: string;
  DimensionesFinal?: string;
  Comentarios?: string;
  EstadoContrato?: string;
  EstadoInstalacion?: string;
  NombreGrupo?: string;
  NombreInstalacion?: string;

  // Relaciones anidadas
  Company?: { Name: string };
  Country?: { Name: string };
  Type?: { Name: string };
  State?: { Name: string };
  Matter?: { Name: string };
  Category1?: { Name: string };
  Category2?: { Name: string };
  Category3?: { Name: string };

  [key: string]: any;
}

// ===============================================================
// Servicio principal
// ===============================================================
@Injectable({ providedIn: 'root' })
export class TablaService {
  private readonly base = '/registros';
  private registrosSubject = new BehaviorSubject<Registro[]>([]);
  public registros$ = this.registrosSubject.asObservable();

  // NUEVO: inyectamos LoginService (no afecta a nada existente)
  constructor(private api: ApiService, private login: LoginService) {}

  // NUEVO: header con el ID de usuario para el backend (X-User-Id)
  private authHeaders() {
    const u: any = this.login.getUsuarioSesion?.();
    // Soporta tanto u.id como u.UserID (según tu sesión actual)
    const id = (u?.id ?? u?.UserID ?? '').toString();
    return id ? { 'X-User-Id': id } : {};
  }

  // ===============================================================
  // GET → obtiene todos los registros
  // ===============================================================
  obtenerRegistros(): Observable<Registro[]> {
    return this.api.get<Registro[]>(`${this.base}/`).pipe(
      tap({
        next: (data) => {
          const normalizados = (data || []).map((r) => this.normalizarEntrada(r));
          this.registrosSubject.next(normalizados);
        },
        error: (err) => console.error('❌ Error cargando registros:', err),
      })
    );
  }

  // ===============================================================
  // GET → obtiene un registro por ID
  // ===============================================================
  obtenerRegistro(id: number): Observable<Registro> {
    return this.api.get<Registro>(`${this.base}/${id}`).pipe(
      tap((r) => this.normalizarEntrada(r))
    );
  }

  // ===============================================================
  // POST → agrega un nuevo registro
  // ===============================================================
  agregarRegistroFastAPI(registro: Omit<Registro, 'AccidentID'>): Observable<Registro> {
    const payload = this.serializarSalida(registro);
    console.log('📤 Enviando datos al backend (POST):', payload);

    // NUEVO: agregamos X-User-Id sin cambiar el resto
    return this.api.post<Registro>(`${this.base}/`, payload, {
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
    }).pipe(
      tap({
        next: (res) => {
          console.log('✅ Registro agregado correctamente:', res);
          this.obtenerRegistros().subscribe();
        },
        error: (err) => {
          console.error('❌ Error al agregar registro:', err);
        },
      })
    );
  }

  // ===============================================================
  // PUT → actualiza un registro existente
  // ===============================================================
  actualizarRegistroFastAPI(id: number, registro: Omit<Registro, 'AccidentID'>): Observable<Registro> {
    const payload = this.serializarSalida(registro);
    console.log('📤 Enviando datos al backend (PUT):', payload);

    // NUEVO: agregamos X-User-Id sin cambiar el resto
    return this.api.put<Registro>(`${this.base}/${id}`, payload, {
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
    }).pipe(
      tap({
        next: (res) => {
          console.log('✅ Registro actualizado correctamente:', res);
          this.obtenerRegistros().subscribe();
        },
        error: (err) => {
          console.error('❌ Error al actualizar registro:', err);
        },
      })
    );
  }

  // ===============================================================
  // DELETE → elimina un registro
  // ===============================================================
  eliminarRegistroFastAPI(id: number): Observable<{ detail: string }> {
    console.log('🗑 Eliminando registro ID:', id);

    // NUEVO: agregamos X-User-Id sin cambiar el resto
    return this.api.delete<{ detail: string }>(`${this.base}/${id}`, {
      headers: this.authHeaders(),
    }).pipe(
      tap({
        next: () => {
          console.log('✅ Registro eliminado correctamente');
          this.obtenerRegistros().subscribe();
        },
        error: (err) => {
          console.error('❌ Error al eliminar registro:', err);
        },
      })
    );
  }

  // ===============================================================
  // Normalización (de backend → frontend)
  // ===============================================================
  private normalizarEntrada(r: Registro): Registro {
    const relacionales = ['Company', 'Country', 'Type', 'State', 'Matter', 'Category1', 'Category2', 'Category3'];
    relacionales.forEach((campo) => {
      if (r[campo] && typeof r[campo] === 'object' && 'Name' in r[campo]) {
        r[campo] = (r[campo] as any).Name;
      }
    });
    return r;
  }

  // ===============================================================
  // Serialización (de frontend → backend)
  // ===============================================================
  private serializarSalida(r: Registro): Registro {
    const serializado: any = { ...r };

    // Campos relacionales esperados como objetos
    const relacionales = ['Company', 'Country', 'Type', 'State', 'Matter', 'Category1', 'Category2', 'Category3'];
    relacionales.forEach((campo) => {
      const valor = r[campo];
      if (typeof valor === 'string' && valor.trim() !== '') {
        serializado[campo] = { Name: valor.trim() };
      }
    });

    // Eliminar campos vacíos o nulos
    Object.keys(serializado).forEach((k) => {
      if (
        serializado[k] === '' ||
        serializado[k] === null ||
        serializado[k] === undefined
      ) {
        delete serializado[k];
      }
    });

    return serializado;
  }
}
