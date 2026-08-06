import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ExternalImportService {
  private readonly base = '/import';

  constructor(private api: ApiService) {}

  /** Ping simple para validar el prefijo/ruta del backend */
  ping(): Observable<any> {
    return this.api.get<any>(`${this.base}/ping`);
  }

  /**
   * Importa proyectos externos (upsert en backend).
   * payload: Array de registros con claves en MAYÚSCULAS (EMPRESA, NOMBRE_CONTRATO, etc.)
   */
  importExternalProjects(payload: any[]): Observable<any> {
    return this.api.post<any>(`${this.base}/external-projects`, payload);
  }
}
