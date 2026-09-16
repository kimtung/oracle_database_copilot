"""WebSocket endpoint for real-time investigation progress streaming."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/investigate/{investigation_id}")
async def ws_investigation_progress(
    websocket: WebSocket,
    investigation_id: str,
) -> None:
    """Stream investigation progress updates in real-time.

    Sends JSON events until the investigation completes or the client disconnects.
    """
    from db_copilot.api.routes.investigate import _investigations

    await websocket.accept()
    logger.info("WebSocket connected for investigation %s", investigation_id)

    try:
        while True:
            inv = _investigations.get(investigation_id)
            if inv is None:
                await websocket.send_text(
                    json.dumps({"type": "error", "message": "Investigation not found"})
                )
                break

            status = inv.get("status", "queued")
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "progress",
                        "investigation_id": investigation_id,
                        "status": status,
                        "step_count": inv.get("step_count", 0),
                        "evidence_count": inv.get("evidence_count", 0),
                    }
                )
            )

            if status in ("completed", "partial", "failed"):
                # Send final result and close
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "result",
                            "investigation_id": investigation_id,
                            "data": inv,
                        }
                    )
                )
                break

            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for investigation %s", investigation_id)
    except Exception as exc:
        logger.error("WebSocket error for %s: %s", investigation_id, exc)
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "message": str(exc)})
            )
        except Exception:
            pass
