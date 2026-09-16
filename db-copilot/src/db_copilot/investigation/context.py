"""InvestigationContext — maintains state across investigation steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationContext:
    """Holds state accumulated during a multi-step investigation.

    Each step writes its results here; subsequent steps can reference
    prior outputs via dynamic parameter expressions like "$step_1.sql_id".
    """

    step_results: dict[str, Any] = field(default_factory=dict)
    collected_evidence: list[Any] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dynamic_parameters: dict[str, Any] = field(default_factory=dict)

    def record_step(self, step_id: str, result: Any) -> None:
        """Store a completed step result."""
        self.step_results[step_id] = result
        # Flatten top-level keys into dynamic_parameters for easy resolution
        if isinstance(result, list) and result:
            # Expose list as-is
            self.dynamic_parameters[f"{step_id}.items"] = result
            # Extract first item's keys for convenience ($step_1.sql_id etc.)
            first = result[0]
            if isinstance(first, dict):
                for sub_key, sub_val in first.items():
                    self.dynamic_parameters[f"{step_id}.{sub_key}"] = sub_val
                    if sub_key == "sql_id":
                        self.dynamic_parameters[f"{step_id}.top_sql_id"] = sub_val
        elif isinstance(result, dict):
            for key, value in result.items():
                self.dynamic_parameters[f"{step_id}.{key}"] = value
                # Also expose items in lists (e.g. first sql_id from a list)
                if isinstance(value, list) and value:
                    first = value[0]
                    if isinstance(first, dict):
                        for sub_key, sub_val in first.items():
                            self.dynamic_parameters[f"{step_id}.{sub_key}"] = sub_val
                            if sub_key == "sql_id":
                                self.dynamic_parameters[f"{step_id}.top_sql_id"] = sub_val

    def resolve_param(self, value: Any) -> Any:
        """Resolve dynamic parameter expressions in a value.

        Expressions take the form "$step_N.field_name".
        Works recursively on dicts and lists.
        """
        if isinstance(value, str) and value.startswith("$"):
            key = value[1:]  # strip leading $
            return self.dynamic_parameters.get(key, value)
        if isinstance(value, dict):
            return {k: self.resolve_param(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.resolve_param(v) for v in value]
        return value

    def resolve_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Resolve all dynamic parameters in a params dict."""
        return {k: self.resolve_param(v) for k, v in params.items()}
