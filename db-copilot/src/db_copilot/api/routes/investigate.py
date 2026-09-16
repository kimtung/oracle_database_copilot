"""API routes for investigation endpoints.

POST /api/v1/investigate       — submit a DBA question, returns investigation_id
GET  /api/v1/investigate/{id}  — poll investigation status/result
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/investigate", tags=["investigate"])

# In-memory store for investigation results (replace with DB in production)
_investigations: dict[str, dict[str, Any]] = {}


class InvestigationRequest(BaseModel):
    question: str
    database_name: str = "Oracle DB"


class InvestigationStatusResponse(BaseModel):
    id: str
    status: str  # "queued" | "running" | "completed" | "partial" | "failed"
    question: str
    started_at: str
    completed_at: str | None = None
    duration_seconds: float | None = None
    step_count: int = 0
    evidence_count: int = 0
    diagnosis_summary: str | None = None
    confidence: float | None = None
    warnings: list[str] = []
    errors: list[str] = []


async def _run_investigation(inv_id: str, question: str, database_name: str) -> None:
    """Background task: run investigation and store result."""
    from db_copilot.ai.service import AIService
    from db_copilot.config.settings import get_settings
    from db_copilot.investigation.engine import InvestigationEngine
    from db_copilot.mcp.client import OracleMcpClient

    _investigations[inv_id]["status"] = "running"
    try:
        settings = get_settings()
        mcp_client = OracleMcpClient(settings)
        ai_service = AIService(settings)
        engine = InvestigationEngine(mcp_client, ai_service, settings)

        result = await engine.investigate(question, database_name=database_name)

        _investigations[inv_id].update(
            {
                "status": result.status,
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "duration_seconds": result.duration_seconds,
                "step_count": result.step_count,
                "evidence_count": len(result.evidence),
                "diagnosis": result.diagnosis.model_dump() if result.diagnosis else None,
                "warnings": result.warnings,
                "errors": result.errors,
            }
        )
    except Exception as exc:
        logger.error("Investigation %s failed: %s", inv_id, exc, exc_info=True)
        _investigations[inv_id].update(
            {
                "status": "failed",
                "errors": [str(exc)],
                "completed_at": datetime.now(UTC).isoformat(),
            }
        )


@router.post("", status_code=202)
async def submit_investigation(
    req: InvestigationRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Submit a new DBA investigation question. Returns immediately with investigation_id."""
    inv_id = str(uuid.uuid4())
    _investigations[inv_id] = {
        "id": inv_id,
        "status": "queued",
        "question": req.question,
        "database_name": req.database_name,
        "started_at": datetime.now(UTC).isoformat(),
        "completed_at": None,
        "duration_seconds": None,
        "step_count": 0,
        "evidence_count": 0,
        "diagnosis": None,
        "warnings": [],
        "errors": [],
    }
    background_tasks.add_task(_run_investigation, inv_id, req.question, req.database_name)
    return {"id": inv_id, "status": "queued", "message": "Investigation started"}


@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str) -> dict:
    """Poll investigation status or retrieve completed result."""
    inv = _investigations.get(investigation_id)
    if inv is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv
