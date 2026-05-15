"""
Endpoints IoT para recepción de lecturas de sensores ESP32.

Rutas:
  POST /api/v1/iot/lecturas         → Recibir lectura de sensor
  GET  /api/v1/iot/lecturas         → Listar lecturas (con filtros opcionales)
  GET  /api/v1/iot/lecturas/ultimas → Última lectura por equipo/área
  GET  /api/v1/iot/stats            → Estadísticas resumidas de lecturas recientes
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.models import LecturaIoT, Equipo, Area
from backend.app.schemas.schemas import LecturaIoTCreate, LecturaIoTOut

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /iot/lecturas  ← Endpoint principal que consume el ESP32
# ---------------------------------------------------------------------------
@router.post(
    "/iot/lecturas",
    response_model=LecturaIoTOut,
    status_code=status.HTTP_201_CREATED
)
def recibir_lectura(payload: LecturaIoTCreate, db: Session = Depends(get_db)):
    """
    Recibe una lectura de temperatura y humedad enviada por un sensor ESP32.
    Valida que el equipo o área referenciada exista en la base de datos.
    Genera una alerta en el log si los valores superan umbrales críticos.
    """
    # Validar que el equipo referenciado existe (si se envía equipo_id)
    if payload.equipo_id:
        equipo = db.query(Equipo).filter(Equipo.id == payload.equipo_id).first()
        if not equipo:
            raise HTTPException(
                status_code=404,
                detail=f"Equipo con id={payload.equipo_id} no encontrado."
            )

    # Validar que el área referenciada existe (si se envía area_id)
    if payload.area_id:
        area = db.query(Area).filter(Area.id == payload.area_id).first()
        if not area:
            raise HTTPException(
                status_code=404,
                detail=f"Área con id={payload.area_id} no encontrada."
            )

    # Persistir la lectura con timestamp UTC actual
    nueva_lectura = LecturaIoT(
        **payload.model_dump(),
        timestamp=datetime.utcnow()
    )
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)

    # Log de alerta si supera umbrales críticos (25°C / 70% humedad)
    _evaluar_umbrales(nueva_lectura)

    return nueva_lectura


# ---------------------------------------------------------------------------
# GET /iot/lecturas
# ---------------------------------------------------------------------------
@router.get("/iot/lecturas", response_model=list[LecturaIoTOut])
def listar_lecturas(
    equipo_id: Optional[int] = Query(None, description="Filtrar por equipo"),
    area_id: Optional[int]   = Query(None, description="Filtrar por área"),
    horas: int               = Query(24, ge=1, le=720, description="Últimas N horas"),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    """
    Retorna lecturas IoT dentro de una ventana de tiempo.
    Por defecto devuelve las últimas 24 horas.
    """
    desde = datetime.utcnow() - timedelta(hours=horas)

    query = (
        db.query(LecturaIoT)
        .filter(LecturaIoT.timestamp >= desde)
        .order_by(LecturaIoT.timestamp.desc())
    )

    if equipo_id is not None:
        query = query.filter(LecturaIoT.equipo_id == equipo_id)
    if area_id is not None:
        query = query.filter(LecturaIoT.area_id == area_id)

    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# GET /iot/lecturas/ultimas
# ---------------------------------------------------------------------------
@router.get("/iot/lecturas/ultimas", response_model=list[LecturaIoTOut])
def ultimas_lecturas_por_equipo(db: Session = Depends(get_db)):
    """
    Retorna la lectura más reciente de cada equipo.
    Útil para el dashboard de estado en tiempo real.
    """
    # Subconsulta: max timestamp por equipo_id
    subq = (
        db.query(
            LecturaIoT.equipo_id,
            func.max(LecturaIoT.timestamp).label("max_ts")
        )
        .filter(LecturaIoT.equipo_id.isnot(None))
        .group_by(LecturaIoT.equipo_id)
        .subquery()
    )

    lecturas = (
        db.query(LecturaIoT)
        .join(
            subq,
            (LecturaIoT.equipo_id == subq.c.equipo_id) &
            (LecturaIoT.timestamp == subq.c.max_ts)
        )
        .all()
    )
    return lecturas


# ---------------------------------------------------------------------------
# GET /iot/stats
# ---------------------------------------------------------------------------
@router.get("/iot/stats")
def estadisticas_iot(
    horas: int = Query(24, ge=1, le=720, description="Ventana de tiempo en horas"),
    db: Session = Depends(get_db)
):
    """
    Retorna estadísticas agregadas de temperatura y humedad
    para las últimas N horas. Incluye promedio, mínimo y máximo.
    """
    desde = datetime.utcnow() - timedelta(hours=horas)

    stats = db.query(
        func.count(LecturaIoT.id).label("total_lecturas"),
        func.avg(LecturaIoT.temperatura).label("temp_promedio"),
        func.min(LecturaIoT.temperatura).label("temp_minima"),
        func.max(LecturaIoT.temperatura).label("temp_maxima"),
        func.avg(LecturaIoT.humedad).label("hum_promedio"),
        func.min(LecturaIoT.humedad).label("hum_minima"),
        func.max(LecturaIoT.humedad).label("hum_maxima"),
    ).filter(LecturaIoT.timestamp >= desde).first()

    return {
        "ventana_horas": horas,
        "total_lecturas": stats.total_lecturas or 0,
        "temperatura": {
            "promedio": round(stats.temp_promedio or 0, 2),
            "minima":   round(stats.temp_minima   or 0, 2),
            "maxima":   round(stats.temp_maxima   or 0, 2),
        },
        "humedad": {
            "promedio": round(stats.hum_promedio or 0, 2),
            "minima":   round(stats.hum_minima   or 0, 2),
            "maxima":   round(stats.hum_maxima   or 0, 2),
        },
    }


# ---------------------------------------------------------------------------
# Función auxiliar: evaluación de umbrales críticos
# ---------------------------------------------------------------------------
def _evaluar_umbrales(lectura: LecturaIoT):
    """
    Compara la lectura contra umbrales críticos y emite advertencias en el log.
    En producción esto se conectaría a un sistema de notificaciones (email/SMS).

    Umbrales estándar para sala de equipos médicos:
      - Temperatura > 25°C → advertencia | > 30°C → crítico
      - Humedad      > 70% → advertencia | > 80%  → crítico
    """
    origen = f"equipo_id={lectura.equipo_id}" if lectura.equipo_id else f"area_id={lectura.area_id}"

    if lectura.temperatura > 30:
        print(f"[🔴 CRÍTICO] Temperatura {lectura.temperatura}°C supera 30°C — {origen}")
    elif lectura.temperatura > 25:
        print(f"[🟡 AVISO]   Temperatura {lectura.temperatura}°C supera 25°C — {origen}")

    if lectura.humedad > 80:
        print(f"[🔴 CRÍTICO] Humedad {lectura.humedad}% supera 80% — {origen}")
    elif lectura.humedad > 70:
        print(f"[🟡 AVISO]   Humedad {lectura.humedad}% supera 70% — {origen}")