# Imagen mínima para el simulador ESP32
# Solo necesita Python estándar (sin dependencias extra)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar únicamente el simulador
COPY esp32_simulator.py .

# El simulador espera que la API esté lista antes de arrancar
# (controlado por healthcheck en docker-compose)
CMD ["python", "esp32_simulator.py"]