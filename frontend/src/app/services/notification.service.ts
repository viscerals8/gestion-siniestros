import { Injectable, inject } from '@angular/core';
import { AlertController, ToastController } from '@ionic/angular/standalone';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private toastController = inject(ToastController);
  private alertController = inject(AlertController);


  async success(message: string) {
    await this.presentToast(message, 'success');
  }

  async error(message: string) {
    await this.presentToast(message, 'danger');
  }

  async info(message: string) {
    await this.presentToast(message, 'medium');
  }

  /** Reemplazo de window.confirm() con el look & feel de la app. */
  async confirm(message: string, header = 'Confirmar'): Promise<boolean> {
    return new Promise((resolve) => {
      this.alertController
        .create({
          header,
          message,
          buttons: [
            {
              text: 'Cancelar',
              role: 'cancel',
              handler: () => resolve(false),
            },
            {
              text: 'Aceptar',
              role: 'confirm',
              handler: () => resolve(true),
            },
          ],
        })
        .then((alert) => alert.present());
    });
  }

  private async presentToast(
    message: string,
    color: 'success' | 'danger' | 'medium'
  ) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'top',
      buttons: [{ icon: 'close', role: 'cancel' }],
    });
    await toast.present();
  }
}
