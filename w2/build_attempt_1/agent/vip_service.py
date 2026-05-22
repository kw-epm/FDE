"""VIP controlled-list service interface.

APD: System and Data Inventory row "VIP controlled-list service" — does NOT
exist; P0 launch blocker. We define the integration contract only and ship a
stub implementation for tests / mock runs.

Design constraints carried over from APD (non-negotiable):
  - Exact match on Discourse account_id (integer), NOT on username
  - Live query at task 1.3 (no caching, no static config) — additions take
    effect without agent restart
  - Returns a rule key + routing target so 1.3E knows where to send
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Set


@dataclass(frozen=True)
class VipRecord:
    account_id: int
    rule_key: str  # e.g. "sponsor_2024", "established_sculptor"
    routing: str = "tom_queue"  # APD: VIP match -> Tom


class VipService(Protocol):
    """Contract. Production implementation queries the (to-be-built) VIP service."""

    def lookup(self, account_id: int) -> Optional[VipRecord]: ...


class StubVipService:
    """In-memory stub. Seeded with the 3 named accounts from artefact 4.3.

    NOT for production. The production VIP service must be a network query so
    that hot-reload (APD Operational Constraints) works without redeploy.
    """

    # Username -> account_id mapping is fabricated; APD treats the 3 names as a
    # known minimum, not a closed list. account_ids here are placeholders so
    # the stub can run; they MUST be replaced from the real VIP service before
    # any deployment. CLAUDE.md "What not to fabricate" applies — these
    # integers are placeholders, not facts about real users.
    _SEED: Set[int] = {1001, 1002, 1003}  # placeholder ids, not real

    def __init__(self, account_ids: Optional[Set[int]] = None) -> None:
        self._ids = set(account_ids) if account_ids is not None else set(self._SEED)

    def lookup(self, account_id: int) -> Optional[VipRecord]:
        if account_id in self._ids:
            # rule_key would in production be returned by the service per record
            return VipRecord(
                account_id=account_id,
                rule_key=f"vip:{account_id}",
                routing="tom_queue",
            )
        return None

    def add(self, account_id: int) -> None:
        """Test helper — simulates Tom adding a VIP without restart."""
        self._ids.add(account_id)
