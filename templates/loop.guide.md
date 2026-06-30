# re:Harmoniz Autonomous Loop — Guide

A companion to [`templates/loop.md`](loop.md): what the autonomous loop is, why it
exists, how to verify it runs the way it claims, **where it actually runs**, and the
exact commands to start it. The template file itself is the terse contract; this is the
long-form explanation. (Korean: [`loop.guide.ko.md`](loop.guide.ko.md).)

---

## What it is

The 0.7.0 release adds **one file** — `templates/loop.md`. Copy it to a research
project's `.claude/loop.md`, and whenever you run `/loop` from that folder, Claude Code
re-feeds the file and advances the evolution loop **one step at a time**.

Each step is three moves:

1. **JUDGE** — `reharm:pushing` inspects the scope (frontier scores, lint health,
   maturity census, last stagnation verdict) **read-only** and names the next action.
2. **ACT** — exactly one recommended skill runs: `root` / `reharmonization` / `critique`
   / `modal-interchange` / `experiment-design`. The main session stands in for every
   approval the skill would normally route to you.
3. **RECORD** — one JSONL line is appended to the loop ledger.

It is **not a 7th skill**. It is a project-local template that *drives* the existing six
skills through the native `/loop` command. The plugin's skill set is unchanged.

---

## Why it exists

re:Harmoniz's six skills are all **"nothing is auto-decided"** by design
(`EVOLUTION.md` §3/§4): you pick the targets, you adjudicate the verdicts. That manual
discipline is the constitution that protects knowledge quality.

But unattended operation is sometimes what you want (overnight batches, long-horizon
accumulation). So this template **deliberately gives that up** — and isolates the
override in a **project-local file, not a plugin skill**, so the plugin core stays
clean. The result: the six skills still obey the constitution, and the override only
runs because *you* copied the file in. Everything it does is reversible
(`deprecate` = a status flip, never a delete) and double-logged (`E####.md` + the
ledger) for after-the-fact audit.

---

## The cycle — one firing, 6 + 1 steps

Run exactly once per firing, in this order:

| # | Step | What happens |
|---|------|--------------|
| 00 | **LOCK** | If `<ledger>.lock` exists, another iteration is mid-flight → `STOP("overlap")`. Otherwise create it. |
| 01 | **LOAD** | Read the ledger tail: `N` = completed iterations. If `MAX_ITERS ≠ inf` and `N ≥ MAX_ITERS` → `STOP("count-reached")`. |
| 02 | **JUDGE** | Run `/reharm:pushing`. Take the next action `R`, its evidence, and the latest stagnation verdict. `R = current` → `STOP("nothing-pending")`; verdict ∈ `STOP_ON` → `STOP("stagnation:…")`. |
| 03 | **ACT** | Perform **exactly one** action for `R`, auto-deciding every choice per the DECISION POLICY. |
| 04 | **RECORD** | Append one JSONL line to the ledger. This is the loop's **only** state. |
| 05 | **UNLOCK** | Remove `<ledger>.lock`. |
| 06 | **NEXT ↺** | Schedule the next wakeup (ScheduleWakeup, 1200–1800 s), or **omit it to end** — that is how the run self-terminates at `MAX_ITERS` or a stop reason. |

---

## Does it run as intended?

The loop's reliability rests on one thing: the way it's written has to match the way
the native `/loop` command *actually* behaves. It does — point by point:

| What native `/loop` actually does | How `loop.md` is designed for it |
|-----------------------------------|----------------------------------|
| Bare `/loop` reads `.claude/loop.md`. | The template is copied to exactly that path. |
| It re-feeds the file **verbatim every firing** — it does not rely on prior chat memory. | State is recovered from the **ledger tail** (`N` = completed iterations), not from the conversation. The file is self-contained. |
| `dynamic` mode self-paces via a scheduled wakeup, and **omitting the wakeup ends the loop**. | Step 6 (`dynamic`): with no stop reason, re-schedule the next wakeup with the same `/loop` input; with a stop reason, omit it → end. This is how `MAX_ITERS` and stop conditions are enforced. |
| The dynamic wakeup delay is bounded (≈ 1 min – 1 h) and the prompt cache has a ~5-minute window. | The template picks **1200–1800 s** — past the cache window to keep cost sane, and it does not poll. |
| A fixed-interval `/loop` (`/loop 6h`) fires on a clock **the prompt cannot stop**, and `.claude/loop.md` is the default prompt for **bare** `/loop` anyway. | So the template is **bare-`/loop`-only** — never pass an interval. Self-pacing (which enforces `MAX_ITERS` / `STOP_ON`) works only for a dynamic `/loop`; a fixed interval would ignore them and run until `Esc` / 7-day expiry. |
| Two instances could run the same file at once. | Step 0 **LOCK** rejects a second concurrent run with `STOP("overlap")`. One loop per scope. |

---

## Execution model — where it runs, and what must stay awake

**This is the most important operational fact, and the easiest to get wrong.**

Claude Code's `/loop` is **local and session-scoped** — *not* an OS-level cron daemon
and *not* a cloud job. Straight from the docs:

> "Tasks only fire while Claude Code is running and idle. Closing the terminal or
> letting the session exit stops them firing."

Mechanically, the scheduler lives in the live CLI process's event loop — it checks every
second for a due task and fires it *between turns* (never mid-response). So "idle" means
*alive and waiting for input*, **not** asleep: if the terminal closes, the process exits,
or the machine sleeps and the OS suspends the process, nothing fires.

So for this template (it runs as a bare, dynamic `/loop`):

- The **Claude Code session must stay open** (terminal or `claude.ai/code` session). Close it and the loop stops.
- The **machine must stay powered on and awake**. The loop runs inside the local CLI process; a closed/sleeping laptop does not fire it.
- Recurring `/loop` tasks **auto-expire after 7 days**. `claude --resume` / `--continue` restores unexpired tasks; a fresh conversation clears them.

So even a self-paced run only advances while the machine is awake — it is **not** the
always-on guarantee a system `cron` or a cloud Routine gives.

### If you need a laptop-closed, unattended run

Use a different mechanism — **not this `/loop` template**:

| Mechanism | Session open? | Machine awake? | Runs on | Min interval | Notes |
|-----------|---------------|----------------|---------|--------------|-------|
| **`/loop`** (this template) | **Required** | **Required** | Local CLI process | ~1 min | 7-day expiry; this is what the template targets |
| **Routines** (`/schedule`) | Not required | **Not required** | Anthropic cloud | 1 hour | Survives a closed laptop; fully autonomous (no prompts); research preview |
| **Desktop scheduled tasks** | Not required | Required | Local machine | 1 min | Needs the Desktop app + an awake machine |
| **GitHub Actions** (`schedule:`) | Not required | Not required | CI infrastructure | per-cron | No local machine at all; runs in your repo's CI |

For a genuine nightly-while-closed loop, the right tool is **cloud Routines**, which run
on Anthropic-managed infrastructure. Note that this template is a `/loop` file, so it
does **not** itself run as a Routine — porting the loop logic into a Routine prompt is a
separate exercise and currently out of scope for the template.

(Requires Claude Code with `/schedule` support — v2.1.81+. Routines are a research
preview; limits and the API may change. Sources:
[scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks.md),
[routines](https://code.claude.com/docs/en/routines.md).)

---

## Safeguards

Autonomy without an undo button is reckless; the contract bakes in four:

- **Per-scope lock** — `<ledger>.lock` allows only one loop per scope; a concurrent firing exits with `STOP("overlap")`.
- **External ledger** — the ledger lives **outside** the scope at `<project>/.reharm-loop/`. `EVOLUTION.md` §8 forbids in-scope state files, and keeping it out also means `wiki-lint` never flags it as an orphan.
- **Reversible deprecate** — discarding a node is a **status flip**, never a delete; the loop never raises a node's generation.
- **Double logging** — the skill writes `E####.md` *and* the loop appends a ledger line, so an unattended run can be retraced step by step.

---

## Experiment execution — the 3-AND gate

`experiment-design` always **designs** (pre-registers a `planned` node + a `## Handoff`
block). Running the *real* experiment is gated on three conditions, all required:

```
RUN_EXPERIMENTS = yes
  AND  a runner entry point is set   (node  runner:  OR scope CLAUDE.md §6 Toggles)
  AND  the code-workspace path exists (scope CLAUDE.md §2 / §12)
```

If any one is missing, the loop **stops after DESIGN + handoff** and records
`gate = "exec-blocked"`.

**Launching is fire-and-return.** The loop launches the run in the background
(`run_in_background`, or submits it to the external runner) and **does not wait** — blocking
would hold the per-scope lock for the entire run and freeze every other iteration. It flips the
node to `status: running`, records the launch time, and ends the iteration. The result lands
asynchronously in `.raw/experiments-results/`; the loop never judges the raw result — a later
`reharmonization` Phase C imports it against the pre-registered criterion and flips the node to
`imported` / `abandoned`.

**Polling.** Every JUDGE first checks for a `status: running` node, so result collection rides
along with normal evolution work — the experiment runs in parallel and usually needs no dedicated
poll (the normal 1200–1800 s cadence). Only when there is nothing else to do does the loop enter a
short poll: **~240 s** for a short/unknown run (inside the 5-min cache window), or **1200 s+** for a
known-long one; **never 300 s**. One experiment at a time. If a run exceeds `EXP_TIMEOUT` with no
result, the node is set `abandoned` and the loop stops with `exec-blocked-needs-human`.

---

## Dynamic-only — and why not cron

This template runs as a **bare `/loop`** (dynamic, self-paced). It deliberately does **not**
support a fixed-interval / cron invocation, because:

- The loop enforces `MAX_ITERS` / `STOP_ON` by choosing whether to schedule its own next wakeup —
  and that self-pacing works **only** for a bare `/loop`.
- A fixed-interval `/loop` (`/loop 6h`) hands pacing to a scheduler the prompt **cannot stop**; it
  would ignore `MAX_ITERS` / `STOP_ON` and run until `Esc` or the 7-day expiry.
- `.claude/loop.md` is the default prompt for bare `/loop` regardless.

So there is **no `MODE` to set and no interval to pass** — just `/loop`. If you need a fixed
wall-clock schedule (e.g. nightly) or a run that survives a closed laptop, that is a job for cloud
**Routines** (`/schedule`), not this template — see Execution model above.

---

## How to use

```bash
# 1. Copy the template into your research project (where the scope lives)
cp templates/loop.md  /path/to/your-project/.claude/loop.md
```

```text
# 2. Fill in the CONFIG block, then leave it fixed.
SCOPE:           /abs/path/to/scope         # must contain .raw/ + wiki/
MAX_ITERS:       12                          # N | inf
RUN_EXPERIMENTS: no                          # yes runs real code, gated above
SIBLING_SCOPE:   none                        # donor scope for modal-interchange
STOP_ON:         reseed, change-strategy
LEDGER:          /abs/your-project/.reharm-loop/scope.jsonl   # OUTSIDE the scope
```

```bash
# 3. From the project root, bare /loop reads .claude/loop.md
/loop                     # the only invocation — dynamic, bounded by MAX_ITERS / self-terminating
```

One loop per scope (the lock enforces it). Stop any time with `Esc`. Keep the session
open and the machine awake for the duration — or switch to cloud Routines for a
laptop-closed run.

---

## Limits & gotchas

- **Not laptop-closed.** `/loop` needs the session open and the machine awake. See Execution model.
- **7-day expiry** on recurring tasks; `--resume` restores unexpired ones.
- **Bare `/loop` only — don't pass an interval.** A fixed-interval `/loop` can't stop itself (runs until `Esc` / 7-day expiry) and ignores `MAX_ITERS` / `STOP_ON`; self-pacing needs a dynamic `/loop`.
- **One scope per loop.** The lock enforces it; point a second loop at a different scope.
- **Experiments stay gated.** Without all three gate conditions, the loop stops at design + handoff — by design.
