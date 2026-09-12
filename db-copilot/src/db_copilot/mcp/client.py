import json
import logging
import os
import time
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from db_copilot.config.settings import get_settings

logger = logging.getLogger(__name__)


class McpClientError(Exception):
    """Raised when an MCP tool execution fails."""

    def __init__(self, tool_name: str, message: str, duration_ms: int = 0):
        super().__init__(f"MCP tool '{tool_name}' error: {message}")
        self.tool_name = tool_name
        self.message = message
        self.duration_ms = duration_ms


class OracleMcpClient:
    """Client for invoking oracle-mcp-server tools via stdio transport."""

    def __init__(
        self,
        command: str | None = None,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ):
        settings = get_settings()
        self.command = command or settings.mcp_server_command
        self.args = args if args is not None else list(settings.mcp_server_args)
        self.cwd = cwd or settings.mcp_server_cwd

        # Build child environment with Oracle credentials
        child_env = os.environ.copy()
        if settings.oracle_user:
            child_env["ORACLE_USER"] = settings.oracle_user
        if settings.oracle_password:
            child_env["ORACLE_PASSWORD"] = settings.oracle_password
        if settings.oracle_dsn:
            child_env["ORACLE_DSN"] = settings.oracle_dsn
        if env:
            child_env.update(env)
        self.env = child_env

    def get_server_params(self) -> StdioServerParameters:
        return StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env,
            cwd=self.cwd,
        )

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call a remote tool on the MCP server and return parsed response."""
        arguments = arguments or {}
        server_params = self.get_server_params()
        start_time = time.monotonic()

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)

            duration_ms = int((time.monotonic() - start_time) * 1000)

            # Check if MCP result signaled an error
            if getattr(result, "isError", False):
                err_msg = self._extract_text(result.content)
                logger.error(f"MCP tool {tool_name} returned error: {err_msg}")
                raise McpClientError(tool_name, err_msg, duration_ms=duration_ms)

            # Extract content text
            content_text = self._extract_text(result.content)
            logger.debug(f"MCP tool {tool_name} executed in {duration_ms}ms")

            if not content_text:
                return None

            try:
                return json.loads(content_text)
            except json.JSONDecodeError:
                return content_text

        except McpClientError:
            raise
        except Exception as e:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.error(f"MCP tool {tool_name} failed after {duration_ms}ms: {e}")
            raise McpClientError(tool_name, str(e), duration_ms=duration_ms) from e

    def _extract_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if hasattr(item, "text"):
                    texts.append(item.text)
                elif isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
                else:
                    texts.append(str(item))
            return "\n".join(texts)
        if hasattr(content, "text"):
            return content.text
        return str(content)
