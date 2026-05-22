# Discovery questions — MedFlex (Thu 09:30–10:30 call)

*Structured per `inputs/Sources/discovery-questioning-patterns.md` (60-min funnel). Plain English. Marcus is CEO — he knows top-line and strategic stuff. He defers operational detail to Kim (senior coordinator), Aaron (IT), Linda (compliance). None of them are on the call. So: ask Marcus what only Marcus can answer, and explicitly park the ops detail as follow-ups for the named people.*

---

## Scenario to zoom into (15–30 min narrow funnel)

**Pick: shift matching itself.** Specifically: a coordinator getting a hospital request and turning it into a confirmed, on-shift nurse.

**Why this one and not the others:**

- **Biggest leverage for "10x without 10x-ing."** 8 coordinators × 120 decisions/day = ~960 matches a day. If "10x" means anything, this is the number that has to move. Anywhere else we drill is a smaller lever.
- **The judgment is right here.** Matching uses credentials, proximity, hospital prefs, nurse prefs, and (somehow) a "quality score." That's exactly the place where a deterministic matcher won't cut it and reasoning-over-context might. If we can't find the agent decision here, the whole AI-native story falls apart.
- **The two failed projects point this way.** A recommender failed. Recommenders try to do matching. Marcus has scar tissue here. Asking *why the recommender failed while we are talking about matching* is the single highest-value question on the call.
- **It pulls the other threads in for free.** Once we're inside a real match, no-shows (12%), credential lapses, the "quality score", and the 4.2h fill time all surface naturally. We don't need separate slots for each.

**Fallback if Marcus deflects to "Kim handles that":** switch to **no-shows and urgent re-matching** (12% no-show rate). It's the same workflow under stress, and the stress version usually exposes the lived process faster than the happy path.

---

## 0–5 min — Friendly open + framing

Goal: lower the guard, frame why we're here, get a top-line read before drilling in. Marcus respects substance, so keep it short.

- *(read room ~30 sec — congratulate on Series B briefly, then move)*
- "Before we start — I'm not here to audit what you've got. I want to find the places where AI can actually help. So I'll ask you to walk through real work, not describe systems. Sound OK?"
- "Quick orientation question: when you say '10x the business without 10x-ing the coordinators' — what's the thing that breaks first if you don't fix it? Is it coordinator hours? Nurse supply? Hospital trust? Compliance? Something else?"

**Why these:**
- The framing line is a hard stop on feature-tour answers later.
- The "what breaks first" question is the only one Marcus can answer better than anyone, and the answer reframes the whole engagement. If he says "coordinator hours" we have a labour story. If he says "nurse supply" we have a marketplace story. Totally different architectures.

---

## 5–15 min — Broad funnel (where does coordinator attention go?)

Goal: get categories of work. Marcus won't know operational detail — but he has a view of where his coordinators waste time, and that view is itself useful (right or wrong).

- "Walk me through what a coordinator's day looks like to you. Not the SOP — what you actually see when you walk the floor."
- "Of the 120 decisions a coordinator makes a day — how many feel routine to them, and how many are the kind they'd want to talk to a colleague about?"
- "Where in the day do things slow down or pile up?"
- "When a coordinator is stuck, what are they stuck on? Waiting on data? Phoning a nurse? Checking a regulator?"

**Listen for:**
- Categories: matching · compliance check · nurse outreach · hospital coordination · no-show scramble · post-shift admin.
- Frustration: "the app doesn't know X, so they have to call Y" → these are the agentic openings.
- Marcus's own confidence: does he sound like he's describing what he's seen, or what he assumes? That tells us how much to trust this part of the input.

**Avoid:**
- "Tell me about your matching system" → feature tour.
- "What are the pain points?" → standard complaints.

**Transition cue:** once a category clearly comes up as the biggest time sink (likely matching), say *"That sounds like the biggest lever. Can we walk through a real case?"* and move to narrow funnel.

---

## 15–30 min — Narrow funnel (walk through a real match)

Goal: map an actual shift-match end-to-end. Force a real case, not a stock answer.

- "Pick the last shift one of your coordinators filled. Not a textbook one — a real one from this week. Walk me through it from the moment the hospital sent the request to the moment the nurse confirmed."
- *(as they walk through it)* "What systems did the coordinator open? In what order?"
- "Where did they stop and think? Where did they have to check something or call someone?"
- "When they picked that nurse out of the eligible ones — what made them pick that nurse?"
- "If a different coordinator had got that request, would they have picked the same nurse?"
- "How long did the whole thing take, roughly? Is 4.2 hours typical, or was this faster/slower?"

**Listen for:**
- Pause points and the systems behind them (this is where the contradictions usually surface)
- The judgment criteria for picking *that* nurse — proximity? rapport? "this nurse won't work nights at Hospital X"? That tacit stuff is the agent's home.
- Whether availability comes from one place or multiple places. **First contradiction probe** — see "Contradictions to hunt" below.

**Don't accept:**
- "They use the matching algorithm" — push back: "OK, but the algorithm gives them, say, five eligible nurses. How do they pick one?"
- "They follow the SOP" — "What does the SOP not tell them?"

---

## 30–45 min — Lived vs documented (and the contradictions)

Goal: surface the gap between what Marcus believes the system does and what coordinators actually do. This is where the planted contradictions live.

- "You said earlier that *[X]*. But in the case you just walked through, *[Y]* happened. Help me understand?"
- "How often does the process work exactly as you'd describe it on a whiteboard?"
- "What's the most common reason a match goes wrong? Who notices it first — the hospital, the nurse, or you?"
- "The 7% mismatch rate — how do you find out about it? Hospital complains? Nurse shows up and gets sent home? Audit?"
- "The 12% no-show rate — when a nurse no-shows, what actually happens in the next hour?"
- "Tell me about the quality score. How is it calculated? Who maintains it?"
- "On compliance — when a nurse's credential lapses, how does the system find out?"

**Contradictions to hunt** (per pack §4 — likely planted; flag gently if caught):

| What he might say early | What may come out later | The gap |
|---|---|---|
| "Our app is the source of truth for nurse availability" | "When a nurse calls in sick they call Kim, Kim updates by hand" | The app isn't the source of truth; Kim's notebook is |
| "Credentials are verified before nurses join the roster" | "When a credential lapses we get a state ping and re-verify in a week" | There's a verification *window*, not a verified *state* |
| "The 7% mismatch is hospital-flagged dissatisfaction" | "We have a quality score — trust me, it's reliable" | If quality is hospital-flagged it isn't a score, it's a complaint count. Two different things doing one job. |

**How to flag a caught one** (Marcus respects this — he'll concede): *"Earlier you said X. Just now Y. I'm not gotcha-ing — I want to know which one is the design input. Which is closer to the truth?"*

---

## 45–55 min — Delegation signals + the failed-projects probe

Goal: read whether the matching decision is genuinely agent-suitable, and at what level of autonomy. Plus the highest-leverage question of the call.

- "When a coordinator picks a nurse out of the eligible set, could they write down the rule they're using? Even roughly?"
- "What percentage of matches fit the standard pattern — and what percentage are the messy ones where they need to think hard?"
- "If an agent picked the nurse instead of a coordinator, what would have to be true for you to be comfortable shipping that match without human review? And separately — with human review of, say, the bottom 10% of confidence?"
- "If the agent gets it wrong — wrong nurse for the shift — what's the cost? Hospital cancels? Re-bill? Lost contract?"
- "Is matching time-critical? Are we filling shifts that start in 30 minutes, or in 3 days?"
- **The high-leverage one:** *"The recommendation engine — the one nobody used. What was it recommending, and what specifically did people not like about it? Was it wrong, or were they just not going to trust it?"*
- *(follow-up to the above)* *"What would have to be different for this to land differently?"*

**Listen for:**
- Codifiability ("I could write it down" vs "it's just experience") — both are agentic, but the architectures differ
- Reversibility — easy to undo a bad match before the shift starts; hard once the nurse is on site
- Latency — if some matches are 30-min urgent and others are 3-day planned, that's two different agent products
- The recommender post-mortem — this is the single best predictor of whether *our* design will land. If he says "it was wrong," that's a model/data problem. If he says "they didn't trust it," that's a workflow integration problem. Very different fixes.

---

## 55–60 min — Close

- Summarise back: "Here's what I heard — *[3 sentences]*. Did I miss anything important?"
- Confirm 2–3 facts you'll build on (the ones that anchor the architecture).
- Park the rest: "I'll send a short list to Kim, Aaron and Linda for the operational specifics — happy if that goes via you or direct."
- Flag next step: "By end of today I'll have rough drafts of problem framing, scope, and architecture. Marcus, you'll see something tomorrow morning."

---

## Things to write down during the call (not ask)

- Did Marcus contradict himself? On what? **Note the exact quote.**
- Did he defer to Kim / Aaron / Linda? On what? (That's the follow-up question list.)
- Did he push back on a premature solution? On what specifically? (Tells you where his scepticism lives.)
- What did he answer precisely vs. vaguely? (Vague = either he doesn't know, or he doesn't want to say.)

---

## Questions to NOT ask (would burn time / sound generic)

- "Tell me about your tech stack" — Aaron's question, not Marcus's. Park it.
- "What's your data infrastructure like?" — same.
- "What's your competitive landscape?" — interesting but not the gate's job.
- "Can you tell me more about your business model?" — already in the pack.
- Anything Marcus could give a McKinsey-deck answer to.
