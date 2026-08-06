// src/app/services/gestion-usuarios.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

// === Tipos alineados al response_model de FastAPI ===
// (response_model_by_alias=False → devuelve id, nombre, correo, rol_id, activo)
export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol_id: number;
  activo: boolean;
}

// Cuerpos según tus Pydantic
export interface UsuarioCreate {
  nombre: string;
  correo: string;
  password: string;
  rol_id: number;
  activo?: boolean;
}

export interface UsuarioUpdate {
  nombre?: string;
  correo?: string;
  password?: string;
  rol_id?: number;
  activo?: boolean;
}

@Injectable({ providedIn: 'root' })
export class GestionUsuariosService {
  // Tu router usa prefix="/usuarios" y la colección está en "/"
  private readonly base = '/usuarios';

  constructor(private api: ApiService) {}

  // GET /usuarios/
  getUsuarios(): Observable<Usuario[]> {
    return this.api.get<Usuario[]>(`${this.base}/`);
  }

  // POST /usuarios/
  agregarUsuario(usuario: UsuarioCreate): Observable<Usuario> {
    return this.api.post<Usuario>(`${this.base}/`, usuario);
  }

  // PUT /usuarios/{user_id}
  editarUsuario(id: number, usuario: UsuarioUpdate): Observable<Usuario> {
    return this.api.put<Usuario>(`${this.base}/${id}`, usuario);
  }

  // DELETE /usuarios/{user_id}
  eliminarUsuario(id: number): Observable<void> {
    return this.api.delete<void>(`${this.base}/${id}`);
  }
}
