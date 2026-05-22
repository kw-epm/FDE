# Build-Loop Exam — Pavel's 4a (Request Intake Agent)

Cold-session test. Goal: run Pavel's `spec.md` through Claude Code under exam conditions, capture what happens, write the reflection later.

---

## Protocol

1. **Open a new terminal.** Do not reuse the one with the main FDE session.
2. `cd /mnt/c/xyh/fde/w4/build_attempt_1`
3. **Start a fresh Claude Code session:** `claude`
4. **Paste the kickoff prompt** (below) into the fresh session.
5. **Start a 30-minute timer** the moment you press Enter on the prompt.
6. **Watch.** Take rough notes in `build-notes.md` as it happens — what it asked, what it built, what it skipped silently, what bugs it noticed (or didn't).
7. **Stop at 30 min.** Even if the build is mid-step. Exam conditions.
8. **Save the terminal transcript** to `build-transcript.txt` (copy-paste the whole session, or pipe `claude` through `tee`).
9. **Sleep.**

The reflection writeup happens tomorrow, in the main FDE session, from the notes + the transcript.

---

## Kickoff prompt (paste exactly)

```
Read spec.md and build the agent it describes. You have 30 minutes.

When you finish (or hit the time limit), summarise:
- what you built
- what you couldn't build, and why
- any questions you would have asked the spec author before starting
- any places in the spec where you had to choose between two interpretations
```

That's the whole prompt. Do not add context, do not coach Claude Code, do not answer its mid-build questions unless it physically halts and waits for you. (If it asks "should I use Postgres or SQLite?" let it pick. The exam tests organic behaviour.)

---

## What to note during the run (4 categories from Gate 3 D#9)

Use the headings in `build-notes.md`. One line per event, with a rough timestamp (just "05 min", "12 min", etc — no need to be precise).

**a. What Claude Code asked clarifying questions about.**
The places it explicitly stopped and asked. Each question is a sign of spec ambiguity it recognised.

**b. What Claude Code said it couldn't build.**
Anything it explicitly punted on. "I'll skip X for now." Whether it noted the reason matters.

**c. What Claude Code silently added or chose without asking.**
This is the most important category for the reflection. Did it pick a confidence formula when the spec gives three? Did it pick the proximity formula in km or miles? Did it invent timezones the spec doesn't specify? Did it fix the SUSPENDED-style bug without flagging? These are the silent decisions — they will not appear in any question; you have to spot them in what it wrote.

**d. What Claude Code built that matches the spec intent.**
The clean wins. Useful for the reflection so you can name what your peer review correctly judged as buildable.

---

## After the timer

- Save notes (`build-notes.md`).
- Save transcript (`build-transcript.txt`).
- Save any files Claude Code wrote (they'll be in this directory automatically).
- Close the terminal. Do not iterate. Exam over.
- Sleep.

---

## What we do tomorrow

Bring the notes + transcript back to the main FDE session. We write `w4/07-build-loop-reflection.md` together — 1 page, structured as:

1. What I built / what I didn't (2–3 sentences)
2. Issues my peer review caught that the build confirmed
3. Issues my peer review missed (false negatives — the embarrassing column)
4. Issues my peer review flagged that the build didn't trigger (false positives — also important)
5. What I would change in Pavel's spec if I had another 30 minutes

The reflection is graded on **diagnosis quality, not code correctness**. Honest naming of misses scores higher than hiding them.
