<img width="1919" height="858" alt="image" src="https://github.com/user-attachments/assets/f29ddb2f-41ac-41e6-9c7e-ed5ae159b3eb" />

 # 🏥 Clinica IoT Dashboard - Plataforma de Gestión Clínica

Plataforma B2B full-stack diseñada para optimizar la gestión de mantenimiento y el monitoreo ambiental en tiempo real de equipos médicos críticos, orientada a departamentos de Ingeniería Clínica.

## 🚀 Arquitectura del Proyecto (Dockerizada)

Este Producto Mínimo Viable (MVP) está construido bajo una arquitectura de microservicios, separando las capas lógicas para asegurar escalabilidad y alta disponibilidad en entornos hospitalarios.

* **Frontend (React + Vite + Tailwind CSS):** Interfaz de usuario reactiva y utilitaria servida mediante **Nginx**. Permite el registro de equipos, visualización de métricas y monitoreo IoT en tiempo real.
* **Backend (Python + FastAPI):** API RESTful asíncrona de alto rendimiento. Gestiona la lógica de negocio, validaciones estrictas (Pydantic) y la ingesta de telemetría de alta frecuencia.
* **Base de Datos (PostgreSQL):** Base de datos relacional robusta para garantizar la integridad del inventario patrimonial y el historial de lecturas ambientales.
* **Simulador IoT (Python):** Script integrado que emula el comportamiento de microcontroladores ESP32, enviando paquetes JSON de temperatura y humedad, incluyendo simulaciones de picos térmicos para testear alertas.

## ⚙️ Requisitos Previos

* [Docker](https://www.docker.com/) y Docker Compose instalados.

## 🛠️ Instalación y Despliegue Local

La plataforma está completamente contenedorizada, lo que permite levantar todo el ecosistema con un solo comando.

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/AlejandoNajera/clinica-iot-dashboard.git](https://github.com/AlejandoNajera/clinica-iot-dashboard.git)
   cd clinica-iot-dashboard

   ## 📊 Vista Previa del Dashboard

A continuación se muestra una captura de la interfaz de usuario en funcionamiento, desplegando las métricas críticas del inventario y la telemetría asíncrona de los sensores IoT:
<img width="1919" height="866" alt="image" src="https://github.com/user-attachments/assets/08f684d4-b0ce-4bc8-9674-97bda072557d" />
