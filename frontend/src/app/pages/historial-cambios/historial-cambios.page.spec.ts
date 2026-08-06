import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HistorialCambiosPage } from './historial-cambios.page';

describe('HistorialCambiosPage', () => {
  let component: HistorialCambiosPage;
  let fixture: ComponentFixture<HistorialCambiosPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(HistorialCambiosPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
