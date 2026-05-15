"""
Endpoints CRUD para el recurso Mantenimiento.

Rutas:
  POST   /api/v1/mantenimientos        → Registrar mantenimiento
  GET    /api/v1/mantenimientos        → Listar todos los mantenimientos
  GET    /api/v1/mantenimientos/{id}   → Obtener mantenimiento por ID
  PUT    /api/v1/mantenimientos/{id}   → Actualizar mantenimiento
  DELETE /api/v1/mantenimientos/{id}   → Eliminar mantenimiento
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from backend.app.database import get_db
from backend.app.models.models import Mantenimiento, Equipo, EstadoEquipo
from backend.app.schemas.schemas import (
    MantenimientoCreate, MantenimientoUpdate, MantenimientoOut
)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /mantenimientos
# ---------------------------------------------------------------------------
@router.post(
    "/mantenimientos",
    response_model=MantenimientoOut,
    status_code=status.HTTP_201_CREATED
)
def crear_mantenimiento(payload: MantenimientoCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo evento de mantenimiento para un equipo.
    Actualiza automáticamente el estado del equipo a EN_MANTENIMIENTO.
    """
    equipo = db.query(Equipo).filter(Equipo.id == payload.equipo_id).first()
    if not equipo:
        raise HTTPException(
            status_code=404,
            detail=f"Equipo con id={payload.equipo_id} no encontrado."
        )

    nuevo = Mantenimiento(**payload.model_dump())
    db.add(nuevo)

    # Marcar el equipo como "en mantenimiento" si el evento es de hoy
    if payload.fecha == date.today():
        equipo.estado = EstadoEquipo.EN_MANTENIMIENTO

    db.commit()
    db.refresh(nuevo)
    return nuevo


# ---------------------------------------------------------------------------
# GET /mantenimientos
# ---------------------------------------------------------------------------
@router.get("/mantenimientos", response_model=list[MantenimientoOut])
def listar_mantenimientos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retorna todos los mantenimientos registrados, ordenados por fecha descendente."""
    return (
        db.query(Mantenimiento)
        .order_by(Mantenimiento.fecha.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# GET /mantenimientos/{mantenimiento_id}
# ---------------------------------------------------------------------------
@router.get("/mantenimientos/{mantenimiento_id}", response_model=MantenimientoOut)
def obtener_mantenimiento(mantenimiento_id: int, db: Session = Depends(get_db)):
    """Retorna un mantenimiento específico por su ID."""
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not m:
        raise HTTPException(
            status_code=404,
            detail=f"Mantenimiento con id={mantenimiento_id} no encontrado."
        )
    return m


# ---------------------------------------------------------------------------
# PUT /mantenimientos/{mantenimiento_id}
# ---------------------------------------------------------------------------
@router.put("/mantenimientos/{mantenimiento_id}", response_model=MantenimientoOut)
def actualizar_mantenimiento(
    mantenimiento_id: int,
    payload: MantenimientoUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza los campos enviados de un mantenimiento existente."""
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not m:
        raise HTTPException(status_code=404, detail=f"Mantenimiento con id={mantenimiento_id} no encontrado.")

    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(m, campo, valor)

    db.commit()
    db.refresh(m)
    return m


# ---------------------------------------------------------------------------
# DELETE /mantenimientos/{mantenimiento_id}
# ---------------------------------------------------------------------------
@router.delete("/mantenimientos/{mantenimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mantenimiento(mantenimiento_id: int, db: Session = Depends(get_db)):
    """Elimina un registro de mantenimiento."""
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not m:
        raise HTTPException(status_code=404, detail=f"Mantenimiento con id={mantenimiento_id} no encontrado.")
    db.delete(m)
    db.commit()