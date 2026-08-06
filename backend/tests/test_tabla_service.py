from datetime import date

from app.services.tabla_service import TablaService
from app.services.gestion_historial_service import GestionHistorialService


def _datos_minimos(**overrides):
    datos = {
        "InitialDate": date(2026, 1, 1),
        "Company": "Compañía X",
        "Country": "España",
        "Type": "Laboral",
        "State": "Abierto",
        "Matter": "General",
        "Zone": "Norte",
    }
    datos.update(overrides)
    return datos


def test_agregar_registro_crea_accidente_y_relaciones(db_session, usuario):
    nuevo = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)

    assert nuevo.AccidentID is not None
    assert nuevo.Zone == "Norte"
    assert nuevo.company.Name == "Compañía X"


def test_agregar_registro_reutiliza_relacion_existente(db_session, usuario):
    primero = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)
    segundo = TablaService.agregar_registro(
        db_session, _datos_minimos(Zone="Sur"), user_id=usuario.UserID
    )

    # Misma compañía ("Compañía X") en ambos: no debe duplicar la fila de Company.
    assert primero.CompanyID == segundo.CompanyID


def test_agregar_registro_genera_historial_de_creacion(db_session, usuario):
    nuevo = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)

    historial = GestionHistorialService.get_historial(db_session)
    campos_logueados = {log.CampoAfectado for log in historial if log.AccidentID == nuevo.AccidentID}

    assert "Zone" in campos_logueados
    assert all(log.TipoAccion == "CREAR" for log in historial)


def test_actualizar_registro_solo_audita_campos_que_cambiaron(db_session, usuario):
    nuevo = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)

    TablaService.actualizar_registro(
        db_session, nuevo.AccidentID, {"Zone": "Sur"}, user_id=usuario.UserID
    )

    historial = GestionHistorialService.get_historial(db_session)
    ediciones = [log for log in historial if log.TipoAccion == "EDITAR"]

    assert len(ediciones) == 1
    assert ediciones[0].CampoAfectado == "Zone"
    assert ediciones[0].ValorAnterior == "Norte"
    assert ediciones[0].ValorNuevo == "Sur"


def test_actualizar_registro_no_audita_si_el_valor_no_cambia(db_session, usuario):
    nuevo = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)

    TablaService.actualizar_registro(
        db_session, nuevo.AccidentID, {"Zone": "Norte"}, user_id=usuario.UserID
    )

    historial = GestionHistorialService.get_historial(db_session)
    ediciones = [log for log in historial if log.TipoAccion == "EDITAR"]

    assert ediciones == []


def test_eliminar_registro_borra_y_audita(db_session, usuario):
    nuevo = TablaService.agregar_registro(db_session, _datos_minimos(), user_id=usuario.UserID)
    accident_id = nuevo.AccidentID

    TablaService.eliminar_registro(db_session, accident_id, user_id=usuario.UserID)

    assert TablaService.obtener_registros(db_session) == []
    historial = GestionHistorialService.get_historial(db_session)
    assert any(log.TipoAccion == "ELIMINAR" and log.AccidentID == accident_id for log in historial)
