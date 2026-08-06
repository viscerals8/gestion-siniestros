import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DynamicsService {
  private readonly dynamicsBaseUrl = environment.dynamicsBaseUrl;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene datos de contrato desde Dynamics por ID
   * @param idProyecto string, ej: "0169/040/17021"
   */
  getContrato(idProyecto: string): Observable<any> {
    const params = new HttpParams().set('id', idProyecto);
    return this.http.get<any>(`${this.dynamicsBaseUrl}/validar_dynamics`, { params })
      .pipe(catchError(this.handleError));
  }

  /** Manejo de errores básico */
  private handleError(error: HttpErrorResponse) {
    const msg = error.error?.message || error.message || 'Error de red al consultar Dynamics';
    return throwError(() => new Error(msg));
  }
}
