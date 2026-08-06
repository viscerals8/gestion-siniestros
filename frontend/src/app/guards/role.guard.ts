import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  Router,
  UrlTree,
} from '@angular/router';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { LoginService } from '../services/login.service';

@Injectable({
  providedIn: 'root',
})
export class RoleGuard implements CanActivate {
  constructor(private loginService: LoginService, private router: Router) {}

  /**
   * Protege rutas según el rol del usuario logueado.
   * Usa el observable del LoginService para reaccionar a cambios en tiempo real.
   */
  canActivate(
    route: ActivatedRouteSnapshot
  ): Observable<boolean | UrlTree> {
    const rolesPermitidos: string[] = route.data['roles'];

    // Nos suscribimos al usuario$ reactivo
    return this.loginService.usuario$.pipe(
      map((usuario) => {
        // Caso: sesión válida y rol permitido
        if (usuario && rolesPermitidos.includes(usuario.rol)) {
          return true;
        }

        // Caso: no autorizado → redirige según su rol
        const rol = usuario?.rol;
        if (rol === 'Administrador') {
          return this.router.parseUrl('/gestion-usuarios');
        } else if (rol === 'Editor') {
          return this.router.parseUrl('/tabla');
        } else if (rol === 'Visualizador') {
          return this.router.parseUrl('/historial-cambios');
        } else {
          return this.router.parseUrl('/login');
        }
      })
    );
  }
}
