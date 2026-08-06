from pydantic import BaseModel, EmailStr, RootModel
from datetime import datetime
from typing import List, Optional, Dict  #  Usamos "Dict" con mayúscula

# -------------------------------------------------------------------------
# Esquema para Rol
# -------------------------------------------------------------------------
class Rol(BaseModel):
    RolID: int
    NombreRol: str

    class Config:
        from_attributes = True


# -------------------------------------------------------------------------
# Esquemas para Usuario
# -------------------------------------------------------------------------
class UserBase(BaseModel):
    Nombre: str
    Correo: EmailStr
    RolID: int
    Activo: bool = True


class UserCreate(UserBase):
    PasswordHash: str   # Solo se usa al crear usuario


class UserUpdate(BaseModel):
    Nombre: Optional[str] = None
    Correo: Optional[EmailStr] = None
    RolID: Optional[int] = None
    Activo: Optional[bool] = None
    PasswordHash: Optional[str] = None


class User(UserBase):
    UserID: int
    FechaCreacion: datetime
    FechaActualizacion: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------------------
# Esquemas de importación (otra API → normalización)
# -------------------------------------------------------------------------
class ExternalProjectItem(BaseModel):
    # Campos tal como vienen del JSON externo
    EMPRESA: str
    NOMBRE_CONTRATO: Optional[str] = None
    NOMBRE_INSTALACION: Optional[str] = None
    CIUDAD: Optional[str] = None
    ZONA: Optional[str] = None
    ID_PROYECTO: Optional[str] = None
    ID_CONTRATO: Optional[str] = None
    ID_INSTALACION: Optional[str] = None
    ESTADO_CONTRATO: Optional[str] = None
    ESTADO_INSTALACION: Optional[str] = None
    NOMBRE_LINEA_VENTA: Optional[str] = None
    ID_LINEA_VENTA: Optional[str] = None
    NOMBRE_DEPARTAMENTO: Optional[str] = None
    ID_DEPARTAMENTO: Optional[str] = None
    NOMBRE_GRUPO: Optional[str] = None
    ID_GRUPO: Optional[str] = None
    NOMBRE_PROYECTO: Optional[str] = None


class ExternalProjectImport(RootModel[List[ExternalProjectItem]]):
    pass


# =========================================================================
# Esquemas para Módulo de Campos Dinámicos (EAV)
# =========================================================================

# --- Esquemas de Administración de FormFields ---
class FormFieldBase(BaseModel):
    Name: str
    DataType: str  # 'text', 'number', 'date', 'boolean' [cite: 196, 211]
    Required: bool = False
    Active: bool = True
    DisplayOrder: int = 0

class FormFieldCreate(FormFieldBase):
    pass

class FormFieldUpdate(BaseModel):
    Name: Optional[str] = None
    DataType: Optional[str] = None
    Required: Optional[bool] = None
    Active: Optional[bool] = None
    DisplayOrder: Optional[int] = None

class FormField(FormFieldBase):
    FieldId: int
    CreatedAt: datetime

    class Config:
        from_attributes = True


# --- Esquemas de Valores (Respuestas) ---
class AccidentFieldValueResponse(BaseModel):
    FieldId: int
    Name: str
    Value: Optional[str] = None

    class Config:
        from_attributes = True


# --- Esquema Principal de Siniestros (Accidents) con Campos Dinámicos ---
class AccidentBase(BaseModel):
    Unico: Optional[int] = None
    JusttimeNumber: Optional[str] = None
    InitialDate: datetime
    Year: Optional[int] = None
    Demandant: Optional[str] = None
    Defendant: Optional[str] = None
    Supervisor: Optional[str] = None
    JOP: Optional[str] = None
    ZonalDelegate: Optional[str] = None
    Zone: Optional[str] = None
    Activity: Optional[str] = None
    AccountingKey: Optional[str] = None
    ClaimedAmount: Optional[float] = None
    EstimatedAmount: Optional[float] = None
    PreviousProvision: Optional[float] = None
    AdditionalDemand: Optional[str] = None
    NonProvisionedAmount: Optional[float] = None
    ReversalAmount: Optional[float] = None
    FinalCost: Optional[float] = None
    FinalAttorneyCost: Optional[float] = None
    OtherExpenses: Optional[float] = None
    CloseDate: Optional[datetime] = None
    CloseComment: Optional[str] = None
    FirstAccountingEstimate: Optional[float] = None
    SecondAccountingEstimate: Optional[float] = None
    Management: Optional[str] = None
    Modification: Optional[str] = None
    OriginMotive: Optional[str] = None
    Responsible: Optional[str] = None
    AppliedMeasure: Optional[str] = None
    Dimensions: Optional[str] = None
    CompanyID: int
    CountryID: int
    TypeID: int
    StateID: int
    MatterID: int
    CategoryID1: Optional[int] = None
    CategoryID2: Optional[int] = None
    CategoryID3: Optional[int] = None

class AccidentCreate(AccidentBase):
    # Permite recibir un diccionario plano con los valores dinámicos al crear
    custom_fields: Optional[Dict] = None 

class AccidentUpdate(BaseModel):
    # Todos los campos fijos opcionales para actualizaciones parciales (PATCH/PUT)
    Unico: Optional[int] = None
    JusttimeNumber: Optional[str] = None
    InitialDate: Optional[datetime] = None
    Year: Optional[int] = None
    Demandant: Optional[str] = None
    Defendant: Optional[str] = None
    Supervisor: Optional[str] = None
    JOP: Optional[str] = None
    ZonalDelegate: Optional[str] = None
    Zone: Optional[str] = None
    Activity: Optional[str] = None
    AccountingKey: Optional[str] = None
    ClaimedAmount: Optional[float] = None
    EstimatedAmount: Optional[float] = None
    PreviousProvision: Optional[float] = None
    AdditionalDemand: Optional[str] = None
    NonProvisionedAmount: Optional[float] = None
    ReversalAmount: Optional[float] = None
    FinalCost: Optional[float] = None
    FinalAttorneyCost: Optional[float] = None
    OtherExpenses: Optional[float] = None
    CloseDate: Optional[datetime] = None
    CloseComment: Optional[str] = None
    FirstAccountingEstimate: Optional[float] = None
    SecondAccountingEstimate: Optional[float] = None
    Management: Optional[str] = None
    Modification: Optional[str] = None
    OriginMotive: Optional[str] = None
    Responsible: Optional[str] = None
    AppliedMeasure: Optional[str] = None
    Dimensions: Optional[str] = None
    CompanyID: Optional[int] = None
    CountryID: Optional[int] = None
    TypeID: Optional[int] = None
    StateID: Optional[int] = None
    MatterID: Optional[int] = None
    CategoryID1: Optional[int] = None
    CategoryID2: Optional[int] = None
    CategoryID3: Optional[int] = None
    
    # Recibe los campos dinámicos a actualizar o añadir
    custom_fields: Optional[Dict] = None 

class AccidentResponse(AccidentBase):
    AccidentID: int
    # En la salida transformaremos la lista relacional en un objeto JSON limpio
    custom_fields: Dict = {}

    class Config:
        from_attributes = True