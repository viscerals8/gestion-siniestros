from typing import Optional, Dict, Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.base import Company, Contract, Installation, Project
from ..schemas import ExternalProjectImport, ExternalProjectItem

# ----------------- helpers internos -----------------

def _upsert_company(db: Session, name: str) -> Company:
    c = db.query(Company).filter(Company.Name == name).first()
    if not c:
        c = Company(Name=name)
        db.add(c)
        db.flush()
    return c

def _upsert_contract(db: Session, company_id: int,
                     ext_id: Optional[str], name: Optional[str], status: Optional[str]) -> Contract:
    ct = db.query(Contract).filter(Contract.ContractExternalID == ext_id).first() if ext_id else None
    if not ct and name:
        ct = (db.query(Contract)
              .filter(Contract.CompanyID == company_id, Contract.Name == name)
              .first())
    if not ct:
        ct = Contract(CompanyID=company_id)
        db.add(ct)
    if ext_id: ct.ContractExternalID = ext_id
    if name:   ct.Name = name
    if status: ct.Status = status
    db.flush()
    return ct

def _upsert_installation(db: Session, company_id: int,
                         ext_id: Optional[str], name: Optional[str], status: Optional[str],
                         city: Optional[str], zone: Optional[str]) -> Installation:
    it = db.query(Installation).filter(Installation.InstallationExternalID == ext_id).first() if ext_id else None
    if not it and name:
        it = (db.query(Installation)
              .filter(Installation.CompanyID == company_id, Installation.Name == name)
              .first())
    if not it:
        it = Installation(CompanyID=company_id)
        db.add(it)
    if ext_id: it.InstallationExternalID = ext_id
    if name:   it.Name = name
    if status: it.Status = status
    if city:   it.City = city
    if zone:   it.Zone = zone
    db.flush()
    return it

def _upsert_project(db: Session, ext_id: Optional[str], name: Optional[str],
                    contract_id: int, installation_id: int,
                    lv_id: Optional[str], lv_name: Optional[str],
                    dept_id: Optional[str], dept_name: Optional[str],
                    grp_id: Optional[str], grp_name: Optional[str]) -> Project:
    pr = db.query(Project).filter(Project.ProjectExternalID == ext_id).first() if ext_id else None
    if not pr:
        pr = (db.query(Project)
              .filter(Project.ContractID == contract_id, Project.InstallationID == installation_id)
              .first())
    if not pr:
        pr = Project(ContractID=contract_id, InstallationID=installation_id)
        db.add(pr)
    if ext_id:    pr.ProjectExternalID = ext_id
    if name:      pr.Name = name
    if lv_id:     pr.LineaVentaID = lv_id
    if lv_name:   pr.LineaVentaName = lv_name
    if dept_id:   pr.DepartmentIDExt = dept_id
    if dept_name: pr.DepartmentName = dept_name
    if grp_id:    pr.GroupIDExt = grp_id
    if grp_name:  pr.GroupName = grp_name
    db.flush()
    return pr

# ----------------- API del service -----------------

def import_external_projects_service(db: Session, payload: ExternalProjectImport) -> dict:
    items: List[ExternalProjectItem] = payload.root  # RootModel en Pydantic v2
    if not items:
        raise HTTPException(status_code=400, detail="Body vacío o inválido (se esperaba lista)")

    stats = {"companies": 0, "contracts": 0, "installations": 0, "projects": 0}
    comp_cache: Dict[str, int] = {}
    contract_cache: Dict[Tuple[int, Optional[str], Optional[str]], int] = {}
    inst_cache: Dict[Tuple[int, Optional[str], Optional[str]], int] = {}

    try:
        for it in items:
            # 1) Company
            cname = (it.EMPRESA or "").strip()
            if not cname:
                raise HTTPException(status_code=422, detail="EMPRESA es requerido")
            if cname in comp_cache:
                company_id = comp_cache[cname]
            else:
                company = _upsert_company(db, cname)
                company_id = company.CompanyID
                comp_cache[cname] = company_id
                stats["companies"] += 1

            # 2) Contract
            key_ct = (company_id, it.ID_CONTRATO, (it.NOMBRE_CONTRATO or "").strip() or None)
            if key_ct in contract_cache:
                contract_id = contract_cache[key_ct]
            else:
                contract = _upsert_contract(db, company_id, it.ID_CONTRATO, it.NOMBRE_CONTRATO, it.ESTADO_CONTRATO)
                contract_id = contract.ContractID
                contract_cache[key_ct] = contract_id
                stats["contracts"] += 1

            # 3) Installation
            key_it = (company_id, it.ID_INSTALACION, (it.NOMBRE_INSTALACION or "").strip() or None)
            if key_it in inst_cache:
                installation_id = inst_cache[key_it]
            else:
                inst = _upsert_installation(
                    db, company_id, it.ID_INSTALACION, it.NOMBRE_INSTALACION,
                    it.ESTADO_INSTALACION, it.CIUDAD, it.ZONA
                )
                installation_id = inst.InstallationID
                inst_cache[key_it] = installation_id
                stats["installations"] += 1

            # 4) Project
            _upsert_project(
                db,
                it.ID_PROYECTO, it.NOMBRE_PROYECTO,
                contract_id, installation_id,
                it.ID_LINEA_VENTA, it.NOMBRE_LINEA_VENTA,
                it.ID_DEPARTAMENTO, it.NOMBRE_DEPARTAMENTO,
                it.ID_GRUPO, it.NOMBRE_GRUPO,
            )
            stats["projects"] += 1

        db.commit()
        return {"ok": True, "stats": stats}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en importación: {e}")


__all__ = ["import_external_projects_service"]
