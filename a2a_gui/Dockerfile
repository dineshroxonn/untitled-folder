# Multi-stage build
FROM node:18 AS frontend-builder

WORKDIR /app

# Copy frontend files
COPY frontend/ ./frontend/

# Install frontend dependencies and build
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next

# Install uv
RUN pip install uv

# Install project dependencies
RUN uv sync

# Expose port
EXPOSE 8000

# Environment variable for car agent URL
ENV CAR_AGENT_URL=http://localhost:10011
ENV PORT=8000

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]