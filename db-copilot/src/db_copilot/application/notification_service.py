"""NotificationService — sends alerts to Slack/Teams webhooks.

Only fires when a webhook URL is configured in settings.
All notification failures are logged but never propagate as exceptions.
"""

from __future__ import annotations

import json
import logging

import aiohttp

from db_copilot.config.settings import get_settings
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class NotificationService:
    """Send Slack/Teams webhook notifications for critical incidents and daily reports.

    Silently skips notification if no webhook URL is configured.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def notify_critical_incident(self, incident: Incident) -> None:
        """Send immediate alert when a CRITICAL incident is detected."""
        if incident.severity.value != "CRITICAL":
            return
        message = {
            "text": (
                f":rotating_light: *CRITICAL Oracle Incident Detected*\n"
                f"*{incident.title}*\n"
                f"Category: `{incident.category.value}`\n"
                f"Time: {incident.detected_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"_No automatic action was taken. DBA review required._"
            )
        }
        await self._send(message)

    async def notify_daily_report(
        self, health_score: int, critical: int, high: int, report_date: str
    ) -> None:
        """Send daily health summary to webhook."""
        if health_score >= 80:
            emoji = ":white_check_mark:"
        elif health_score >= 60:
            emoji = ":warning:"
        else:
            emoji = ":rotating_light:"
        message = {
            "text": (
                f"{emoji} *Daily Oracle DB Health Report — {report_date}*\n"
                f"Health Score: *{health_score}/100*\n"
                f"Critical: {critical} | High: {high}\n"
                f"_No automatic database changes were executed._"
            )
        }
        await self._send(message)

    async def _send(self, payload: dict) -> None:
        for url_attr in ("slack_webhook_url", "teams_webhook_url"):
            url = getattr(self._settings, url_attr, "")
            if not url:
                continue
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        data=json.dumps(payload),
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status not in (200, 204):
                            logger.warning(
                                "Webhook %s responded %d", url_attr, resp.status
                            )
            except Exception as exc:
                logger.warning("Failed to send webhook notification: %s", exc)
