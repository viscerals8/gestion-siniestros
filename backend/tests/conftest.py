from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.models import base as models  # noqa: F401  (registra todos los modelos en Base.metadata)
from app.models.base import Rol, User, Company, Country, AccidentType, AccidentState, AccidentMatter, Accident


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def usuario(db_session):
    rol = Rol(NombreRol="Administrador")
    db_session.add(rol)
    db_session.flush()

    user = User(
        Nombre="Usuaria de prueba",
        Correo="prueba@example.com",
        PasswordHash="hash-no-usado-en-estos-tests",
        RolID=rol.RolID,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def accidente(db_session):
    company = Company(Name="Compañía de prueba")
    country = Country(Name="España")
    tipo = AccidentType(Name="Laboral")
    estado = AccidentState(Name="Abierto")
    materia = AccidentMatter(Name="General")
    db_session.add_all([company, country, tipo, estado, materia])
    db_session.flush()

    accidente = Accident(
        InitialDate=date(2026, 1, 1),
        CompanyID=company.CompanyID,
        CountryID=country.CountryID,
        TypeID=tipo.TypeID,
        StateID=estado.StateID,
        MatterID=materia.MatterID,
    )
    db_session.add(accidente)
    db_session.commit()
    return accidente
