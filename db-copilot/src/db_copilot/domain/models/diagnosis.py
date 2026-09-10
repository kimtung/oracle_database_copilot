
from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    action: str
    rationale: str
    risk: str = "LOW"
    sql: str | None = None  # SQL command (display only, never auto-execute)
    priority: str = "MEDIUM"  # "HIGH", "MEDIUM", "LOW"
    note: str = "DBA must review and execute manually"


class Hypothesis(BaseModel):
    name: str
    confidence: float = 0.0
    supporting_evidence: list[str] = Field(default_factory=list)
    refuting_evidence: list[str] = Field(default_factory=list)


class DiagnosisResult(BaseModel):
    diagnosis: str
    confidence: float  # 0.0 – 1.0
    primary_cause: str
    evidence_used: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    confidence_explanation: str = ""
    alternative_causes: list[str] = Field(default_factory=list)
    hypothesis_ranking: list[Hypothesis] = Field(default_factory=list)
