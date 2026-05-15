"""
Módulo de configuración de la conexión a la base de datos (SQLite para desarrollo local).
Utiliza SQLAlchemy como ORM y expone la sesión de DB como dependencia de FastAPI.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# 1. Cambiamos la URL por defecto para que cree un archivo local llamado clinica_mvp.db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./clinica_mvp.db"
)

# 2. Configuración del motor de base de datos
# SQLite requiere el argumento 'check_same_thread': False para permitir que múltiples peticiones asíncronas de FastAPI accedan a él.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Fábrica de sesiones: autocommit y autoflush desactivados para control manual
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base de la que heredarán todos los modelos ORM."""
    pass


def get_db():
    """
    Dependencia de FastAPI que provee una sesión de DB por request.
    Garantiza el cierre de la sesión al finalizar, incluso ante errores.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()