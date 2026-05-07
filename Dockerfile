# ==========================================
# Stage 1: Build React Frontend
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies and build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Output to /app/frontend/build
RUN REACT_APP_API_URL=/api npm run build

# ==========================================
# Stage 2: Build Flask API / Backend
# ==========================================
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt gunicorn

# Copy backend python code
COPY api.py .
COPY simulator.py .
COPY src/ ./src/
COPY .env .
COPY service_account.json .

# Copy React build from Stage 1 into the Flask API static folder
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Ensure standard Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Run Flask using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "api:app"]
