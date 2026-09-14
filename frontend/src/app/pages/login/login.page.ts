import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton
} from '@ionic/angular/standalone';
import { LoginService, UsuarioLogin } from '../../services/login.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
  ],
})
export class LoginPage {
  private loginService = inject(LoginService);
  private notification = inject(NotificationService);

  email = '';
  password = '';
  loading = false;

  login() {
    if (!this.email || !this.password) {
      this.notification.error('Debes ingresar correo y contraseña.');
      return;
    }

    const credenciales: UsuarioLogin = {
      correo: this.email,
      password: this.password,
    };

    this.loading = true;

    this.loginService.login(credenciales).subscribe({
      next: (exito) => {
        this.loading = false;
        if (!exito) {
          this.notification.error('Usuario o contraseña inválidos');
        }
        // Si exito === true, el servicio ya se encarga de redirigir según el rol.
      },
      error: (err) => {
        this.loading = false;
        console.error('Error en login:', err);
        this.notification.error('Hubo un problema al iniciar sesión.');
      },
    });
  }
}
