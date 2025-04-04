# Etapa 1: build do frontend (React com Vite)
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/ ./
RUN npm install
RUN npm run build

# Etapa 2: backend com Python + FastAPI
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y curl build-essential

# Diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código backend e banco de dados
COPY src/ ./src
COPY auth.db ./

# Copiar o frontend já buildado
COPY --from=frontend-builder /app/frontend/dist ./frontend-dist

# Copiar variáveis de ambiente
COPY .env .env

# Expor porta do Uvicorn
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
