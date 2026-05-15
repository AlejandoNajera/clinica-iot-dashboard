# ─────────────────────────────────────────────
# Imagen base: Python 3.11 slim (liviana)
# ─────────────────────────────────────────────
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y
# que el buffer de stdout/stderr retrase los logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python primero
# (aprovecha la caché de capas de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Puerto expuesto por Uvicorn
EXPOSE 8000

# Comando de inicio con recarga desactivada en producción
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]