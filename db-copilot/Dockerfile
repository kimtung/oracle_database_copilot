FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy build config & dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy source code and migrations
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "db_copilot.main:app", "--host", "0.0.0.0", "--port", "8000"]
