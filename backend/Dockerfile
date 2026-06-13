# ── Stage 1: build Next.js ────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# URL vazia = chamadas relativas ao mesmo servidor
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

# ── Stage 2: Python runtime + frontend estático ───────────────────────────────
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-builder /frontend/out ./out

RUN mkdir -p data/sessions

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
