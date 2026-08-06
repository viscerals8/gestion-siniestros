from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict, Any, Optional
from ..models.base import (
    Accident,
    Company,
    Country,
    AccidentType,
    AccidentState,
    AccidentMatter,
    FormField,            # Importación de modelos dinámicos
    AccidentFieldValue    # Importación de modelos dinámicos
)
from ..services.gestion_historial_service import GestionHistorialService

# =========================================================================
# Helpers y mapeos para el logging
# =========================================================================
SECCION_MAP = {
    # Identificación
    "JusttimeNumber": "Identificación", "InitialDate": "Identificación", "Year": "Identificación",
    "CountryID": "Identificación",
    # Datos generales
    "IDEntidad": "Datos generales", "Demandant": "Datos generales", "Defendant": "Datos generales",
    "CompanyID": "Datos generales", "Dimensions": "Datos generales", "Contrato": "Datos generales",
    "Instalacion": "Datos generales", "Supervisor": "Datos generales", "JOP": "Datos generales",
    "ZonalDelegate": "Datos generales", "Zone": "Datos generales", "TypeID": "Datos generales",
    "Activity": "Datos generales", "AccountingKey": "Datos generales", "BeenProcessing": "Datos generales",
    "Motivo": "Datos generales", "MatterID": "Datos generales",
    # Costos
    "ClaimedAmount": "Costos", "EstimatedAmount": "Costos", "PreviousProvision": "Costos",
    "AdditionalDemand": "Costos", "NonProvisionedAmount": "Costos", "ReversalAmount": "Costos",
    "FinalCost": "Costos", "FinalAttorneyCost": "Costos", "OtherExpenses": "Costos",
    # Cierre
    "CloseDate": "Cierre", "PenaltyNumber": "Cierre", "CloseComment": "Cierre",
    "FirstAccountingEstimate": "Cierre", "SecondAccountingEstimate": "Cierre",
    # Categorías
    "Category1": "Categorías", "Category2": "Categorías", "Category3": "Categorías",
    # Gestión y fiscalización
    "Management": "Gestión y fiscalización", "Modification": "Gestión y fiscalización", "Categoria": "Gestión y fiscalización",
    "InspectionDate": "Gestión y fiscalización", "PeriodoFiscalizado": "Gestión y fiscalización",
    "Department": "Gestión y fiscalización", "Responsible": "Gestión y fiscalización",
    "AppliedMeasure": "Gestión y fiscalización", "Estado": "Gestión y fiscalización",
    "DimensionesFinal": "Gestión y fiscalización", "Comentarios": "Gestión y fiscalización",
    "EstadoContrato": "Gestión y fiscalización", "EstadoInstalacion": "Gestión y fiscalización",
    "NombreGrupo": "Gestión y fiscalización", "NombreInstalacion": "Gestión y fiscalización",
}

def _nombre_relacional(db: Session, modelo, id_val: Optional[int], pk_name: str, name_field: str = "Name") -> Optional[str]:
    if id_val is None:
        return None
    obj = db.query(modelo).filter(getattr(modelo, pk_name) == id_val).first()
    return getattr(obj, name_field) if obj else None

def _to_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v)

def _inyectar_custom_fields(db: Session, registro: Accident) -> Accident:
    """Helper interno para transformar la lista relacional en un diccionario plano para el frontend"""
    if not registro:
        return registro
    
    dict_dinamico = {}
    for val in registro.custom_field_values:
        if val.field:
            dict_dinamico[val.field.Name] = val.Value
            
    # Añadimos la propiedad de forma dinámica al objeto para que sea parseada por AccidentResponse
    registro.custom_fields = dict_dinamico
    return registro


class TablaService:
    """Servicio mejorado para manejar inserciones y actualizaciones relacionales e híbridas de Accident"""

    # =========================================================================
    # OBTENER REGISTROS
    # =========================================================================
    @staticmethod
    def obtener_registros(db: Session) -> List[Accident]:
        registros = db.query(Accident).all()
        for r in registros:
            _inyectar_custom_fields(db, r)
        return registros

    @staticmethod
    def obtener_registro(db: Session, registro_id: int) -> Accident:
        registro = db.query(Accident).filter(Accident.AccidentID == registro_id).first()
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return _inyectar_custom_fields(db, registro)

    # =========================================================================
    # AGREGAR NUEVO (con persistencia híbrida y auditoría dinámica)
    # =========================================================================
    @staticmethod
    def agregar_registro(db: Session, datos: Dict[str, Any], user_id: int) -> Accident:
        """Inserta un nuevo registro fijo, procesa su mapa dinámico EAV y genera logs automáticos."""
        
        # Extraer de forma aislada el diccionario de campos dinámicos
        custom_fields_input = datos.pop("custom_fields", None) or {}

        def procesar_relacion(campo: str, modelo, clave: str = "Name"):
            valor = datos.pop(campo, None)
            if not valor:
                return None
            if isinstance(valor, str):
                valor = {clave: valor.strip()}
            if not isinstance(valor, dict) or not valor.get(clave):
                return None
            nombre = valor[clave]
            existente = db.query(modelo).filter(getattr(modelo, clave) == nombre).first()
            if not existente:
                existente = modelo(**valor)
                db.add(existente)
                db.flush()
            return existente

        relaciones = {}
        for campo, modelo in {
            "Company": Company,
            "Country": Country,
            "Type": AccidentType,
            "State": AccidentState,
            "Matter": AccidentMatter,
        }.items():
            obj = procesar_relacion(campo, modelo)
            if obj:
                relaciones[f"{campo}ID"] = getattr(obj, f"{campo}ID")

        columnas_validas = {col.name for col in Accident.__table__.columns}
        datos_filtrados = {k: v for k, v in datos.items() if k in columnas_validas}

        try:
            nuevo = Accident(**datos_filtrados, **relaciones)
            db.add(nuevo)
            db.flush()  # Genera el AccidentID crítico para las claves dinámicas externas

            # LOG: un registro por cada campo fijo seteado al crear
            for campo, valor in {**datos_filtrados, **relaciones}.items():
                if campo == "CompanyID":
                    valor_str = _nombre_relacional(db, Company, valor, "CompanyID")
                elif campo == "CountryID":
                    valor_str = _nombre_relacional(db, Country, valor, "CountryID")
                elif campo == "TypeID":
                    valor_str = _nombre_relacional(db, AccidentType, valor, "TypeID")
                elif campo == "StateID":
                    valor_str = _nombre_relacional(db, AccidentState, valor, "StateID")
                elif campo == "MatterID":
                    valor_str = _nombre_relacional(db, AccidentMatter, valor, "MatterID")
                else:
                    valor_str = _to_str(valor)

                GestionHistorialService.agregar_historial(
                    db=db,
                    user_id=user_id,
                    accident_id=nuevo.AccidentID,
                    tipo_accion="CREAR",
                    seccion_afectada=SECCION_MAP.get(campo, "Otros"),
                    campo_afectado=campo,
                    valor_anterior=None,
                    valor_nuevo=valor_str,
                )

            # PERSISTENCIA DINÁMICA: Procesamiento de custom_fields recibidos
            if custom_fields_input and isinstance(custom_fields_input, dict):
                for f_name, f_value in custom_fields_input.items():
                    if f_value is None or _to_str(f_value).strip() == "":
                        continue
                        
                    # Validar existencia y estado del campo dinámico en el formulario administrativo
                    meta_field = db.query(FormField).filter(FormField.Name == f_name, FormField.Active == True).first()
                    if meta_field:
                        nuevo_val_dinamico = AccidentFieldValue(
                            AccidentId=nuevo.AccidentID,
                            FieldId=meta_field.FieldId,
                            Value=_to_str(f_value)
                        )
                        db.add(nuevo_val_dinamico)
                        
                        # Guardar el campo dinámico en el historial de auditoría bajo su respectiva sección
                        GestionHistorialService.agregar_historial(
                            db=db,
                            user_id=user_id,
                            accident_id=nuevo.AccidentID,
                            tipo_accion="CREAR",
                            seccion_afectada="Campos Personalizados",
                            campo_afectado=f_name,
                            valor_anterior=None,
                            valor_nuevo=_to_str(f_value),
                        )

            db.commit()
            db.refresh(nuevo)
            return _inyectar_custom_fields(db, nuevo)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error al insertar registro híbrido: {e}")

    # =========================================================================
    # ACTUALIZAR EXISTENTE (con sincronización EAV e historial diferencial)
    # =========================================================================
    @staticmethod
    def actualizar_registro(db: Session, registro_id: int, datos: Dict[str, Any], user_id: int) -> Accident:
        """Actualiza el núcleo estructural del accidente, reconcilia campos dinámicos y audita el diferencial."""
        registro = db.query(Accident).filter(Accident.AccidentID == registro_id).first()
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        # Extraer de forma aislada el diccionario de cambios dinámicos
        custom_fields_input = datos.pop("custom_fields", None)

        # Snapshot previo de campos estructurales fijos
        prev = {c.name: getattr(registro, c.name) for c in Accident.__table__.columns}

        def procesar_relacion(campo: str, modelo, clave: str = "Name", fkname: str = ""):
            valor = datos.pop(campo, None)
            if not valor:
                return None
            if isinstance(valor, str):
                valor = {clave: valor.strip()}
            if not isinstance(valor, dict) or not valor.get(clave):
                return None
            nombre = valor[clave]
            existente = db.query(modelo).filter(getattr(modelo, clave) == nombre).first()
            if not existente:
                existente = modelo(**valor)
                db.add(existente)
                db.flush()
            return {fkname: getattr(existente, fkname)}

        relaciones = {}
        for campo, (modelo, fkname) in {
            "Company": (Company, "CompanyID"),
            "Country": (Country, "CountryID"),
            "Type": (AccidentType, "TypeID"),
            "State": (AccidentState, "StateID"),
            "Matter": (AccidentMatter, "MatterID"),
        }.items():
            res = procesar_relacion(campo, modelo, fkname=fkname)
            if res:
                relaciones.update(res)

        columnas_validas = {col.name for col in Accident.__table__.columns}
        datos_filtrados = {k: v for k, v in datos.items() if k in columnas_validas}
        cambios = {**datos_filtrados, **relaciones}

        # Aplicar cambios sobre el núcleo del registro
        for key, value in cambios.items():
            setattr(registro, key, value)

        try:
            db.flush()

            # Auditoría diferencial para campos Core fijos
            for campo, nuevo_val in cambios.items():
                viejo_val = prev.get(campo)

                if campo == "CompanyID":
                    viejo_leg = _nombre_relacional(db, Company, viejo_val, "CompanyID")
                    nuevo_leg = _nombre_relacional(db, Company, nuevo_val, "CompanyID")
                elif campo == "CountryID":
                    viejo_leg = _nombre_relacional(db, Country, viejo_val, "CountryID")
                    nuevo_leg = _nombre_relacional(db, Country, nuevo_val, "CountryID")
                elif campo == "TypeID":
                    viejo_leg = _nombre_relacional(db, AccidentType, viejo_val, "TypeID")
                    nuevo_leg = _nombre_relacional(db, AccidentType, nuevo_val, "TypeID")
                elif campo == "StateID":
                    viejo_leg = _nombre_relacional(db, AccidentState, viejo_val, "StateID")
                    nuevo_leg = _nombre_relacional(db, AccidentState, nuevo_val, "StateID")
                elif campo == "MatterID":
                    viejo_leg = _nombre_relacional(db, AccidentMatter, viejo_val, "MatterID")
                    nuevo_leg = _nombre_relacional(db, AccidentMatter, nuevo_val, "MatterID")
                else:
                    viejo_leg, nuevo_leg = _to_str(viejo_val), _to_str(nuevo_val)

                if (viejo_leg or "") != (nuevo_leg or ""):
                    GestionHistorialService.agregar_historial(
                        db=db,
                        user_id=user_id,
                        accident_id=registro.AccidentID,
                        tipo_accion="EDITAR",
                        seccion_afectada=SECCION_MAP.get(campo, "Otros"),
                        campo_afectado=campo,
                        valor_anterior=viejo_leg,
                        valor_nuevo=nuevo_leg
                    )

            # SINCRONIZACIÓN DINÁMICA (EAV): Comparación y guardado de custom_fields
            if custom_fields_input is not None and isinstance(custom_fields_input, dict):
                for f_name, f_value in custom_fields_input.items():
                    meta_field = db.query(FormField).filter(FormField.Name == f_name, FormField.Active == True).first()
                    if not meta_field:
                        continue
                    
                    # Buscar si ya existía un valor anterior asignado a este accidente para este campo específico
                    db_val_existente = db.query(AccidentFieldValue).filter(
                        AccidentFieldValue.AccidentId == registro.AccidentID,
                        AccidentFieldValue.FieldId == meta_field.FieldId
                    ).first()

                    val_nuevo_str = _to_str(f_value) if f_value is not None else ""
                    val_viejo_str = db_val_existente.Value if db_val_existente else ""

                    if val_viejo_str != val_nuevo_str:
                        if db_val_existente:
                            # Caso 1: Modificación de un valor dinámico existente
                            db_val_existente.Value = val_nuevo_str
                        else:
                            # Caso 2: El campo existía en el catálogo pero no se le había asignado valor a este accidente
                            nuevo_valor_eav = AccidentFieldValue(
                                AccidentId=registro.AccidentID,
                                FieldId=meta_field.FieldId,
                                Value=val_nuevo_str
                            )
                            db.add(nuevo_valor_eav)

                        # Inyección del cambio dinámico en tu bitácora general de auditoría
                        GestionHistorialService.agregar_historial(
                            db=db,
                            user_id=user_id,
                            accident_id=registro.AccidentID,
                            tipo_accion="EDITAR",
                            seccion_afectada="Campos Personalizados",
                            campo_afectado=f_name,
                            valor_anterior=val_viejo_str if db_val_existente else None,
                            valor_nuevo=val_nuevo_str,
                        )

            db.commit()
            db.refresh(registro)
            return _inyectar_custom_fields(db, registro)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error al actualizar registro híbrido: {e}")

    # =========================================================================
    # ELIMINAR (con log de eliminación)
    # =========================================================================
    @staticmethod
    def eliminar_registro(db: Session, registro_id: int, user_id: int) -> None:
        registro = db.query(Accident).filter(Accident.AccidentID == registro_id).first()
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        try:
            GestionHistorialService.agregar_historial(
                db=db,
                user_id=user_id,
                accident_id=registro.AccidentID,
                tipo_accion="ELIMINAR",
                seccion_afectada="Accidente",
                campo_afectado="*",
                valor_anterior="REGISTRO EXISTENTE",
                valor_nuevo="REGISTRO ELIMINADO",
            )
            db.delete(registro)
            db.commit()
        except Exception:
            db.rollback()
            raise