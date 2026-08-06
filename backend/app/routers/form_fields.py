from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.form_fields_service import FormFieldsService
from ..db.database import get_db
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

router = APIRouter(
    prefix="/form-fields",
    tags=["Campos Dinámicos"]
)

# Schemas de entrada (Uso de snake_case para contratos JSON frontend)
class FormFieldRequest(BaseModel):
    name: str
    data_type: str  # 'text', 'number', 'date', 'boolean'
    required: Optional[bool] = False
    active: Optional[bool] = True
    display_order: Optional[int] = 0

class FormFieldUpdateRequest(BaseModel):
    name: Optional[str] = None
    data_type: Optional[str] = None
    required: Optional[bool] = None
    active: Optional[bool] = None
    display_order: Optional[int] = None

# Schema de salida con aliases dirigidos a los atributos en mayúsculas del ORM
class FormFieldResponse(BaseModel):
    id: int = Field(alias="FieldId")
    name: str = Field(alias="Name")
    data_type: str = Field(alias="DataType")
    required: bool = Field(alias="Required")
    active: bool = Field(alias="Active")
    display_order: int = Field(alias="DisplayOrder")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Endpoints
@router.get("/", response_model=List[FormFieldResponse], response_model_by_alias=False)
def get_fields(active: bool = False, db: Session = Depends(get_db)):
    return FormFieldsService.get_fields(db, only_active=active)

@router.get("/{field_id}", response_model=FormFieldResponse, response_model_by_alias=False)
def get_field(field_id: int, db: Session = Depends(get_db)):
    return FormFieldsService.get_field(db, field_id=field_id)

@router.post("/", response_model=FormFieldResponse, response_model_by_alias=False)
def crear_campo(datos: FormFieldRequest, db: Session = Depends(get_db)):
    return FormFieldsService.crear_campo(
        db,
        name=datos.name,
        data_type=datos.data_type,
        required=datos.required,
        active=datos.active,
        display_order=datos.display_order
    )

@router.put("/{field_id}", response_model=FormFieldResponse, response_model_by_alias=False)
def editar_campo(field_id: int, datos: FormFieldUpdateRequest, db: Session = Depends(get_db)):
    return FormFieldsService.editar_campo(
        db,
        field_id=field_id,
        name=datos.name,
        data_type=datos.data_type,
        required=datos.required,
        active=datos.active,
        display_order=datos.display_order
    )

@router.delete("/{field_id}")
def eliminar_campo(field_id: int, db: Session = Depends(get_db)):
    return FormFieldsService.eliminar_campo(db, field_id=field_id)