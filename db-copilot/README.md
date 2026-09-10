# DB Copilot

AI-powered Oracle Database Performance Copilot — automated incident detection, correlation, and diagnosis.

## Features
- **FastAPI API** with async lifespan and structured health check endpoint
- **PostgreSQL Database** with SQLAlchemy 2.0 (asyncio) and Alembic migrations
- **Domain Models**: Evidence, Incident, DiagnosisResult, Hypothesis, Recommendation
- **Modular Architecture**: Config, Domain, DB, API, and upcoming Engine modules

## Quick Start

### 1. Requirements
- Python 3.12+
- PostgreSQL 15+ (or Docker)

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Run with Docker Compose
```bash
docker compose up --build
```

### 4. Run Locally
```bash
pip install -e ".[dev]"
# or with uv: uv pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start API server
uvicorn db_copilot.main:app --reload --port 8000
```

### 5. Health Check
```bash
curl http://localhost:8000/api/v1/health
```
Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "0.1.0",
  "timestamp": "2026-09-10T14:30:00Z"
}
```
