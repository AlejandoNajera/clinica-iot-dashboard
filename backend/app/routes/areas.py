"""
Endpoints CRUD para el recurso Área.

Rutas:
  POST   /api/v1/areas          → Crear área
  GET    /api/v1/areas          → Listar todas las áreas
  GET    /api/v1/areas/{id}     → Obtener área por ID
  PUT    /api/v1/areas/{id}     → Actualizar área completa
  DELETE /api/v1/areas/{id}     → Eliminar área
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.models import Area
from backend.app.schemas.schemas import AreaCreate, AreaUpdate, AreaOut

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /areas
# ---------------------------------------------------------------------------
@router.post("/areas", response_model=AreaOut, status_code=status.HTTP_201_CREATED)
def crear_area(payload: AreaCreate, db: Session = Depends(get_db)):
    """Registra una nueva área en el sistema."""
    # Verificar nombre duplicado
    existe = db.query(Area).filter(Area.nombre == payload.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un área con el nombre '{payload.nombre}'."
        )
    nueva_area = Area(**payload.model_dump())
    db.add(nueva_area)
    db.commit()
    db.refresh(nueva_area)
    return nueva_area


# ---------------------------------------------------------------------------
# GET /areas
# ---------------------------------------------------------------------------
@router.get("/areas", response_model=list[AreaOut])
def listar_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna la lista de todas las áreas registradas."""
    return db.query(Area).offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# GET /areas/{area_id}
# ---------------------------------------------------------------------------
@router.get("/areas/{area_id}", response_model=AreaOut)
def obtener_area(area_id: int, db: Session = Depends(get_db)):
    """Retorna una área específica por su ID."""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Área con id={area_id} no encontrada."
        )
    return area


# ---------------------------------------------------------------------------
# PUT /areas/{area_id}
# ---------------------------------------------------------------------------
@router.put("/areas/{area_id}", response_model=AreaOut)
def actualizar_area(area_id: int, payload: AreaUpdate, db: Session = Depends(get_db)):
    """Actualiza los datos de un área existente (solo los campos enviados)."""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail=f"Área con id={area_id} no encontrada.")

    # Actualiza solo los campos que vienen en el payload (exclude_unset)
    cambios = payload.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(area, campo, valor)

    db.commit()
    db.refresh(area)
    return area


# ---------------------------------------------------------------------------
# DELETE /areas/{area_id}
# ---------------------------------------------------------------------------
@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_area(area_id: int, db: Session = Depends(get_db)):
    """Elimina un área. Fallará si tiene equipos asociados."""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail=f"Área con id={area_id} no encontrada.")
    db.delete(area)
    db.commit()