# Scenario 4 — Community Content Moderation

## The platform

**MiniBase** — UK-incorporated tabletop-miniature hobbyist community platform (~180K active users, mostly UK / Western Europe / North America, with smaller bases in Japan and Australia). 12K posts/day across 14 sub-forums plus a gallery section. Revenue ~£1.4M/yr from premium memberships, gallery commissions, and sponsored content from miniature manufacturers.

## The function

Hybrid moderation team: 8 volunteer moderators (US, UK, Germany, Australia, Japan — covering time zones) + 2 paid staff (the Community Manager and a Senior Moderator).

## The four work streams

Of the ~12K daily posts, about **12.5% (~1,500/day) enter the moderation queue**.

| Stream | Volume/day | Time/case | Queue share |
|---|---|---|---|
| Routine spam / clear-violation removal | ~1,080 | ~30 sec | ~72% |
| Grey-zone case review | ~360 | ~5 min | ~24% |
| User dispute appeals | ~60 | ~8 min | ~4% |
| IP-claim resolution | ~3–5/wk | ~30 min + escalation | separate channel |

Total moderator effort ≈ 47 hours/day across the 10-person team; the team is at capacity.

## Tooling sketch

- **Discourse** (forum platform, self-hosted on AWS, REST APIs)
- **In-house gallery** (Rails app, custom; limited API surface)
- **Stripe** (premium memberships and gallery commissions)
- **Discord** (volunteer moderator coordination)
- **Google Sheets** (Community Manager's tracker)
- **Email** (IP-claim correspondence; legal record-keeping)

## Stakeholder

**Tomasz "Tom" Włodarczyk**, Community Manager (paid, Warsaw-based, ex-volunteer moderator promoted). Brief from the founder: "False positives are survivable; one viral false negative is existential."

## What to elicit

- What previous moderation incidents have shaped Tom's risk tolerance?
- Where do sub-forum-specific norms diverge from the global 14-page policy?
- How are IP claims actually triaged in practice — by whom, against what criteria?
- Where do volunteer moderators disagree, and what happens when they do?
- What sponsorship / commercial dynamics constrain content decisions in ways the policy doesn't acknowledge?

## Sample artefacts

### Artefact 4.1 — Grey-zone post

*Post in "Painting Critique" sub-forum, 18.10. Reported by 4 users.*

> **@greenwingmolar:** "Honestly mate, your highlights are gone, your edges are blurry, the freehand is wonky, and the basing looks like you used cat litter without thinking about colour. The OSL is the only thing saving this from being a beginner Reddit post. If you're entering this in Golden Demon you'll get DQ'd at the table. Fix the highlights first, then come back."

Reactions: 12 ❤️ / 6 😐 / 4 reported as "harsh / harassment"

**@knightmodeller_v2** (OP) replied 90 min later: "thanks, that's actually really useful. cat litter ouch lol. will redo highlights."

### Artefact 4.2 — Volunteer mod Discord thread

*#mod-decisions, Aki (Japan, painters sub) and Klaus (Germany, historical sub).*

> **Aki:** This @greenwingmolar critique post — 4 reports. Within painters norm or harassment?
> **Klaus:** I'd call it normal critique. The OP literally asked for help.
> **Aki:** Yeah but the painters sub has the "no critique without invitation" thing — but this is a critique thread so invitation is implicit. I think it's fine, want a second opinion.
> **Klaus:** That "no critique without invitation" is painters-sub-specific. Thread title is literally "help me figure out what's wrong" so OP invited it.
> **Aki:** OK closing as no action. Tom said before to be careful about harshness reports though, the 2024 thing.
> **Klaus:** That was the sponsor incident. Different. OP isn't a high-profile sculptor and the reply shows they took it well.
> **Aki:** Closing. Logging in Discourse as "no action — invited critique within sub norms."

### Artefact 4.3 — Tom's moderation patterns Google Sheet

*Shared with the senior moderator only; not in the volunteer Discord.*

| User / topic | Pattern | Action default | Notes |
|---|---|---|---|
| @sculpturedragon | Established sculptor; recurring IP claims | Tom personally reviews every IP claim | After 2024 incident, full review every time |
| @vortex_minis | Sponsor account; commercial-content posts | Tom personally reviews; do not auto-flag as commercial-spam | THE 2024 SPONSOR — never get this wrong |
| Painters sub | "No critique without invitation" | Apply norm; flag posts that critique uninvited | Not in global policy; sub-forum-specific |
| Historical sub | More permissive on historically-charged imagery | Don't apply global "controversial imagery" rule strictly | Flag to Tom if uncertain |
| Japanese painters sub | English-language critiques sometimes read harsher than intended | Soft-warning before any removal action | Aki has flagged this; we're learning |
| @vintage_kitbasher | IP claims credibility unclear; small sculptor | Standard escalation, no fast-track | Watch for retaliatory reports |
