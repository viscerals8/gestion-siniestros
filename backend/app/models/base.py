# app/models/base.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List, Optional
from ..db.database import Base

# =========================================================================
# Tablas de Catálogo
# =========================================================================

class Rol(Base):
    __tablename__ = "Roles"
    RolID: Mapped[int] = mapped_column(primary_key=True)
    NombreRol: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="rol")

class Country(Base):
    __tablename__ = "Countries"
    CountryID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False)
    accidents: Mapped[List["Accident"]] = relationship(back_populates="country")

class Company(Base):
    __tablename__ = "Companies"
    CompanyID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    Contract: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Installation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    FechaCreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    FechaActualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    accidents: Mapped[List["Accident"]] = relationship(back_populates="company")
    contracts: Mapped[List["Contract"]] = relationship(back_populates="company")
    installations: Mapped[List["Installation"]] = relationship(back_populates="company")

class AccidentType(Base):
    __tablename__ = "AccidentTypes"
    TypeID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False)
    accidents: Mapped[List["Accident"]] = relationship(back_populates="type")

class AccidentState(Base):
    __tablename__ = "AccidentStates"
    StateID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False)
    accidents: Mapped[List["Accident"]] = relationship(back_populates="state")

class AccidentMatter(Base):
    __tablename__ = "AccidentMatters"
    MatterID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False)
    accidents: Mapped[List["Accident"]] = relationship(back_populates="matter")

class AccidentCategory(Base):
    __tablename__ = "AccidentCategories"
    CategoryID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False)
    Type: Mapped[str] = mapped_column(String(50), nullable=False)
    accidents_cat1: Mapped[List["Accident"]] = relationship(foreign_keys="[Accident.CategoryID1]", back_populates="category1")
    accidents_cat2: Mapped[List["Accident"]] = relationship(foreign_keys="[Accident.CategoryID2]", back_populates="category2")
    accidents_cat3: Mapped[List["Accident"]] = relationship(foreign_keys="[Accident.CategoryID3]", back_populates="category3")

# =========================================================================
# Tablas Principales
# =========================================================================

class User(Base):
    __tablename__ = "Users"
    UserID: Mapped[int] = mapped_column(primary_key=True, index=True)
    Nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    Correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    PasswordHash: Mapped[str] = mapped_column(String(255), nullable=False)
    RolID: Mapped[int] = mapped_column(ForeignKey("Roles.RolID"), nullable=False)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)
    FechaCreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    FechaActualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    rol: Mapped["Rol"] = relationship(back_populates="users")

class Accident(Base):
    __tablename__ = "Accidents"
    Unico: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    AccidentID: Mapped[int] = mapped_column(primary_key=True)
    JusttimeNumber: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    InitialDate: Mapped[Date] = mapped_column(Date, nullable=False)
    Year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Demandant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Defendant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Supervisor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    JOP: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ZonalDelegate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    Activity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    AccountingKey: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ClaimedAmount: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    EstimatedAmount: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    PreviousProvision: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    AdditionalDemand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    NonProvisionedAmount: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    ReversalAmount: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    FinalCost: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    FinalAttorneyCost: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    OtherExpenses: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    CloseDate: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    CloseComment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    FirstAccountingEstimate: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    SecondAccountingEstimate: Mapped[Optional[float]] = mapped_column(Numeric(18,2), nullable=True)
    Management: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    Modification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    OriginMotive: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Responsible: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    AppliedMeasure: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    Dimensions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Claves foráneas
    CompanyID: Mapped[int] = mapped_column(ForeignKey("Companies.CompanyID"))
    CountryID: Mapped[int] = mapped_column(ForeignKey("Countries.CountryID"))
    TypeID: Mapped[int] = mapped_column(ForeignKey("AccidentTypes.TypeID"))
    StateID: Mapped[int] = mapped_column(ForeignKey("AccidentStates.StateID"))
    MatterID: Mapped[int] = mapped_column(ForeignKey("AccidentMatters.MatterID"))
    CategoryID1: Mapped[Optional[int]] = mapped_column(ForeignKey("AccidentCategories.CategoryID"))
    CategoryID2: Mapped[Optional[int]] = mapped_column(ForeignKey("AccidentCategories.CategoryID"))
    CategoryID3: Mapped[Optional[int]] = mapped_column(ForeignKey("AccidentCategories.CategoryID"))

    company: Mapped["Company"] = relationship(back_populates="accidents")
    country: Mapped["Country"] = relationship(back_populates="accidents")
    type: Mapped["AccidentType"] = relationship(back_populates="accidents")
    state: Mapped["AccidentState"] = relationship(back_populates="accidents")
    matter: Mapped["AccidentMatter"] = relationship(back_populates="accidents")
    category1: Mapped["AccidentCategory"] = relationship(foreign_keys=[CategoryID1], back_populates="accidents_cat1")
    category2: Mapped["AccidentCategory"] = relationship(foreign_keys=[CategoryID2], back_populates="accidents_cat2")
    category3: Mapped["AccidentCategory"] = relationship(foreign_keys=[CategoryID3], back_populates="accidents_cat3")

    multas: Mapped[List["Multa"]] = relationship(back_populates="accident", cascade="all, delete-orphan")
    log: Mapped[List["AccidentLog"]] = relationship(back_populates="accident", cascade="all, delete-orphan")

    # === CONEXIÓN CON CAMPOS DINÁMICOS ===
    custom_field_values: Mapped[List["AccidentFieldValue"]] = relationship(back_populates="accident", cascade="all, delete-orphan")

class Multa(Base):
    __tablename__ = "Multas"
    MultaID: Mapped[int] = mapped_column(primary_key=True)
    MultaNumber: Mapped[str] = mapped_column(String(50), nullable=False)
    AccidentID: Mapped[int] = mapped_column(ForeignKey("Accidents.AccidentID"))
    accident: Mapped["Accident"] = relationship(back_populates="multas")

class AccidentLog(Base):
    __tablename__ = "AccidentLog"
    LogID: Mapped[int] = mapped_column(primary_key=True)
    Fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    UserID: Mapped[int] = mapped_column(ForeignKey("Users.UserID"))
    AccidentID: Mapped[int] = mapped_column(ForeignKey("Accidents.AccidentID"))
    TipoAccion: Mapped[str] = mapped_column(String(50), nullable=False)
    SeccionAfectada: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    CampoAfectado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ValorAnterior: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ValorNuevo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user: Mapped["User"] = relationship()
    accident: Mapped["Accident"] = relationship(back_populates="log")

# =========================================================================
# Normalización externa: Contracts, Installations, Projects
# =========================================================================

class Contract(Base):
    __tablename__ = "Contracts"
    ContractID: Mapped[int] = mapped_column(primary_key=True, index=True)
    ContractExternalID: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    Status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    CompanyID: Mapped[int] = mapped_column(ForeignKey("Companies.CompanyID"), nullable=False)

    FechaCreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    FechaActualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    company: Mapped["Company"] = relationship(back_populates="contracts")
    projects: Mapped[List["Project"]] = relationship(back_populates="contract")

class Installation(Base):
    __tablename__ = "Installations"
    InstallationID: Mapped[int] = mapped_column(primary_key=True, index=True)
    InstallationExternalID: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    Status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    City: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    Zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    CompanyID: Mapped[int] = mapped_column(ForeignKey("Companies.CompanyID"), nullable=False)

    FechaCreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    FechaActualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    company: Mapped["Company"] = relationship(back_populates="installations")
    projects: Mapped[List["Project"]] = relationship(back_populates="installation")

class Project(Base):
    __tablename__ = "Projects"
    ProjectID: Mapped[int] = mapped_column(primary_key=True, index=True)
    ProjectExternalID: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    Name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    ContractID: Mapped[int] = mapped_column(ForeignKey("Contracts.ContractID"), nullable=False)
    InstallationID: Mapped[int] = mapped_column(ForeignKey("Installations.InstallationID"), nullable=False)

    LineaVentaID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    LineaVentaName: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    DepartmentIDExt: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    DepartmentName: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    GroupIDExt: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    GroupName: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    FechaCreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    FechaActualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    contract: Mapped["Contract"] = relationship(back_populates="projects")
    installation: Mapped["Installation"] = relationship(back_populates="projects")

# =========================================================================
# Módulo de Campos Dinámicos (EAV)
# =========================================================================

class FormField(Base):
    __tablename__ = "FormFields"

    FieldId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    DataType: Mapped[str] = mapped_column(String(20), nullable=False)
    Required: Mapped[bool] = mapped_column(Boolean, default=False)
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    DisplayOrder: Mapped[int] = mapped_column(Integer, default=0)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    values: Mapped[List["AccidentFieldValue"]] = relationship(back_populates="field", cascade="all, delete-orphan")

class AccidentFieldValue(Base):
    __tablename__ = "AccidentFieldValues"

    ValueId: Mapped[int] = mapped_column(primary_key=True)
    AccidentId: Mapped[int] = mapped_column(ForeignKey("Accidents.AccidentID", ondelete="CASCADE"), nullable=False)
    FieldId: Mapped[int] = mapped_column(ForeignKey("FormFields.FieldId", ondelete="CASCADE"), nullable=False)
    Value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    accident: Mapped["Accident"] = relationship(back_populates="custom_field_values")
    field: Mapped["FormField"] = relationship(back_populates="values")