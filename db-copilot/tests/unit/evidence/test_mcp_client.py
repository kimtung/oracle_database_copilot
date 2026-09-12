from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import TextContent

from db_copilot.mcp.client import McpClientError, OracleMcpClient


def test_oracle_mcp_client_init():
    client = OracleMcpClient(
        command="python",
        args=["-m", "oracle_mcp.server"],
        env={"CUSTOM_VAR": "val"},
        cwd="/tmp",
    )
    params = client.get_server_params()
    assert params.command == "python"
    assert params.args == ["-m", "oracle_mcp.server"]
    assert params.cwd == "/tmp"
    assert "ORACLE_USER" in params.env
    assert params.env["CUSTOM_VAR"] == "val"


@pytest.mark.asyncio
async def test_oracle_mcp_client_call_tool_success():
    client = OracleMcpClient()

    mock_result = MagicMock()
    mock_result.isError = False
    payload = '[{"sql_id": "abc123", "elapsed_time": 5000}]'
    mock_result.content = [TextContent(type="text", text=payload)]

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.call_tool = AsyncMock(return_value=mock_result)

    @asynccontextmanager
    async def mock_stdio_client(params):
        yield (MagicMock(), MagicMock())

    @asynccontextmanager
    async def mock_client_session(read, write):
        yield mock_session

    with patch("db_copilot.mcp.client.stdio_client", side_effect=mock_stdio_client), \
         patch("db_copilot.mcp.client.ClientSession", side_effect=mock_client_session):

        result = await client.call_tool("get_top_sql", {"metric": "elapsed_time"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["sql_id"] == "abc123"
        assert result[0]["elapsed_time"] == 5000


@pytest.mark.asyncio
async def test_oracle_mcp_client_call_tool_raises_on_is_error():
    client = OracleMcpClient()

    mock_result = MagicMock()
    mock_result.isError = True
    mock_result.content = [TextContent(type="text", text="ORA-00942: table or view does not exist")]

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.call_tool = AsyncMock(return_value=mock_result)

    @asynccontextmanager
    async def mock_stdio_client(params):
        yield (MagicMock(), MagicMock())

    @asynccontextmanager
    async def mock_client_session(read, write):
        yield mock_session

    with patch("db_copilot.mcp.client.stdio_client", side_effect=mock_stdio_client), \
         patch("db_copilot.mcp.client.ClientSession", side_effect=mock_client_session):

        with pytest.raises(McpClientError) as exc_info:
            await client.call_tool("get_sql_plan", {"sql_id": "invalid"})

        assert "ORA-00942" in str(exc_info.value)
        assert exc_info.value.tool_name == "get_sql_plan"


@pytest.mark.asyncio
async def test_oracle_mcp_client_call_tool_handles_transport_failure():
    client = OracleMcpClient()

    @asynccontextmanager
    async def mock_stdio_client(params):
        raise ConnectionRefusedError("Failed to spawn process")
        yield  # unreachable

    with patch("db_copilot.mcp.client.stdio_client", side_effect=mock_stdio_client):
        with pytest.raises(McpClientError) as exc_info:
            await client.call_tool("get_database_info", {})

        assert "Failed to spawn process" in str(exc_info.value)
