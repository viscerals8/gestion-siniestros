
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

// ============================================================
// Interfaces de Tipos
// ============================================================

// ↳ Estructura del response devuelto por el backend (HistorialResponse)
export interface HistorialEntry {
  id: number;
  user_id: number;
  accident_id: number;
  tipo_accion: string;
  seccion_afectada?: string | null;
  campo_afectado?: string | null;
  valor_anterior?: string | null;
  valor_nuevo?: string | null;
  fecha: string; // ISO string (datetime)
}

// ↳ Estructura del body enviado al backend (HistorialRequest). user_id lo agrega
// el backend a partir del token de sesión, no se manda desde el cliente.
export interface HistorialCreate {
  accident_id: number;
  tipo_accion: string;
  seccion_afectada?: string;
  campo_afectado?: string;
  valor_anterior?: string;
  valor_nuevo?: string;
}

// ============================================================
// Servicio principal de gestión de historial
// ============================================================
@Injectable({ providedIn: 'root' })
export class HistorialCambiosService {
  /** Prefijo del router FastAPI */
  private readonly base = '/historial';

  constructor(private api: ApiService) {}

  // ============================================================
  // Obtener historial completo
  // ============================================================
  getHistorial(): Observable<HistorialEntry[]> {
    console.log('📡 Solicitando historial completo al backend...');
    return this.api.get<HistorialEntry[]>(`${this.base}/`);
  }

  // ============================================================
  // Agregar nuevo registro
  // ============================================================
  agregarHistorial(entry: HistorialCreate): Observable<HistorialEntry> {
    console.log('🧾 Enviando nuevo log al backend:', entry);
    return this.api.post<HistorialEntry>(`${this.base}/`, entry);
  }

  // ============================================================
  // Filtrar historial
  // ============================================================
  /**
   * Filtros disponibles:
   * - usuario: nombre del usuario (string)
   * - campo: campo afectado (string)
   * - id: ID del usuario (number)
   * - fechaInicio / fechaFin: formato ISO (YYYY-MM-DD o completo)
   */
  filtrarHistorial(filtros: {
    usuario?: string;
    campo?: string;
    id?: number;          // ← mapeado a user_id en backend
    fechaInicio?: string; // ISO 'YYYY-MM-DD' o 'YYYY-MM-DDTHH:mm:ss'
    fechaFin?: string;    // ISO
  }): Observable<HistorialEntry[]> {
    const query: Record<string, string> = {};

    if (filtros?.id !== undefined) query['user_id'] = String(filtros.id);
    if (filtros?.usuario) query['usuario'] = filtros.usuario;
    if (filtros?.campo) query['campo'] = filtros.campo;
    if (filtros?.fechaInicio) query['fecha_inicio'] = filtros.fechaInicio;
    if (filtros?.fechaFin) query['fecha_fin'] = filtros.fechaFin;

    console.log('🔍 Aplicando filtros al historial:', query);

    return this.api.get<HistorialEntry[]>(`${this.base}/filtrar`, query);
  }
}
