FROM python:3.12-slim

LABEL maintainer="DB Copilot Team"
LABEL description="Oracle MCP Server — read-only Oracle observability gateway"

WORKDIR /app

# Install build tools (needed by some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Copy source
COPY src/ src/

# python-oracledb thin mode — no Oracle Instant Client needed
# No extra system libs required.

# MCP server communicates via stdio by default
# Oracle credentials MUST be provided via environment variables:
#   ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

CMD ["python", "-m", "oracle_mcp.server"]
