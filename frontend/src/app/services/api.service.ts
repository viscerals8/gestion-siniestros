// ===============================================================
// src/app/services/api.service.ts
// Servicio base HTTP — versión profesional y robusta
// Autor: Javier Soto
// Fecha: 2025-10-16
// ===============================================================

import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpParams,
  HttpHeaders,
} from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly base = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  // ===============================================================
  // GET
  // ===============================================================
  get<T>(
    endpoint: string,
    params?: Record<string, any>,
    options?: { headers?: any; withCredentials?: boolean }
  ): Observable<T> {
    const httpParams = new HttpParams({ fromObject: params ?? {} });
    return this.http
      .get<T>(`${this.base}${endpoint}`, {
        params: httpParams,
        ...options,
      })
      .pipe(catchError(this.handle));
  }

  // ===============================================================
  // POST
  // ===============================================================
  post<T>(
    endpoint: string,
    body: any,
    options?: { headers?: any; withCredentials?: boolean }
  ): Observable<T> {
    const headers = this.ensureHeaders(body, options);
    return this.http
      .post<T>(`${this.base}${endpoint}`, body, { headers, ...options })
      .pipe(catchError(this.handle));
  }

  // ===============================================================
  // PUT
  // ===============================================================
  put<T>(
    endpoint: string,
    body: any,
    options?: { headers?: any; withCredentials?: boolean }
  ): Observable<T> {
    const headers = this.ensureHeaders(body, options);
    return this.http
      .put<T>(`${this.base}${endpoint}`, body, { headers, ...options })
      .pipe(catchError(this.handle));
  }

  // ===============================================================
  // PATCH
  // ===============================================================
  patch<T>(
    endpoint: string,
    body: any,
    options?: { headers?: any; withCredentials?: boolean }
  ): Observable<T> {
    const headers = this.ensureHeaders(body, options);
    return this.http
      .patch<T>(`${this.base}${endpoint}`, body, { headers, ...options })
      .pipe(catchError(this.handle));
  }

  // ===============================================================
  // DELETE
  // ===============================================================
  delete<T>(
    endpoint: string,
    body?: any,
    options?: { headers?: any; withCredentials?: boolean }
  ): Observable<T> {
    const headers = this.ensureHeaders(body, options);
    return this.http
      .request<T>('DELETE', `${this.base}${endpoint}`, {
        body,
        headers,
        ...options,
      })
      .pipe(catchError(this.handle));
  }

  // ===============================================================
  // Manejador de errores global
  // ===============================================================
  private handle(error: HttpErrorResponse) {
    const message =
      (error.error && (error.error.detail || error.error.message)) ||
      error.message ||
      'Error de red';

    const errorInfo = {
      status: error.status,
      message,
      timestamp: new Date().toISOString(),
      url: error.url,
    };

    console.error('❌ Error HTTP:', errorInfo);

    return throwError(() => errorInfo);
  }

  // ===============================================================
  // Asegura encabezados correctos (JSON / FormData / JWT)
  // ===============================================================
  private ensureHeaders(body?: any, options?: any): HttpHeaders {
    const existingHeaders = options?.headers || {};
    const token = localStorage.getItem('token');

    // Si el body es FormData, no se debe establecer Content-Type
    const isFormData = body instanceof FormData;

    const headersConfig: Record<string, string> = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...existingHeaders,
    };

    return new HttpHeaders(headersConfig);
  }
}
