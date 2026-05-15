"""
Punto de entrada principal de la aplicación FastAPI.
Registra todos los routers y configura CORS para el frontend React.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import engine, Base
from backend.app.routes import areas, equipos, mantenimientos, alertas, iot

# Crea todas las tablas en la DB al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API - Gestión de Equipos Clínicos",
    description="Plataforma SaaS B2B para mantenimiento de equipos médicos con soporte IoT.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Middleware CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Registro de routers
# ---------------------------------------------------------------------------
app.include_router(areas.router,          prefix="/api/v1", tags=["Áreas"])
app.include_router(equipos.router,        prefix="/api/v1", tags=["Equipos"])
app.include_router(mantenimientos.router, prefix="/api/v1", tags=["Mantenimientos"])
app.include_router(alertas.router,        prefix="/api/v1", tags=["Alertas"])
app.include_router(iot.router,            prefix="/api/v1", tags=["IoT"])


@app.get("/", tags=["Health Check"])
def root():
    """Endpoint raíz para verificar que la API está en línea."""
    return {"status": "ok", "message": "API de Equipos Clínicos activa ✅"}