import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { ApiService } from './api.service';

export interface UsuarioLogin {
  correo: string;
  password: string;
}

export interface UsuarioSesion {
  id: number;
  nombre: string;
  correo: string;
  rol: 'Administrador' | 'Editor' | 'Visualizador' | string;
}

interface LoginResponse extends UsuarioSesion {
  token: string;
}

@Injectable({ providedIn: 'root' })
export class LoginService {
  private router = inject(Router);
  private api = inject(ApiService);

  private readonly base = '/login';
  private usuarioSesion: UsuarioSesion | null = null;

  // Nuevo: Observable reactivo para la sesión
  private usuarioSubject = new BehaviorSubject<UsuarioSesion | null>(null);
  public usuario$ = this.usuarioSubject.asObservable();

  constructor() {
    // Restaurar sesión si hay algo guardado en localStorage
    const guardado = localStorage.getItem('usuarioSesion');
    if (guardado) {
      this.usuarioSesion = JSON.parse(guardado);
      this.usuarioSubject.next(this.usuarioSesion); // notifica a los suscriptores
    }
  }

  /**
   * Autentica contra FastAPI: POST /login/
   * Devuelve true si autenticó; false si falló.
   */
  login(datos: UsuarioLogin): Observable<boolean> {
    return this.api.post<LoginResponse>(`${this.base}/`, datos).pipe(
      tap(({ token, ...user }) => {
        // Guarda usuario y token de sesión
        this.usuarioSesion = user;
        localStorage.setItem('usuarioSesion', JSON.stringify(user));
        localStorage.setItem('token', token);
        this.usuarioSubject.next(user); // notifica cambio inmediato

        // Navegación según rol
        switch (user.rol) {
          case 'Administrador':
            this.router.navigate(['/gestion-usuarios']);
            break;
          case 'Editor':
            this.router.navigate(['/tabla']);
            break;
          case 'Visualizador':
            this.router.navigate(['/historial-cambios']);
            break;
          default:
            this.router.navigate(['/login']);
        }
      }),
      map(() => true),
      catchError(() => of(false))
    );
  }

  /** Obtiene usuario por id: GET /login/usuario/{user_id} */
  obtenerUsuario(userId: number): Observable<UsuarioSesion> {
    return this.api.get<UsuarioSesion>(`${this.base}/usuario/${userId}`);
  }

  /** Cierra sesión y redirige a /login */
  logout(): void {
    this.usuarioSesion = null;
    localStorage.removeItem('usuarioSesion');
    localStorage.removeItem('token');
    this.usuarioSubject.next(null); // notifica logout inmediato
    this.router.navigate(['/login']);
  }

  /** Devuelve el usuario actual */
  getUsuarioSesion(): UsuarioSesion | null {
    return this.usuarioSesion;
  }

  /** Devuelve el rol actual */
  getRol(): string | null {
    return this.usuarioSesion?.rol ?? null;
  }

  /** ¿Hay sesión activa? */
  estaAutenticado(): boolean {
    return this.usuarioSesion !== null;
  }
}
