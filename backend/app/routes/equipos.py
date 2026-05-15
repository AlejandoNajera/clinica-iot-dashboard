"""
Endpoints CRUD para el recurso Equipo.

Rutas:
  POST   /api/v1/equipos              → Crear equipo
  GET    /api/v1/equipos              → Listar equipos (con filtros opcionales)
  GET    /api/v1/equipos/{id}         → Obtener equipo por ID
  PUT    /api/v1/equipos/{id}         → Actualizar equipo
  DELETE /api/v1/equipos/{id}         → Eliminar equipo
  GET    /api/v1/equipos/{id}/mantenimientos → Historial de mantenimientos
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from backend.app.database import get_db
from backend.app.models.models import Equipo, Area, EstadoEquipo
from backend.app.schemas.schemas import (
    EquipoCreate, EquipoUpdate, EquipoOut, MantenimientoOut
)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /equipos
# ---------------------------------------------------------------------------
@router.post("/equipos", response_model=EquipoOut, status_code=status.HTTP_201_CREATED)
def crear_equipo(payload: EquipoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo equipo clínico en el inventario."""
    # Verificar que el área existe
    area = db.query(Area).filter(Area.id == payload.area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail=f"Área con id={payload.area_id} no encontrada.")

    # Verificar código patrimonial único
    if db.query(Equipo).filter(Equipo.codigo_patrimonial == payload.codigo_patrimonial).first():
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un equipo con código '{payload.codigo_patrimonial}'."
        )

    nuevo_equipo = Equipo(**payload.model_dump())
    db.add(nuevo_equipo)
    db.commit()
    db.refresh(nuevo_equipo)

    # Recargar con relación 'area' para la respuesta anidada
    return db.query(Equipo).options(joinedload(Equipo.area)).filter(Equipo.id == nuevo_equipo.id).first()


# ---------------------------------------------------------------------------
# GET /equipos
# ---------------------------------------------------------------------------
@router.get("/equipos", response_model=list[EquipoOut])
def listar_equipos(
    skip: int = 0,
    limit: int = 100,
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    estado: Optional[EstadoEquipo] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Retorna la lista de equipos.
    Admite filtros opcionales por área y/o estado.
    """
    query = db.query(Equipo).options(joinedload(Equipo.area))

    if area_id is not None:
        query = query.filter(Equipo.area_id == area_id)
    if estado is not None:
        query = query.filter(Equipo.estado == estado)

    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# GET /equipos/{equipo_id}
# ---------------------------------------------------------------------------
@router.get("/equipos/{equipo_id}", response_model=EquipoOut)
def obtener_equipo(equipo_id: int, db: Session = Depends(get_db)):
    """Retorna un equipo específico por su ID, incluyendo datos del área."""
    equipo = (
        db.query(Equipo)
        .options(joinedload(Equipo.area))
        .filter(Equipo.id == equipo_id)
        .first()
    )
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo con id={equipo_id} no encontrado.")
    return equipo


# ---------------------------------------------------------------------------
# PUT /equipos/{equipo_id}
# ---------------------------------------------------------------------------
@router.put("/equipos/{equipo_id}", response_model=EquipoOut)
def actualizar_equipo(equipo_id: int, payload: EquipoUpdate, db: Session = Depends(get_db)):
    """Actualiza los campos enviados de un equipo existente."""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo con id={equipo_id} no encontrado.")

    # Validar área si se está cambiando
    cambios = payload.model_dump(exclude_unset=True)
    if "area_id" in cambios:
        area = db.query(Area).filter(Area.id == cambios["area_id"]).first()
        if not area:
            raise HTTPException(status_code=404, detail=f"Área con id={cambios['area_id']} no encontrada.")

    for campo, valor in cambios.items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return db.query(Equipo).options(joinedload(Equipo.area)).filter(Equipo.id == equipo_id).first()


# ---------------------------------------------------------------------------
# DELETE /equipos/{equipo_id}
# ---------------------------------------------------------------------------
@router.delete("/equipos/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    """Elimina un equipo y su historial de mantenimientos (cascade)."""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo con id={equipo_id} no encontrado.")
    db.delete(equipo)
    db.commit()


# ---------------------------------------------------------------------------
# GET /equipos/{equipo_id}/mantenimientos
# ---------------------------------------------------------------------------
@router.get("/equipos/{equipo_id}/mantenimientos", response_model=list[MantenimientoOut])
def historial_mantenimientos(equipo_id: int, db: Session = Depends(get_db)):
    """Retorna el historial completo de mantenimientos de un equipo."""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo con id={equipo_id} no encontrado.")
    return equipo.mantenimientos