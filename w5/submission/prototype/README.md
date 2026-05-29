# ResolveOne — Capstone Prototype (Deliverable #12)

**Option C — Multi-Channel Customer Resolution · CloudServe Inc.**
Author: Krzysztof Wilniewczyc · built from the design package (`../01`…`../10`, `../CLAUDE.md`).

An agentic customer-resolution prototype. It reads an inbound ticket (chat / email /
phone), assembles context, and makes the **load-bearing disposition decision**:
auto-resolve a read-only request, pre-fill an entitlement request for a human to
approve, or escalate — all on the sealed-pack **mock data**, no live systems.

## What's agentic vs deterministic

The agent's *judgment* is the LLM (Haiku classifies, Sonnet decides the residual tier
and composes the reply). The *binding safety policy* is deterministic code — the
guardrail layer in `core/guardrails.py`. The LLM **proposes**; the deterministic layer
**disposes**: a proposed Tier-1 auto-resolve that fails the allow-list / confidence /
KB-grounding / guardrail checks is downgraded to a human gate. Guardrails can only
*downgrade* autonomy, never upgrade it. That boundary is the answer to "isn't this just
an LLM wrapper?" — no, the money/identity/legal decisions are made in code.

## Run it

```bash
cd prototype
python3 demo.py            # runs the 4 paths in sequence (target < 5 min)
python3 -m pytest -q       # 11 tests across all three required paths + safety negatives
python3 eval.py            # scores the agent against data/ground-truth-labels.csv (48 rows)
```

**Offline by default.** With no `ANTHROPIC_API_KEY`/SDK, a deterministic mock stands in
for the model so everything runs and the tests pass — this validates the *architecture
and guardrails*, not model accuracy.

**Live (genuinely agentic) path** — for the demo:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python3 demo.py            # banner now reads: provider: live (haiku/sonnet)
```

## Web UI (React + FastAPI)

A browser demo surface over the same agent. **One command** starts the backend and the
React UI together (auto-installs the UI deps on first run); Ctrl-C stops both:

```bash
# from prototype/
export ANTHROPIC_API_KEY=sk-ant-...   # optional; omit for the offline mock
python3 run.py                        # backend :8000 + Vite UI :5173 — open http://localhost:5173
```

Prefer two terminals (e.g. to see logs separately)? Run them by hand:

```bash
uvicorn server:app --port 8000        # terminal 1 (from prototype/)
cd ui && npm install && npm run dev    # terminal 2  -> http://localhost:5173 (proxies /api -> :8000)
```

Pick one of the four demo paths or paste your own ticket; the panel shows the tier
(colour-coded), action, route, cited KB, guardrail flags, the LLM-call count (0 for
phone), the rationale, and the customer-facing draft. `demo.py` (CLI) remains the
zero-dependency fallback for the live defense if the UI hiccups.

## Container / Kubernetes

One image, one port: a multi-stage build compiles the React UI to static files, then the
FastAPI runtime serves **both** the API (`/api/*`) and the built UI (`/`) on **:8000** —
so it's a single Deployment + Service in k8s.

```bash
# build & run locally (from prototype/)
docker build -t resolveone:1.0 .
docker run --rm -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... resolveone:1.0
# -> open http://localhost:8000   (omit the key for the offline mock)
```

Kubernetes — manifests in `k8s/` (Deployment + Service, `LoadBalancer` + `nodePort`,
an `imagePullSecret` named `regcred`):

```bash
# tag + push to the private registry
docker tag resolveone:1.0 docker.xyh.pl/resolveone:latest
docker login docker.xyh.pl
docker push docker.xyh.pl/resolveone:latest

# API key as a secret (optional; omit -> offline mock)
kubectl create secret generic resolveone-secrets \
    --from-literal=anthropic-api-key=sk-ant-...

# the manifest already references docker.xyh.pl/resolveone:latest:
kubectl apply -f k8s/resolveone-dep.yaml -f k8s/resolveone-service.yaml
kubectl get pods,svc -l app=resolveone
```

Exposed on a `nodePort` — front it with your ingress / load-balancer. Runs as non-root
(uid 10001); the audit log writes to `/app` (ephemeral) — mount a volume to persist.

## The demo paths (Deliverable #12 requirement)

| Path | Ticket | Expected |
|---|---|---|
| **Happy** | `CS-2026-0000002` password reset | Tier 1 `AUTO_RESOLVE`, cites `password-reset.md` |
| **Failure-mode escalation** | `CS-2026-0000011` refund | Tier 2 `PREFILL_AND_ROUTE` → Billing/Ravi Chen, `approved=False`, holding message promises nothing |
| **Edge (phone)** | `CS-2026-0000010` phone | `DEFER_PHONE`, **zero LLM calls**, transcript never read |
| **Edge (legal, bonus)** | `CS-2026-0000306` return + AG threat | Tier 3 `ESCALATE` → Uma (legal overrides the entitlement route) |

## Layout

```
prototype/
  models.py         # dataclasses + enums (spec §0.7)
  config.py         # thresholds τ/τ_r/τ_floor, allow-list, anchors, lexicons, routing
  util.py           # word-boundary keyword matching (spike finding #3)
  adapters/         # chat.py / email.py / phone.py -> Ticket
  core/
    stores.py       # CustomerStore (fail-loud, no default record)
    retrieve.py     # KBIndex (query-token-coverage retrieval)
    llm.py          # LiveProvider (Haiku/Sonnet) + MockProvider + build_provider()
    guardrails.py   # deterministic, downgrade-only safety layer
    entitlement.py  # Spec B — pre-fill + human gate; never approves
    disposition.py  # Spec A — the triage orchestrator
    audit.py        # append-only JSONL + idempotency
  demo.py · eval.py · tests/ · data/   # data = sealed Capstone-C fixtures
```

See `SPEC_AMENDMENTS.md` for the (minor) divergences from the submitted design and the
build-exposed notes.
