"""
Simulador de dispositivo ESP32 para pruebas de integración IoT.

Simula múltiples sensores enviando lecturas de temperatura y humedad
al endpoint POST /api/v1/iot/lecturas de la API FastAPI.

Uso:
    python iot_mock/esp32_simulator.py

Configuración:
    API_BASE_URL  → URL base de la API (default: http://localhost:8000)
    INTERVALO_SEG → Segundos entre cada ciclo de envío (default: 5)
    CICLOS        → Número de ciclos a ejecutar (0 = infinito)
"""

import time
import random
import json
import urllib.request
import urllib.error
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
API_BASE_URL  = os.getenv("API_BASE_URL", "http://localhost:8000")
ENDPOINT      = f"{API_BASE_URL}/api/v1/iot/lecturas"
INTERVALO_SEG = int(os.getenv("INTERVALO_SEG", "5"))
CICLOS        = int(os.getenv("CICLOS", "0"))   # 0 = loop infinito

# ---------------------------------------------------------------------------
# Definición de sensores virtuales
# Cada sensor simula un ESP32 físico instalado en un equipo o área.
# IMPORTANTE: los IDs deben existir en tu base de datos antes de simular.
# ---------------------------------------------------------------------------
SENSORES = [
    {
        "nombre":    "Sensor-UCI-Ventilador",
        "equipo_id": 1,          # ID del equipo en la DB
        "area_id":   None,
        # Rango normal de operación para este equipo
        "temp_base": 22.0,
        "temp_var":  3.0,        # ± variación máxima
        "hum_base":  55.0,
        "hum_var":   10.0,
    },
    {
        "nombre":    "Sensor-Radiologia-Monitor",
        "equipo_id": 2,
        "area_id":   None,
        "temp_base": 20.0,
        "temp_var":  2.5,
        "hum_base":  50.0,
        "hum_var":   8.0,
    },
    {
        "nombre":    "Sensor-Area-Laboratorio",
        "equipo_id": None,
        "area_id":   1,          # ID del área en la DB
        "temp_base": 18.0,
        "temp_var":  4.0,
        "hum_base":  60.0,
        "hum_var":   12.0,
    },
]

# ---------------------------------------------------------------------------
# Colores ANSI para la consola
# ---------------------------------------------------------------------------
VERDE   = "\033[92m"
AMARILLO = "\033[93m"
ROJO    = "\033[91m"
CYAN    = "\033[96m"
RESET   = "\033[0m"
BOLD    = "\033[1m"


def generar_lectura(sensor: dict) -> dict:
    """
    Genera una lectura realista con variación aleatoria tipo ruido gaussiano.
    Con una probabilidad del 10% simula un pico de temperatura (anomalía).
    """
    # Simular anomalía térmica ocasional (10% de probabilidad)
    es_anomalia = random.random() < 0.10

    if es_anomalia:
        # Pico entre +5°C y +12°C sobre la base
        temperatura = round(sensor["temp_base"] + sensor["temp_var"] + random.uniform(5, 12), 2)
        humedad     = round(sensor["hum_base"]  + sensor["hum_var"]  + random.uniform(5, 15), 2)
    else:
        # Variación gaussiana normal
        temperatura = round(
            sensor["temp_base"] + random.gauss(0, sensor["temp_var"] / 2), 2
        )
        humedad = round(
            sensor["hum_base"] + random.gauss(0, sensor["hum_var"] / 2), 2
        )

    # Limitar humedad al rango físico válido [0, 100]
    humedad = max(0.0, min(100.0, humedad))

    payload = {
        "temperatura": temperatura,
        "humedad":     humedad,
    }

    # Solo incluir el campo que aplica (equipo_id o area_id)
    if sensor["equipo_id"] is not None:
        payload["equipo_id"] = sensor["equipo_id"]
    if sensor["area_id"] is not None:
        payload["area_id"] = sensor["area_id"]

    return payload, es_anomalia


def enviar_lectura(payload: dict) -> tuple[bool, dict | str]:
    """
    Envía la lectura a la API mediante urllib (sin dependencias externas).
    Retorna (éxito: bool, respuesta: dict | mensaje_error: str).
    """
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return False, f"HTTP {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return False, f"Conexión rechazada: {e.reason}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def imprimir_resultado(sensor: dict, payload: dict, exito: bool, respuesta, es_anomalia: bool):
    """Imprime el resultado del envío con formato visual en la consola."""
    ts  = datetime.now().strftime("%H:%M:%S")
    ico = "🌡️ "

    # Color según temperatura
    temp = payload["temperatura"]
    if temp > 30:
        color_temp = ROJO
    elif temp > 25:
        color_temp = AMARILLO
    else:
        color_temp = VERDE

    estado = f"{ROJO}✗ ERROR{RESET}" if not exito else f"{VERDE}✓ OK{RESET}"
    anomalia_tag = f" {ROJO}{BOLD}[⚠ ANOMALÍA]{RESET}" if es_anomalia else ""

    print(
        f"[{ts}] {ico} {CYAN}{sensor['nombre']:<30}{RESET} | "
        f"Temp: {color_temp}{temp:>6.2f}°C{RESET} | "
        f"Hum: {payload['humedad']:>5.1f}% | "
        f"{estado}{anomalia_tag}"
    )

    if not exito:
        print(f"         └─ {ROJO}{respuesta}{RESET}")


def ejecutar_ciclo(ciclo_num: int):
    """Ejecuta un ciclo completo: envía una lectura por cada sensor definido."""
    print(f"\n{BOLD}{'─'*70}{RESET}")
    print(f"  Ciclo #{ciclo_num:04d} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*70}{RESET}")

    for sensor in SENSORES:
        payload, es_anomalia = generar_lectura(sensor)
        exito, respuesta     = enviar_lectura(payload)
        imprimir_resultado(sensor, payload, exito, respuesta, es_anomalia)
        time.sleep(0.3)   # pequeña pausa entre sensores del mismo ciclo


def main():
    """Punto de entrada: ejecuta el simulador en bucle."""
    print(f"\n{BOLD}{'='*70}")
    print("   🏥  SIMULADOR ESP32 — Plataforma de Equipos Clínicos")
    print(f"{'='*70}{RESET}")
    print(f"  Endpoint  : {CYAN}{ENDPOINT}{RESET}")
    print(f"  Sensores  : {len(SENSORES)} dispositivos virtuales")
    print(f"  Intervalo : {INTERVALO_SEG} segundos")
    print(f"  Ciclos    : {'∞ (infinito)' if CICLOS == 0 else CICLOS}")
    print(f"  Detener   : Ctrl+C")
    print(f"{'='*70}\n")

    # Verificar conectividad con la API antes de iniciar
    print("  Verificando conexión con la API...", end=" ", flush=True)
    try:
        urllib.request.urlopen(f"{API_BASE_URL}/", timeout=5)
        print(f"{VERDE}✓ Conectado{RESET}\n")
    except Exception:
        print(f"{AMARILLO}⚠ No se pudo conectar. Intentando de todas formas...{RESET}\n")

    ciclo = 1
    try:
        while True:
            ejecutar_ciclo(ciclo)
            ciclo += 1

            if CICLOS > 0 and ciclo > CICLOS:
                print(f"\n{VERDE}✓ Simulación completada ({CICLOS} ciclos).{RESET}\n")
                break

            time.sleep(INTERVALO_SEG)

    except KeyboardInterrupt:
        print(f"\n\n{AMARILLO}⏹  Simulación detenida por el usuario.{RESET}\n")


if __name__ == "__main__":
    main()