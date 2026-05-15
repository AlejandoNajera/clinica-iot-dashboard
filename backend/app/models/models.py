"""
Modelos ORM de SQLAlchemy para la plataforma de gestión de equipos clínicos.

Tablas:
- Area           → Áreas o servicios del centro de salud.
- Equipo         → Equipos clínicos inventariados.
- Mantenimiento  → Historial de mantenimientos por equipo.
- LecturaIoT     → Lecturas de temperatura/humedad enviadas por sensores ESP32.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Date, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from backend.app.database import Base


# ---------------------------------------------------------------------------
# Enum de estados posibles de un equipo clínico
# ---------------------------------------------------------------------------
class EstadoEquipo(str, enum.Enum):
    OPERATIVO = "operativo"
    EN_MANTENIMIENTO = "en_mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"
    EN_REVISION = "en_revision"


# ---------------------------------------------------------------------------
# Enum de tipos de mantenimiento
# ---------------------------------------------------------------------------
class TipoMantenimiento(str, enum.Enum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    PREDICTIVO = "predictivo"
    CALIBRACION = "calibracion"


# ---------------------------------------------------------------------------
# MODELO: Area
# ---------------------------------------------------------------------------
class Area(Base):
    """
    Representa un área o servicio dentro del centro de salud
    (ej: UCI, Radiología, Laboratorio).
    """
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False, unique=True)
    responsable = Column(String(150), nullable=False)

    # Relaciones inversas
    equipos = relationship("Equipo", back_populates="area")
    lecturas_iot = relationship("LecturaIoT", back_populates="area")

    def __repr__(self):
        return f"<Area id={self.id} nombre='{self.nombre}'>"


# ---------------------------------------------------------------------------
# MODELO: Equipo
# ---------------------------------------------------------------------------
class Equipo(Base):
    """
    Equipo clínico registrado en el inventario.
    Cada equipo pertenece a un Área y puede tener múltiples mantenimientos.
    """
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_patrimonial = Column(String(60), nullable=False, unique=True, index=True)
    nombre = Column(String(150), nullable=False)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    numero_serie = Column(String(100), nullable=True, unique=True)
    estado = Column(
        SAEnum(EstadoEquipo, name="estado_equipo"),
        nullable=False,
        default=EstadoEquipo.OPERATIVO
    )
    proximo_mantenimiento = Column(Date, nullable=True)

    # FK hacia Area
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)

    # Relaciones
    area = relationship("Area", back_populates="equipos")
    mantenimientos = relationship(
        "Mantenimiento", back_populates="equipo", cascade="all, delete-orphan"
    )
    lecturas_iot = relationship(
        "LecturaIoT", back_populates="equipo", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Equipo id={self.id} codigo='{self.codigo_patrimonial}'>"


# ---------------------------------------------------------------------------
# MODELO: Mantenimiento
# ---------------------------------------------------------------------------
class Mantenimiento(Base):
    """
    Registro de un evento de mantenimiento aplicado a un equipo clínico.
    """
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(
        SAEnum(TipoMantenimiento, name="tipo_mantenimiento"),
        nullable=False
    )
    fecha = Column(Date, nullable=False, default=date.today)
    descripcion = Column(String(500), nullable=True)
    tecnico = Column(String(150), nullable=False)

    # FK hacia Equipo
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)

    # Relación
    equipo = relationship("Equipo", back_populates="mantenimientos")

    def __repr__(self):
        return (
            f"<Mantenimiento id={self.id} equipo_id={self.equipo_id} "
            f"tipo='{self.tipo}' fecha={self.fecha}>"
        )


# ---------------------------------------------------------------------------
# MODELO: LecturaIoT
# ---------------------------------------------------------------------------
class LecturaIoT(Base):
    """
    Lectura enviada por un sensor ESP32.
    Puede asociarse a un equipo específico O a un área completa,
    dependiendo de dónde esté instalado el sensor.
    """
    __tablename__ = "lecturas_iot"

    id = Column(Integer, primary_key=True, index=True)
    temperatura = Column(Float, nullable=False)   # Celsius
    humedad = Column(Float, nullable=False)        # Porcentaje (%)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # FKs opcionales — al menos uno debe estar presente (se valida en Pydantic)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)

    # Relaciones
    equipo = relationship("Equipo", back_populates="lecturas_iot")
    area = relationship("Area", back_populates="lecturas_iot")

    def __repr__(self):
        return (
            f"<LecturaIoT id={self.id} temp={self.temperatura}°C "
            f"hum={self.humedad}% ts={self.timestamp}>"
        )