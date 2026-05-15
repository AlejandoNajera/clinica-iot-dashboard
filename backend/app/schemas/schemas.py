"""
Esquemas Pydantic v2 para validación de entrada/salida de la API.

Convención de nomenclatura:
- <Entidad>Base    → campos comunes compartidos.
- <Entidad>Create  → payload para POST (sin id ni timestamps).
- <Entidad>Update  → payload para PATCH (todos los campos opcionales).
- <Entidad>Out     → respuesta de la API (incluye id y relaciones).
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from backend.app.models.models import EstadoEquipo, TipoMantenimiento


# ===========================================================================
# AREA
# ===========================================================================

class AreaBase(BaseModel):
    nombre: str = Field(..., max_length=120, examples=["UCI"])
    responsable: str = Field(..., max_length=150, examples=["Dr. García"])


class AreaCreate(AreaBase):
    """Payload para crear un área nueva."""
    pass


class AreaUpdate(BaseModel):
    """Payload para actualizar un área (todos los campos son opcionales)."""
    nombre: Optional[str] = Field(None, max_length=120)
    responsable: Optional[str] = Field(None, max_length=150)


class AreaOut(AreaBase):
    """Respuesta de la API al consultar un área."""
    id: int

    model_config = {"from_attributes": True}


# ===========================================================================
# EQUIPO
# ===========================================================================

class EquipoBase(BaseModel):
    codigo_patrimonial: str = Field(..., max_length=60, examples=["PAT-001"])
    nombre: str = Field(..., max_length=150, examples=["Ventilador Mecánico"])
    marca: Optional[str] = Field(None, max_length=100, examples=["Philips"])
    modelo: Optional[str] = Field(None, max_length=100, examples=["V60"])
    numero_serie: Optional[str] = Field(None, max_length=100)
    estado: EstadoEquipo = Field(default=EstadoEquipo.OPERATIVO)
    proximo_mantenimiento: Optional[date] = None
    area_id: int = Field(..., ge=1)


class EquipoCreate(EquipoBase):
    """Payload para registrar un equipo nuevo."""
    pass


class EquipoUpdate(BaseModel):
    """Payload para actualizar un equipo (todos los campos son opcionales)."""
    nombre: Optional[str] = Field(None, max_length=150)
    marca: Optional[str] = Field(None, max_length=100)
    modelo: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    estado: Optional[EstadoEquipo] = None
    proximo_mantenimiento: Optional[date] = None
    area_id: Optional[int] = Field(None, ge=1)


class EquipoOut(EquipoBase):
    """Respuesta de la API al consultar un equipo."""
    id: int
    area: AreaOut  # Incluye datos del área relacionada

    model_config = {"from_attributes": True}


# ===========================================================================
# MANTENIMIENTO
# ===========================================================================

class MantenimientoBase(BaseModel):
    tipo: TipoMantenimiento
    fecha: date = Field(default_factory=date.today)
    descripcion: Optional[str] = Field(None, max_length=500)
    tecnico: str = Field(..., max_length=150, examples=["Ing. López"])
    equipo_id: int = Field(..., ge=1)


class MantenimientoCreate(MantenimientoBase):
    """Payload para registrar un nuevo mantenimiento."""
    pass


class MantenimientoUpdate(BaseModel):
    """Payload para actualizar un mantenimiento."""
    tipo: Optional[TipoMantenimiento] = None
    fecha: Optional[date] = None
    descripcion: Optional[str] = Field(None, max_length=500)
    tecnico: Optional[str] = Field(None, max_length=150)


class MantenimientoOut(MantenimientoBase):
    """Respuesta de la API al consultar un mantenimiento."""
    id: int

    model_config = {"from_attributes": True}


# ===========================================================================
# LECTURA IoT
# ===========================================================================

class LecturaIoTBase(BaseModel):
    temperatura: float = Field(..., ge=-50.0, le=150.0, examples=[22.5])
    humedad: float = Field(..., ge=0.0, le=100.0, examples=[60.0])
    equipo_id: Optional[int] = Field(None, ge=1)
    area_id: Optional[int] = Field(None, ge=1)

    @model_validator(mode="after")
    def validar_origen(self) -> "LecturaIoTBase":
        """Garantiza que la lectura tenga al menos un origen: equipo o área."""
        if self.equipo_id is None and self.area_id is None:
            raise ValueError(
                "La lectura IoT debe tener al menos 'equipo_id' o 'area_id'."
            )
        return self


class LecturaIoTCreate(LecturaIoTBase):
    """Payload enviado por el ESP32 vía POST."""
    pass


class LecturaIoTOut(LecturaIoTBase):
    """Respuesta de la API al consultar una lectura IoT."""
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# ALERTAS (respuesta del endpoint GET /alertas)
# ===========================================================================

class AlertaEquipo(BaseModel):
    """
    Equipo con mantenimiento próximo (dentro de los siguientes 15 días).
    Usado en el endpoint GET /alertas para el dashboard.
    """
    id: int
    codigo_patrimonial: str
    nombre: str
    estado: EstadoEquipo
    proximo_mantenimiento: date
    dias_restantes: int
    area: AreaOut

    model_config = {"from_attributes": True}