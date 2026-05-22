"""End-to-end demo. Runs the worked example from D#4a §6 plus edge cases.

Usage:
    python -m d9_build.demo               # all scenarios
    python -m d9_build.demo worked         # just the worked example
    python -m d9_build.demo expired        # credential-expiry edge case
"""
from __future__ import annotations

import sys
from datetime import datetime

# Allow execution from inside the d9_build folder OR as a package from above.
if __package__ in (None, ""):
    sys.path.insert(0, ".")
    from medflex.comms import CommsLayer
    from medflex.lock_store import LockStore
    from medflex.pipeline import run, CoordinatorDecision
    from medflex.seed import NURSES, NOW
    from medflex.trust_ramp import TrustRamp
else:
    from .medflex.comms import CommsLayer
    from .medflex.lock_store import LockStore
    from .medflex.pipeline import run, CoordinatorDecision
    from .medflex.seed import NURSES, NOW
    from .medflex.trust_ramp import TrustRamp


WORKED_EXAMPLE_EMAIL = (
    "Need an ICU nurse for tomorrow's night shift. "
    "Prefer someone we've worked with before — the unit just admitted a "
    "paediatric patient with a rare medication allergy."
)


def _header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def scenario_worked_example_week8() -> None:
    _header("Scenario 1: D#4a §6 worked example — week 8 trust ramp, high conf, auto-send")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(),
        comms=CommsLayer(),
    )
    _print_summary(res)


def scenario_worked_example_week2() -> None:
    _header("Scenario 2: same request, week 2 — every offer needs coordinator approval")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=2),
        lock_store=LockStore(),
        comms=CommsLayer(),
        coordinator=lambda cd: CoordinatorDecision(approve_top=True,
                                                   note="LGTM — recognise Nicole at A"),
    )
    _print_summary(res)


def scenario_expired_credential() -> None:
    _header("Scenario 3: edge case 5 — Paula's credentials expire before shift; "
            "she is dropped at step 3")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(),
        comms=CommsLayer(),
    )
    _print_summary(res)


def scenario_comms_retry() -> None:
    _header("Scenario 4: comms layer drops the first 2 attempts; retry succeeds")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(),
        comms=CommsLayer(fail_first_n=2),
    )
    _print_summary(res)


def scenario_nurse_declines() -> None:
    _header("Scenario 5: edge case 3 — nurse declines; soft-lock releases (re-pool path)")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(),
        comms=CommsLayer(),
        nurse_decision="no",
    )
    _print_summary(res)


def scenario_lock_store_down() -> None:
    _header("Scenario 6: lock-state store unavailable — step 8 halts; ops alerted")
    res = run(
        raw_email=WORKED_EXAMPLE_EMAIL,
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(available=False),
        comms=CommsLayer(),
    )
    _print_summary(res)


def scenario_low_extraction_confidence() -> None:
    _header("Scenario 7: edge case 2 — ambiguous email; extraction confidence too low; "
            "routes to coordinator before ranking runs")
    res = run(
        raw_email="Hi we need a nurse, urgent-ish, sometime soon. Thanks!",
        hospital_id="hosp_A",
        received_at=NOW,
        nurses=NURSES,
        trust_ramp=TrustRamp(week=8),
        lock_store=LockStore(),
        comms=CommsLayer(),
    )
    _print_summary(res)


def _print_summary(res) -> None:
    print("\n  ---- run summary ----")
    print(f"  confidence: {res.confidence}")
    print(f"  decision:   {res.decision}")
    if res.confirmed:
        print(f"  CONFIRMED FILL: nurse {res.offered_to_nurse_id} / shift "
              f"{res.shift_request.id}")
        print(f"  primary KPI (request → hospital submission): "
              f"{res.primary_kpi_seconds/60:.1f} min")
    elif res.halted_at_step is not None:
        print(f"  HALTED at step {res.halted_at_step}: {res.halt_reason}")


SCENARIOS = {
    "worked":  scenario_worked_example_week8,
    "week2":   scenario_worked_example_week2,
    "expired": scenario_expired_credential,
    "comms":   scenario_comms_retry,
    "decline": scenario_nurse_declines,
    "lockdown": scenario_lock_store_down,
    "lowconf": scenario_low_extraction_confidence,
}


def main() -> None:
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            if name not in SCENARIOS:
                print(f"unknown scenario {name}; available: {list(SCENARIOS)}")
                sys.exit(2)
            SCENARIOS[name]()
        return
    for fn in SCENARIOS.values():
        fn()


if __name__ == "__main__":
    main()
