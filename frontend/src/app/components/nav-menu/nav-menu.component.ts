import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import {
  IonList,
  IonItem,
  IonIcon,
  IonLabel,
  MenuController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  documentTextOutline,
  timeOutline,
  peopleOutline,
  optionsOutline,
  logOutOutline,
} from 'ionicons/icons';
import { LoginService, UsuarioSesion } from '../../services/login.service';

@Component({
  selector: 'app-nav-menu',
  standalone: true,
  imports: [CommonModule, IonList, IonItem, IonIcon, IonLabel],
  templateUrl: './nav-menu.component.html',
  styleUrls: ['./nav-menu.component.scss'],
})
export class NavMenuComponent implements OnInit, OnDestroy {
  usuario: UsuarioSesion | null = null;
  rolUsuarioLogueado: 'Administrador' | 'Editor' | 'Visualizador' | string = '';
  private subUsuario!: Subscription;

  constructor(
    private loginService: LoginService,
    private router: Router,
    private menuController: MenuController
  ) {
    addIcons({
      documentTextOutline,
      timeOutline,
      peopleOutline,
      optionsOutline,
      logOutOutline,
    });
  }

  ngOnInit() {
    this.subUsuario = this.loginService.usuario$.subscribe((user) => {
      this.usuario = user;
      this.rolUsuarioLogueado = user?.rol || '';
    });
  }

  ngOnDestroy() {
    if (this.subUsuario) this.subUsuario.unsubscribe();
  }

  private irA(ruta: string) {
    this.router.navigate([ruta]);
    this.menuController.close();
  }

  irTabla() {
    this.irA('/tabla');
  }

  irHistorialCambios() {
    this.irA('/historial-cambios');
  }

  irGestionUsuarios() {
    this.irA('/gestion-usuarios');
  }

  irCamposDinamicos() {
    this.irA('/campos-dinamicos');
  }

  cerrarSesion() {
    this.menuController.close();
    this.loginService.logout();
  }
}
