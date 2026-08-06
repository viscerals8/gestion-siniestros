from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from ..models.base import FormField

class FormFieldsService:
    """Servicio para manejar las definiciones de los campos dinámicos (FormFields)"""

    @staticmethod
    def get_fields(db: Session, only_active: bool = False) -> List[FormField]:
        query = db.query(FormField)
        if only_active:
            query = query.filter(FormField.Active == True)
        return query.order_by(FormField.DisplayOrder.asc()).all()

    @staticmethod
    def get_field(db: Session, field_id: int) -> FormField:
        field = db.query(FormField).filter(FormField.FieldId == field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Campo dinámico no encontrado")
        return field

    @staticmethod
    def crear_campo(db: Session, name: str, data_type: str, required: bool = False, active: bool = True, display_order: int = 0) -> FormField:
        existing_field = db.query(FormField).filter(FormField.Name == name).first()
        if existing_field:
            raise HTTPException(status_code=400, detail="Ya existe un campo con este nombre")
        
        nuevo_campo = FormField(
            Name=name,
            DataType=data_type,
            Required=required,
            Active=active,
            DisplayOrder=display_order
        )
        db.add(nuevo_campo)
        db.commit()
        db.refresh(nuevo_campo)
        return nuevo_campo

    @staticmethod
    def editar_campo(db: Session, field_id: int, name: Optional[str] = None, data_type: Optional[str] = None,
                     required: Optional[bool] = None, active: Optional[bool] = None, display_order: Optional[int] = None) -> FormField:
        campo = db.query(FormField).filter(FormField.FieldId == field_id).first()
        if not campo:
            raise HTTPException(status_code=404, detail="Campo dinámico no encontrado")
        
        if name:
            existing_field = db.query(FormField).filter(FormField.Name == name, FormField.FieldId != field_id).first()
            if existing_field:
                raise HTTPException(status_code=400, detail="Ya existe otro campo registrado con ese nombre")
            campo.Name = name
        if data_type:
            campo.DataType = data_type
        if required is not None:
            campo.Required = required
        if active is not None:
            campo.Active = active
        if display_order is not None:
            campo.DisplayOrder = display_order
            
        db.commit()
        db.refresh(campo)
        return campo

    @staticmethod
    def eliminar_campo(db: Session, field_id: int):
        campo = db.query(FormField).filter(FormField.FieldId == field_id).first()
        if not campo:
            raise HTTPException(status_code=404, detail="Campo dinámico no encontrado")
        
        db.delete(campo)
        db.commit()
        return {"detail": "Campo dinámico eliminado permanentemente"}