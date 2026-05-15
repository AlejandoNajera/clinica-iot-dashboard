# ─────────────────────────────────────────────
# ETAPA 1: Build de la app React con Vite
# ─────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar manifiestos e instalar dependencias
COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install

# Copiar fuente y construir
COPY . .

# Variable de entorno para que Vite apunte a la API
# En Docker el proxy de Vite no aplica; Nginx hace el proxy
ENV VITE_API_BASE_URL=""

RUN npm run build

# ─────────────────────────────────────────────
# ETAPA 2: Servidor estático con Nginx Alpine
# ─────────────────────────────────────────────
FROM nginx:1.25-alpine

# Eliminar configuración default de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nuestra configuración personalizada
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copiar el build de Vite al directorio de Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]