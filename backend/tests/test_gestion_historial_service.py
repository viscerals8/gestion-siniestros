import pytest
from fastapi import HTTPException

from app.services.gestion_historial_service import GestionHistorialService


def test_agregar_historial_crea_registro(db_session, usuario, accidente):
    log = GestionHistorialService.agregar_historial(
        db=db_session,
        user_id=usuario.UserID,
        accident_id=accidente.AccidentID,
        tipo_accion="CREAR",
        campo_afectado="Zone",
        valor_anterior=None,
        valor_nuevo="Norte",
    )

    assert log.LogID is not None
    assert log.UserID == usuario.UserID
    assert log.AccidentID == accidente.AccidentID
    assert log.ValorNuevo == "Norte"


def test_agregar_historial_falla_si_usuario_no_existe(db_session, accidente):
    with pytest.raises(HTTPException) as exc_info:
        GestionHistorialService.agregar_historial(
            db=db_session,
            user_id=9999,
            accident_id=accidente.AccidentID,
            tipo_accion="CREAR",
        )
    assert exc_info.value.status_code == 422


def test_agregar_historial_falla_si_accidente_no_existe(db_session, usuario):
    with pytest.raises(HTTPException) as exc_info:
        GestionHistorialService.agregar_historial(
            db=db_session,
            user_id=usuario.UserID,
            accident_id=9999,
            tipo_accion="CREAR",
        )
    assert exc_info.value.status_code == 422


def test_get_historial_ordena_por_mas_reciente_primero(db_session, usuario, accidente):
    primero = GestionHistorialService.agregar_historial(
        db=db_session, user_id=usuario.UserID, accident_id=accidente.AccidentID,
        tipo_accion="CREAR", campo_afectado="Zone", valor_nuevo="Norte",
    )
    segundo = GestionHistorialService.agregar_historial(
        db=db_session, user_id=usuario.UserID, accident_id=accidente.AccidentID,
        tipo_accion="EDITAR", campo_afectado="Zone", valor_anterior="Norte", valor_nuevo="Sur",
    )

    resultados = GestionHistorialService.get_historial(db_session)

    assert [r.LogID for r in resultados] == [segundo.LogID, primero.LogID]


def test_filtrar_historial_por_campo(db_session, usuario, accidente):
    GestionHistorialService.agregar_historial(
        db=db_session, user_id=usuario.UserID, accident_id=accidente.AccidentID,
        tipo_accion="EDITAR", campo_afectado="Zone", valor_nuevo="Norte",
    )
    GestionHistorialService.agregar_historial(
        db=db_session, user_id=usuario.UserID, accident_id=accidente.AccidentID,
        tipo_accion="EDITAR", campo_afectado="Supervisor", valor_nuevo="Alguien",
    )

    resultados = GestionHistorialService.filtrar_historial(db_session, campo="zone")

    assert len(resultados) == 1
    assert resultados[0].CampoAfectado == "Zone"
