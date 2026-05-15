"""
Endpoint de Alertas de mantenimiento próximo.

Rutas:
  GET /api/v1/alertas  → Equipos con mantenimiento en los próximos N días (default 15)

Lógica:
  Consulta todos los equipos cuyo campo `proximo_mantenimiento`
  esté entre HOY y HOY + días_limite, ordenados por urgencia (más próximo primero).
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from backend.app.database import get_db
from backend.app.models.models import Equipo
from backend.app.schemas.schemas import AlertaEquipo

router = APIRouter()


@router.get("/alertas", response_model=list[AlertaEquipo])
def obtener_alertas(
    dias: int = Query(
        default=15,
        ge=1,
        le=90,
        description="Ventana de días hacia adelante para buscar mantenimientos próximos."
    ),
    db: Session = Depends(get_db)
):
    """
    Retorna los equipos que tienen mantenimiento programado dentro
    de los próximos `dias` días (por defecto 15).

    Cada elemento incluye `dias_restantes` para facilitar
    la priorización visual en el dashboard.
    """
    hoy = date.today()
    limite = hoy + timedelta(days=dias)

    equipos_proximos = (
        db.query(Equipo)
        .options(joinedload(Equipo.area))
        .filter(
            Equipo.proximo_mantenimiento >= hoy,
            Equipo.proximo_mantenimiento <= limite
        )
        .order_by(Equipo.proximo_mantenimiento.asc())  # más urgente primero
        .all()
    )

    # Construir la respuesta calculando dias_restantes para cada equipo
    resultado = []
    for equipo in equipos_proximos:
        dias_restantes = (equipo.proximo_mantenimiento - hoy).days
        resultado.append(
            AlertaEquipo(
                id=equipo.id,
                codigo_patrimonial=equipo.codigo_patrimonial,
                nombre=equipo.nombre,
                estado=equipo.estado,
                proximo_mantenimiento=equipo.proximo_mantenimiento,
                dias_restantes=dias_restantes,
                area=equipo.area,
            )
        )

    return resultado