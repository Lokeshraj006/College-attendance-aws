# ── Stage 1: build the React app ─────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --silent

# VITE_API_BASE_URL is injected at build time via --build-arg / ARG
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY . .
RUN npm run build          # outputs to /app/dist

# ── Stage 2: serve with nginx on port 80 ────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled React assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config: serve React SPA + reverse-proxy /api → backend:8000
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

