import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

// Mapeamos la interfaz idéntica a lo que devuelve el backend (Swagger)
export interface FormField {
  id?: number;
  name: string;
  data_type: string; // 'string' | 'number' | 'boolean' | 'date'
  required: boolean;
  active: boolean;
  display_order: number;
}

export interface FormFieldCreate {
  name: string;
  data_type: string;
  required?: boolean;
  active?: boolean;
  display_order?: number;
}

export interface FormFieldUpdate {
  name?: string;
  data_type?: string;
  required?: boolean;
  active?: boolean;
  display_order?: number;
}

@Injectable({
  providedIn: 'root'
})
export class FormFieldsService {
  // Tu router usa prefix="/form-fields" y la colección está en "/"
  private readonly base = '/form-fields';

  constructor(private api: ApiService) {}

  /**
   * Obtiene los campos dinámicos desde el backend.
   * @param soloActivos Si es true, pide al backend solo los campos activos (?active=true).
   */
  getFields(soloActivos: boolean = true): Observable<FormField[]> {
    return this.api.get<FormField[]>(`${this.base}/`, { active: soloActivos });
  }

  // GET /form-fields/{id}
  getField(id: number): Observable<FormField> {
    return this.api.get<FormField>(`${this.base}/${id}`);
  }

  // POST /form-fields/ — pensado para la pantalla de administración
  createField(field: FormFieldCreate): Observable<FormField> {
    return this.api.post<FormField>(`${this.base}/`, field);
  }

  // PUT /form-fields/{id}
  updateField(id: number, field: FormFieldUpdate): Observable<FormField> {
    return this.api.put<FormField>(`${this.base}/${id}`, field);
  }

  // DELETE /form-fields/{id}
  deleteField(id: number): Observable<void> {
    return this.api.delete<void>(`${this.base}/${id}`);
  }
}
