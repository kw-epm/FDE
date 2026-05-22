"""Step 6 — confidence gate × trust ramp.

Per D#4a §1:
  - weeks 1-2: manual approval for every offer
  - weeks 3-4: high-confidence auto-send
  - week 8+:   sample audits (auto-send remains the default for high conf)
Medium and low confidence always route to coordinator.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrustRamp:
    week: int   # 1-based week since rollout start

    def decision(self, confidence: str) -> str:
        if confidence == "high" and self.week >= 3:
            return "auto-send"
        if confidence == "high":
            return "flag-to-coordinator"  # weeks 1-2
        if confidence == "medium":
            return "flag-to-coordinator"
        return "coordinator-decides"      # low

    def label(self) -> str:
        if self.week <= 2:
            return "weeks 1-2 (manual approval)"
        if self.week <= 4:
            return "weeks 3-4 (high-confidence auto-send)"
        return f"week {self.week} (auto + sample audit)"
