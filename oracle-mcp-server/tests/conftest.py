"""
conftest.py — set fake Oracle env vars before any test imports oracle_mcp.
This prevents pydantic_settings from raising ValidationError during unit tests.
"""

import os

# Must be set BEFORE oracle_mcp modules are imported
os.environ.setdefault("ORACLE_USER", "test_user")
os.environ.setdefault("ORACLE_PASSWORD", "test_password")
os.environ.setdefault("ORACLE_DSN", "localhost:1521/TESTDB")
