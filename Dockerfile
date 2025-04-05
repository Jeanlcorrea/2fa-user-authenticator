# Adiciona antes de tudo
ARG VITE_API_URL

# Etapa 1: build do frontend (React com Vite)
FROM node:18 AS frontend-builder
WORKDIR /app/frontend

COPY frontend/ ./

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN echo "VITE_API_URL=$VITE_API_URL" > .env

RUN npm install
RUN npm run build

# Etapa 2: backend com Python + FastAPI
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY auth.db ./

COPY --from=frontend-builder /app/frontend/dist ./frontend-dist

COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
