import uuid

from db_copilot.evidence.normalizers.evidence_normalizer import EvidenceNormalizer
from db_copilot.evidence.repository import EvidenceRepository
from db_copilot.mcp.client import OracleMcpClient


class BaseCollector:
    """Base class for Oracle data collectors."""

    def __init__(
        self,
        mcp_client: OracleMcpClient,
        repo: EvidenceRepository,
        normalizer: EvidenceNormalizer | None = None,
        database_id: uuid.UUID | None = None,
    ):
        self.mcp = mcp_client
        self.repo = repo
        self.normalizer = normalizer or EvidenceNormalizer()
        self.database_id = database_id

    async def get_database_id(self) -> uuid.UUID:
        if self.database_id is None:
            db_obj = await self.repo.get_or_create_default_database()
            self.database_id = db_obj.id
        return self.database_id
