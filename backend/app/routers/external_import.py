from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..schemas import ExternalProjectImport
from ..services.external_import_service import import_external_projects_service  # ← IMPORT CLAVE
from ..utils.security import get_current_user

router = APIRouter(prefix="/import", tags=["Importación"], dependencies=[Depends(get_current_user)])

@router.post("/external-projects")
def import_external_projects_endpoint(payload: ExternalProjectImport, db: Session = Depends(get_db)):
    return import_external_projects_service(db, payload)

# (opcional) ping para confirmar prefijo/ruta
@router.get("/ping")
def ping():
    return {"ok": True, "path": "/api/import/ping"}
