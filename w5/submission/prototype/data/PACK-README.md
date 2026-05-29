# Capstone Option C — Multi-Channel Customer Resolution Pack (Participant Edition)

**Pack version:** v1.0 (2026-04-27)
**Scenario:** Capstone Option C — CloudServe Inc. Multi-Channel Customer Resolution
**Purpose:** A simulated 7-day slice of CloudServe's support intake — 2,300 tickets across **chat, email, and phone**, plus the surrounding customer master and KB article library — **delivered in their real on-the-wire formats** (Zendesk-style ticket JSON with embedded chat transcripts, RFC 5322 `.eml` for email tickets, WebVTT for phone-call transcripts, RFC 4180 CSV for customer master, Markdown for KB articles). This is the **fixture data** you use to design, test, and demo your agentic customer-resolution solution during the Capstone week.

> ⚠️ **All data is synthetic.** No real customer accounts, names, emails, payment data, ticket numbers, or call transcripts. The "CloudServe Inc." organisation and the three stakeholder personas (Amanda Torres, Jennifer Park, David Okonkwo) are fictional. Do not treat any value in this pack as a real-world identifier.

> 🔒 **There is no answer key in this folder.** Coaches hold a separate per-ticket ground-truth oracle for grading. Your job is to design your *own* disposition and validation logic and evaluate your agent against it — see "Grading & validation" below.

---

## Why this pack exists

Capstone Option C is built around the scenario:

> *CloudServe Inc. — ~10,000 support tickets/month across chat, email, and phone. Auto-resolution rate near zero today. NPS at 6.2; competitors at 7.5+. CCO Amanda Torres wants an AI resolution agent live in 60 days; CCC Jennifer Park requires human approval for any decision affecting customer entitlements (refunds, cancellations, account modifications); CTO David Okonkwo says the legacy Avaya telephony stack can't host AI integration safely — chat and email only, on modern infrastructure.*

Your job during the Capstone is to design (and partially build) an agentic customer-resolution solution that **safely** auto-handles the read-only majority (password resets, billing Q&A, KB-lookup how-to questions), correctly **routes refunds and cancellations through human approval** (Jennifer's compliance gate), and **explicitly excludes the phone channel** until the platform modernization completes (David's blocker). Without realistic fixture data, every solution looks plausible on paper. With this pack, you can:

- run a real agent against a representative week of intake and measure its disposition accuracy *per channel and per issue type* against *your own* validation set;
- check whether your design correctly **refuses** to auto-resolve refunds and cancellations on AI alone — a solution that approves entitlement changes without a human in the loop is a **failure mode**, not a feature;
- check whether your design correctly **defers** the phone channel — a solution that pretends to handle voice transcription end-to-end on day one is also a failure mode;
- demo the *messy reality* of multi-channel support intake to a stakeholder who thinks "just plug in a chatbot."

This pack is **not** a benchmark suite. It's a representative week of intake. Treat it like one.

---

## What's in the pack

| Folder / file | Format | File ext | Count | Notes |
|---|---|---|---:|---|
| `customers/customer_master.csv` | RFC 4180 CSV | `.csv` | 1 (3,000 rows) | Source-of-truth account list — 11 columns covering plan, MRR, tenure, last NPS, churn score, support tier. |
| `kb-articles/` | Markdown | `.md` | 20 | The resolution playbook. Articles for password reset, refund policy, cancellation process, billing FAQ, complaint handling, abusive-language policy, contract-change escalation, etc. Your agent should match each ticket to the relevant article(s). |
| `tickets/` | Zendesk-style JSON | `.json` | 1,150 | One file per **chat-channel** ticket. Full ticket metadata (priority, status, SLA, tags, requester) plus an embedded `chat_transcript` array with multi-turn customer ↔ agent messages, including `internal_note: true` for staff-only turns. |
| `email-threads/` | RFC 5322 | `.eml` | ~1,700 (across 690 tickets) | Each email-channel ticket spans 1–3 messages. Real `From`/`To`/`Subject`/`Date`/`Message-ID` headers, replies linked via `In-Reply-To` and `References`. Custom `X-CloudServe-Ticket-Id`/`X-CloudServe-Channel`/`X-CloudServe-Customer-Id` headers tie each message to its ticket. |
| `phone-calls/` | WebVTT | `.vtt` | 460 | Speaker-tagged call transcripts (`<v Agent>` / `<v Customer>` cues with timestamped intervals). Same format Twilio Voice, Zoom, and AWS Transcribe emit. NOTE blocks at the top carry the ticket_id and customer_id for cross-reference. |
| **Total** | | | **1 + 20 + 1,150 + ~1,700 + 460 ≈ 3,330 files** | |

> 🎲 **Your pack is one fresh non-deterministic draw.** The concrete tickets, customers, and transcripts in your copy are unique to your draw — the channel mix and issue-type distribution match the scenario, but the specific data does not match anyone else's pack. (Coaches regenerate packs from a generator they hold; you don't need it.)

A representative week of intake is a *mix* of dispositions: a large share are safely auto-resolvable read-only requests; a meaningful slice affect customer entitlements (refunds, cancellations, downgrades) and **must go through a human-approval gate**; the entire phone channel is **out of scope** until the telephony platform is modernized; and a remaining slice needs explicit escalation to a specialist. **Part of the exercise is determining the right disposition for each ticket yourself** — your agent has to decide, not be handed the answer.

---

## How to use this pack

1. **Start with one channel.** Don't try to ingest all three on day one. Most teams pick `tickets/` (chat JSON — fully structured, in-band transcripts) to bootstrap.
2. **Define your own ground truth as you go.** Since there is no answer key in this folder, hand-label a sample of tickets with their correct disposition and measure your agent against that. Your validation design is a graded deliverable (Capstone Deliverable #9).
3. **Measure disposition accuracy first, *then* resolution quality.** A solution that nails read-only auto-resolution but misroutes refunds into auto-approval is **worse** than one with lower raw throughput and zero false entitlement approvals. The compliance failure mode is the dealbreaker — weight human-approval precision above raw throughput.
4. **Tackle email second.** Threading via `In-Reply-To` is what your agent must reconstruct — don't keyword-match across a flat dump. Use a real `email.parser`.
5. **Treat the phone channel as out-of-scope by design.** If your agent silently includes `phone` in its handled set, you've broken David's infrastructure constraint. Better: explicitly route `channel == "phone"` to a human queue and surface the architectural rationale.
6. **Use the KB articles as the agent's tool surface, not its training data.** A real production agent looks up KB articles on demand and quotes them. A weaker design tries to memorise the whole KB and respond from latent knowledge.

---

## Grading & validation

There is **no `master-index.csv` or answer key in this folder.** Coaches hold a separate per-ticket ground-truth oracle (expected disposition, expected KB articles, value-at-risk, risk flags) and grade your agent's output against it after you submit.

What this means for you:

- **Build your own validation design.** Hand-label a representative sample of tickets across all three channels, define your per-disposition precision metrics, and report honestly against your own labels. Your validation plan is graded.
- **The worst failure mode is auto-approving an entitlement change.** AI-approving a refund or cancellation that should have gone through Jennifer Park's human-approval gate breaks compliance — it is the single most dangerous error in this scenario, worse than a missed auto-resolution. Pretending to handle the phone channel is the second-worst.
- **Be explicit about coverage.** Volunteer what your solution does *not* handle (e.g., "we don't process the phone channel — that's the CTO's constraint") and why. Silently including phone, or quietly auto-approving refunds when the customer "clearly meant it," is the weakest move in the defense.

---

## Sample file pointers

For quick orientation, open one file per format. Because each pack is a fresh draw, exact filenames vary — pick any file in each folder:

- Customer master: `customers/customer_master.csv` (open in any spreadsheet or text editor)
- KB article: `kb-articles/refund-policy.md` (the highest-leverage policy article — it explicitly says the AI agent cannot issue refunds)
- Chat ticket (read-only, auto-resolvable): `tickets/` (any `.json` — pretty-printed; look for a `chat_transcript` array with multiple turns)
- Chat ticket (entitlement change — human-approval territory): `tickets/` — find one where `issue_type` is `refund_request` or `service_cancellation` to see how a pre-fill-and-route design would handle it
- Email thread: `email-threads/` (any `.eml` — open in any mail client; replies link via `In-Reply-To` and `References`)
- Phone-call transcript: `phone-calls/` (any `.vtt` — open in any text editor or a player that supports WebVTT)

---

## What the pack is *not*

- **Not real customer data.** All customer accounts, emails, payment amounts, and call transcripts are synthetic.
- **Not connected to a live ticketing system.** The Zendesk-style JSON is realistic and consistent, sufficient for parser exercises and round-tripping. It's not certified for import into any specific ticketing platform.
- **Not exhaustive of every possible support issue.** The issue-type and risk taxonomies cover the most common operational issues a SaaS support desk sees. Real desks see hundreds of edge cases out of scope here.
- **Not an audio file.** The phone-channel transcripts are WebVTT text — there is no MP3/WAV. If you want to demo audio-in transcription, synthesize the audio from the VTT or treat it as already done.
- **Not a benchmark.** There is no leaderboard, no canonical score. Your agent design is the deliverable; this pack is the test bed.

---

## File manifest

```
./
├── README.md                              # This file
├── customers/
│   └── customer_master.csv                #   1 file, 3,000 customer rows
├── kb-articles/                           #  20 .md files (resolution playbook)
├── tickets/                               # 1,150 .json files (chat-channel tickets with embedded chat transcripts)
├── email-threads/                         # ~1,700 .eml files across 690 email-channel tickets (RFC 5322 with In-Reply-To/References)
└── phone-calls/                           #   460 .vtt files (WebVTT speaker-tagged call transcripts)
```

*The ground-truth oracle, answer-distribution stats, and the pack generator are held by coaches (not in this folder). Evaluate your agent against your own validation design.*
