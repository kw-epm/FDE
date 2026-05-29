# Capstone demo script — ResolveOne (5 minutes, live)

Spoken narration for the Gate 5a live demo. Budget: **5:00**. Primary surface is the **React UI**
(`python3 run.py` → http://localhost:5173), which shows a **live agent trace** — each agent lights
up as it runs. `python3 demo.py` (CLI, same four paths) is the fallback.

**SAY** = what to say · **DO** = what to run/click · **POINT** = what to point at · **POINT (trace)** = what to narrate on the live agent trace as it fills in.

---

## Before your slot (pre-flight, not timed)
- [ ] `export ANTHROPIC_API_KEY=...` first, so the UI banner reads **`provider: live (haiku/sonnet)`** (a mock-only run reads as a rules engine).
- [ ] `cd prototype && python3 run.py`, open **http://localhost:5173**, click each demo path once — confirm the live trace fills in. **Restart `run.py` after any code change** (the backend does not hot-reload — a stale server is what causes a "Not Found").
- [ ] Browser zoomed so the coach can read the live trace + the disposition.
- [ ] `python3 demo.py` (CLI) ready as the fallback if the UI hiccups.

---

## 0:00–0:45 — Open on the architecture
**DO:** have the UI open at http://localhost:5173 (the banner shows `provider` + the agent roster).
**SAY:** "This is ResolveOne — it handles CloudServe support tickets. It isn't one big model call. It's **one coordinator agent and four worker agents**. The coordinator reads the ticket, asks a cheap model to classify it, then checks a set of hard rules — the **guardrail gate**. Those rules are plain code. They can only make the agent *more* careful, never less. Then the coordinator hands the ticket to **one** worker."
**POINT:** the topology line in the banner, then: "When I click a ticket you'll see each agent light up as it runs — that's the real call sequence, not an animation."

> **Narrating the live trace (the technique).** Each path below fills the **Agent run** panel top-to-bottom as the agents fire. The line with the spinner is the agent running *right now*; it flips to a dot when done. Read the handoff out loud as it happens — "Triage on Haiku… now the Coordinator decides… now the Resolution worker writes the reply." In live mode each model call takes a second or two, so the trace paces your narration for you.

## 0:45–2:00 — Happy path (Tier 1 auto-resolve)
**POINT:** first block — `handled_by=resolution`.
**SAY:** "First, the easy case — a password reset. The coordinator decided it's safe to auto-resolve, so it gave it to the **Resolution worker**. The reply isn't made up — it **quotes our help article**, `password-reset.md`. If no article matched, it would not send an answer at all. That's a hard rule: no citation, no auto-reply."
**POINT (trace):** "Triage on Haiku → Coordinator decides **Tier 1** → **Resolution** composes. Three model calls, and you watched each one fire."

## 2:00–3:15 — Failure-mode escalation (refund → human gate)
**POINT:** `handled_by=entitlement`, then the holding message.
**SAY:** "Now a refund — this is the important one. The guardrail gate caught it and forced it to a human **before the model got a vote**. The **Entitlement worker** did everything *except* decide: it pre-filled the request and routed it to Billing. Read the customer note — it never says 'approved', never promises the money. **No agent in this system can approve a refund. That code path doesn't exist.**"
**POINT (trace):** "Triage → the gate flags **ENTITLEMENT** → straight to the **Entitlement** worker. Notice the Coordinator never even makes a 'decide' call — the rule routed it before the model could weigh in."

## 3:15–4:00 — Edge case: phone (defer, zero LLM calls)
**POINT:** the `[check] LLM calls ... (phone must add 0): PASS` line.
**SAY:** "Edge case — a phone call. The CTO's rule is: no AI on phone until the old system is replaced. So the coordinator **stops immediately** — it never reads the transcript. Look at the counter: **zero model calls** on this ticket. We don't fake a channel we were told to leave alone."
**POINT (trace):** "Two lines only — *received*, then *phone short-circuit*. No Triage, no worker, no model call. You're watching it refuse to touch the channel."

## 4:00–4:40 — Bonus edge: legal override (rule beats the model)
**POINT:** `handled_by=escalation`, flags `['ENTITLEMENT', 'LEGAL']`.
**SAY:** "Last one — a return where the customer mentions their attorney general. Two rules fire: it's a refund **and** it's legal. The model classified it as a normal refund — but the **gate beat the model** and pushed it to Tier 3, to Compliance. The **Escalation worker** wrote a briefing for the human. The rule wins, every time."
**POINT (trace):** "Triage reads it as a refund → the gate fires **ENTITLEMENT + LEGAL** → **Escalation** worker. You can literally see the rule override the model's call."

## 4:40–5:00 — Close (the honest gap)
**POINT:** the audit-log line.
**SAY:** "Every ticket writes one audit line. To be straight about the gap: this runs on **mock data**; the model layer swaps to live Haiku and Sonnet with a key; and the thing I'd watch in production is **classifier drift** on the read-only allow-list — that's what the weekly sampling audit is for. That's the demo."

---

## Three lines to land (if you remember nothing else)
1. **"The model proposes; the deterministic gate disposes."** — it's agentic, but the compliance calls are in code.
2. **"No agent can approve a refund — that path doesn't exist."** — the #1 automatic-fail, closed by design.
3. **"Phone makes zero model calls."** — we respect the CTO's red line, we don't fake the channel.

## If something breaks (fallback)
- UI glitch → drop to the terminal: `python3 demo.py`. Same four paths, same story.
- Live API error → say so plainly, restart with the offline mock (`unset ANTHROPIC_API_KEY`), and name it: "the architecture and guardrails are what's running; the mock stands in for the model."
- Out of time → the **refund** path is the one that must be shown (the automatic-fail boundary). Cut the legal bonus first.

## Likely Q&A pivots (10-min block, after the demo)
- *"Isn't this just an LLM wrapper?"* → the guardrail gate (code) makes the binding calls; show `core/guardrails.py`.
- *"How do the agents communicate?"* → hub-and-spoke, in-process typed messages; coordinator is the only caller (ADR-6). MCP is the tool surface, not the agent path.
- *"What did multi-agent cost?"* → +$360/yr (#8 §4); ~1% of the labour saving. Justified on legibility, not dollars.
- *"What breaks in production the demo doesn't show?"* → classifier drift on the allow-list; the τ_r retrieval threshold needs real-data calibration; handle-time assumption in the economics.
