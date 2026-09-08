# AI Engine Design
# Thiết Kế AI Engine

**Project:** `db-copilot` — `ai/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

AI Engine là layer duy nhất trong `db-copilot` giao tiếp với LLM. Nó nhận **structured evidence** từ Investigation Engine và trả về **structured diagnosis** — không bao giờ nhận raw Oracle data và không bao giờ trả về free-form text.

### Nguyên tắc

| Nguyên tắc | Giải thích |
|---|---|
| **Evidence-first** | LLM chỉ được gọi sau khi có đủ evidence từ deterministic rules |
| **Structured I/O** | Input: EvidencePackage, Output: DiagnosisResult (JSON) |
| **Multi-provider** | Không lock-in một LLM, có thể switch OpenAI/Claude/Gemini |
| **No credentials leak** | LLM không bao giờ nhận Oracle credentials hoặc PII |
| **No auto-execute** | LLM chỉ được recommend, không được suggest execute |

---

## 2. Component Overview

```
db-copilot/ai/
│
├── providers/
│   ├── openai_provider.py    # OpenAI GPT-4o
│   ├── claude_provider.py    # Anthropic Claude
│   └── gemini_provider.py    # Google Gemini
│
├── prompts/
│   ├── diagnosis_prompt.py   # System prompt cho diagnosis
│   └── report_prompt.py      # System prompt cho daily report
│
└── service.py                # AI service orchestrator
```

---

## 3. LLM Provider Interface

```python
# src/db_copilot/domain/interfaces/llm_provider.py

from abc import ABC, abstractmethod

class LLMProvider(ABC):

    @abstractmethod
    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """
        Nhận evidence package, trả về structured diagnosis.
        Output PHẢI là DiagnosisResult — không trả free-form text.
        Raise LLMDiagnosisError nếu không thể tạo structured output.
        """
        pass

    @abstractmethod
    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str
    ) -> str:
        """
        Tạo một section của daily report (markdown format).
        section_type: "critical", "warning", "info", "summary"
        """
        pass

    @abstractmethod
    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        """
        Parse natural language question thành InvestigationIntent dict.
        Separate, nhỏ call — không cần full evidence context.
        """
        pass
```

---

## 4. Evidence Package Schema

```python
# src/db_copilot/domain/models/diagnosis.py

@dataclass
class EvidencePackage:
    # Core
    question: str
    intent: InvestigationIntent

    # Evidence
    evidence: list[Evidence]          # All collected evidence
    hypotheses: list[Hypothesis]      # Pre-ranked by Hypothesis Engine

    # Context
    database_name: str
    investigation_timestamp: datetime
    investigation_duration_seconds: float

    # Additional data (filtered, not raw Oracle data)
    sql_details: dict | None = None   # SQL text, plan summary
    source_fragment: str | None = None # PL/SQL source fragment (NOT full source)
    baseline_data: dict | None = None  # Baseline comparison

    # What LLM should NOT know
    # oracle_credentials: ← NEVER included
    # raw_oracle_rows: ← NEVER included (only processed evidence)
```

---

## 5. Structured Output Schema

LLM **bắt buộc** trả về JSON theo schema sau:

```python
@dataclass
class Recommendation:
    action: str           # "Gather statistics for ACCOUNT_POSITION"
    sql: str | None       # SQL command (display only, never auto-execute)
    priority: str         # "HIGH", "MEDIUM", "LOW"
    note: str             # "DBA must review and execute manually"

@dataclass
class DiagnosisResult:
    diagnosis: str                    # Tóm tắt chẩn đoán
    confidence: float                 # 0.0 – 1.0
    primary_cause: str                # Root cause chính
    evidence_used: list[str]          # Evidence hỗ trợ kết luận
    evidence_against: list[str]       # Evidence mâu thuẫn
    recommendations: list[Recommendation]
    confidence_explanation: str       # Giải thích tại sao confidence = X%
    alternative_causes: list[str]     # Các nguyên nhân khác ít khả năng hơn
```

---

## 6. Diagnosis Prompt Design

```python
# src/db_copilot/ai/prompts/diagnosis_prompt.py

DIAGNOSIS_SYSTEM_PROMPT = """
You are an expert Oracle Database Performance Engineer.

TASK: Analyze the provided database investigation evidence and provide a structured diagnosis.

RULES:
1. Base ALL conclusions ONLY on the provided evidence — never use general knowledge as primary evidence.
2. If evidence is insufficient, say so explicitly and lower confidence.
3. Do NOT suggest any automatic execution. All recommendations must be prefixed with "DBA must review and execute manually."
4. Confidence must reflect actual evidence quality:
   - < 0.5: Insufficient evidence
   - 0.5 – 0.7: Partial evidence, possible cause
   - 0.7 – 0.9: Strong evidence, likely cause
   - > 0.9: Very strong evidence, highly probable cause
5. Always include contradicting evidence (what rules out other causes).
6. SQL in recommendations is for human review only — clearly state this.

OUTPUT FORMAT: Return ONLY valid JSON matching the DiagnosisResult schema. No markdown, no explanation outside JSON.
"""

DIAGNOSIS_USER_TEMPLATE = """
QUESTION: {question}

DATABASE: {database_name}
INVESTIGATION TIME: {timestamp}

PRE-RANKED HYPOTHESES (from deterministic analysis):
{hypotheses_json}

EVIDENCE COLLECTED:
{evidence_json}

ADDITIONAL CONTEXT:
{context_json}
"""
```

---

## 7. Provider Implementations

### 7.1 OpenAI Provider

```python
# src/db_copilot/ai/providers/openai_provider.py

from openai import AsyncOpenAI
from db_copilot.domain.interfaces.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):

    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI()
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        user_prompt = DIAGNOSIS_USER_TEMPLATE.format(
            question=package.question,
            database_name=package.database_name,
            timestamp=package.investigation_timestamp.isoformat(),
            hypotheses_json=json.dumps(
                [h.__dict__ for h in package.hypotheses], indent=2
            ),
            evidence_json=json.dumps(
                [self._serialize_evidence(e) for e in package.evidence], indent=2
            ),
            context_json=json.dumps({
                "sql_details": package.sql_details,
                "source_fragment": package.source_fragment
            }, indent=2)
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,          # Low temperature for consistent structured output
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw_json = response.choices[0].message.content
        return DiagnosisResult(**json.loads(raw_json))

    def _serialize_evidence(self, e: Evidence) -> dict:
        """Serialize evidence, removing any sensitive fields."""
        return {
            "type": e.type.value,
            "entity": f"{e.entity_type}:{e.entity_id}",
            "severity": e.severity.value,
            "data": e.data  # Already sanitized by collector
        }
```

### 7.2 Claude Provider

```python
# src/db_copilot/ai/providers/claude_provider.py

import anthropic

class ClaudeProvider(LLMProvider):

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.AsyncAnthropic()
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=DIAGNOSIS_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": self._build_user_prompt(package)}
            ]
        )

        # Claude không có native JSON mode → parse manually
        raw_text = response.content[0].text
        # Strip markdown code blocks nếu có
        raw_json = self._extract_json(raw_text)
        return DiagnosisResult(**json.loads(raw_json))
```

### 7.3 Gemini Provider

```python
# src/db_copilot/ai/providers/gemini_provider.py

import google.generativeai as genai

class GeminiProvider(LLMProvider):

    def __init__(self, model: str = "gemini-1.5-pro"):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={"response_mime_type": "application/json"}
        )

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        prompt = f"{DIAGNOSIS_SYSTEM_PROMPT}\n\n{self._build_user_prompt(package)}"
        response = await self.model.generate_content_async(prompt)
        return DiagnosisResult(**json.loads(response.text))
```

---

## 8. AI Service Orchestrator

```python
# src/db_copilot/ai/service.py

class AIService:
    """
    Orchestrates LLM calls.
    Handles: provider selection, retry, fallback, error handling.
    """

    def __init__(self, settings: Settings):
        self.primary = self._create_provider(settings.llm_provider)
        self.fallback = self._create_provider(settings.llm_fallback_provider)

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        try:
            return await asyncio.wait_for(
                self.primary.diagnose(package),
                timeout=30.0  # 30s timeout cho LLM call
            )
        except asyncio.TimeoutError:
            logger.warning("Primary LLM timed out, trying fallback")
            return await self.fallback.diagnose(package)
        except LLMDiagnosisError as e:
            logger.error(f"LLM diagnosis failed: {e}")
            return self._fallback_diagnosis(package)

    def _fallback_diagnosis(self, package: EvidencePackage) -> DiagnosisResult:
        """
        Khi LLM fail hoàn toàn, tạo diagnosis từ Hypothesis Engine output.
        Không dùng LLM, chỉ dùng hypotheses đã có.
        """
        top_hypothesis = package.hypotheses[0] if package.hypotheses else None
        return DiagnosisResult(
            diagnosis=top_hypothesis.name if top_hypothesis else "Unable to diagnose",
            confidence=top_hypothesis.confidence if top_hypothesis else 0.0,
            primary_cause=top_hypothesis.name if top_hypothesis else "Unknown",
            evidence_used=[e.type.value for e in package.evidence[:5]],
            evidence_against=[],
            recommendations=[
                Recommendation(
                    action="Review the evidence manually",
                    sql=None,
                    priority="HIGH",
                    note="AI diagnosis unavailable. DBA must review manually."
                )
            ],
            confidence_explanation="Diagnosis based on rule engine only (AI unavailable)",
            alternative_causes=[]
        )

    def _create_provider(self, provider_name: str) -> LLMProvider:
        match provider_name:
            case "openai":
                return OpenAIProvider(model=settings.openai_model)
            case "claude":
                return ClaudeProvider(model=settings.claude_model)
            case "gemini":
                return GeminiProvider(model=settings.gemini_model)
            case _:
                raise ValueError(f"Unknown LLM provider: {provider_name}")
```

---

## 9. Report Generation

```python
# src/db_copilot/ai/prompts/report_prompt.py

REPORT_SYSTEM_PROMPT = """
You are an Oracle Database monitoring system generating a daily health report for DBAs.

RULES:
1. Be concise and actionable — DBAs are busy.
2. Group issues by severity: CRITICAL > WARNING > INFO.
3. For each issue, provide: what happened, evidence summary, specific recommendation.
4. Use plain language — avoid jargon where possible.
5. Always end with: "No automatic database changes were executed."
6. Never recommend automatic execution of any database commands.

FORMAT: Clean markdown. Use headings, bullet points, and code blocks for SQL.
"""

class AIService:
    async def generate_daily_report(
        self,
        incidents: list[Incident],
        health_score: int,
        database_name: str,
        report_date: date
    ) -> str:
        """
        Generate markdown daily report from incidents.
        """
        # Build context (no credentials, no sensitive data)
        report_context = {
            "database": database_name,
            "date": report_date.isoformat(),
            "health_score": health_score,
            "critical_count": sum(1 for i in incidents if i.severity == Severity.CRITICAL),
            "warning_count": sum(1 for i in incidents if i.severity == Severity.MEDIUM),
            "incidents": [self._serialize_incident(i) for i in incidents]
        }

        response = await self.primary.generate_report_section(
            incidents=incidents,
            section_type="full_report"
        )
        return response
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 10. Overview

AI Engine is the only layer in `db-copilot` that communicates with LLMs. It receives **structured evidence** from Investigation Engine and returns **structured diagnosis** — never raw Oracle data in, never free-form text out.

---

## 11. Multi-Provider Architecture

```
AIService (orchestrator)
    │
    ├── Primary Provider  (configured via LLM_PROVIDER env)
    │   ├── OpenAIProvider (GPT-4o)
    │   ├── ClaudeProvider (Claude 3.5 Sonnet)
    │   └── GeminiProvider (Gemini 1.5 Pro)
    │
    └── Fallback Provider (LLM_FALLBACK_PROVIDER env)
        └── Falls back to rule-engine diagnosis if both fail
```

---

## 12. Provider Selection

```python
# .env
LLM_PROVIDER=openai
LLM_FALLBACK_PROVIDER=claude
OPENAI_MODEL=gpt-4o
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_MODEL=gemini-1.5-pro
```

---

## 13. Evidence Sanitization

Before sending to LLM, evidence is:
1. **Serialized** from typed objects to JSON
2. **Filtered**: Oracle credentials, connection strings, PII → removed
3. **Summarized**: Large objects (SQL plans) → summary only
4. **Truncated**: Source code → only relevant fragment (±20 lines around matching line)

---

## 14. Fail-Safe Behavior

| Failure Mode | Response |
|---|---|
| LLM timeout (> 30s) | Try fallback provider |
| Both providers fail | Return rule-engine based diagnosis (lower confidence) |
| JSON parse error | Retry with stricter JSON formatting instruction |
| Invalid schema | Return error with partial results |

**The system always returns some diagnosis.** Even if LLM is completely unavailable, the Hypothesis Engine provides a fallback diagnosis based on deterministic scoring.

---

## 15. Prompt Design Principles

1. **Low temperature** (0.1): Consistent, deterministic output
2. **JSON mode enabled**: Where supported (OpenAI), forces JSON output
3. **Evidence-first instructions**: LLM explicitly told to base conclusions on evidence, not general knowledge
4. **No-execute clause**: Explicitly instructed that recommendations are for human review only
5. **Confidence calibration**: Clear guidance on what different confidence levels mean
