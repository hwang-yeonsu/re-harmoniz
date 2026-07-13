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
   / `modal-interchange` / `experiment-design` / `ensemble`. The main session stands in
   for every approval the skill would normally route to you. (The one recommendation it
   never takes: a §13 deep-research escalation — manual-only by design.)
3. **RECORD** — one JSONL line is appended to the loop ledger.

It is **not an extra skill**. It is a project-local template that *drives* the existing
seven skills through the native `/loop` command. The plugin's skill set is unchanged.

---

## Why it exists

re:Harmoniz's seven skills are all **"nothing is auto-decided"** by design
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
| 06 | **NEXT ↺** | Dynamic mode: schedule the next wakeup (ScheduleWakeup, prompt `<<loop.md-dynamic>>`, 1200–1800 s), or **omit it to end**. Interval mode: do nothing to continue (the cron re-fires), or **CronDelete the loop's job to end**. Either way, this is how the run self-terminates at `MAX_ITERS` or a stop reason. |

---

## Does it run as intended?

The loop's reliability rests on one thing: the way it's written has to match the way
the native `/loop` command *actually* behaves. It does — point by point:

| What native `/loop` actually does | How `loop.md` is designed for it |
|-----------------------------------|----------------------------------|
| `/loop` with no prompt — bare **or** interval-only (`/loop 2h`) — reads `.claude/loop.md`. | The template is copied to exactly that path. |
| It re-reads the file **every firing** (full text on the first fire / after an edit / post-compact, else a short reminder while the full text stays in context) — it does not rely on prior chat memory. | State is recovered from the **ledger tail** (`N` = completed iterations), not from the conversation. The file is self-contained. |
| `dynamic` mode self-paces via a scheduled wakeup, and **omitting the wakeup ends the loop**. | Step 6 (`dynamic`): with no stop reason, re-arm the wakeup with `prompt = <<loop.md-dynamic>>` (the sentinel the runtime re-expands to this file — not the string "/loop"); with a stop reason, omit it → end. This is how `MAX_ITERS` and stop conditions are enforced. |
| The dynamic wakeup delay is bounded (≈ 1 min – 1 h) and the prompt cache has a ~5-minute window. | The template picks **1200–1800 s** — past the cache window to keep cost sane, and it does not poll. |
| An **interval-only** `/loop 2h` also reads `.claude/loop.md`: it schedules a recurring cron whose prompt is the `<<loop.md>>` sentinel, re-expanded from disk each fire — but the cron keeps firing until the job is deleted. | So interval mode is **supported**: step 6 ends the run by finding the loop's own cron job (CronList) and **CronDelete**-ing it. Dynamic stays the default because its ending is fail-safe (just don't re-arm). Never pass a *prompt* with the interval — `/loop 2h <prompt>` bypasses loop.md entirely. |
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

So for this template (it runs as a bare `/loop`, or an interval-only `/loop 2h`):

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

### Compacting mid-run is safe (`/clear` is not)

A long run **will** hit context compaction, and the loop is built for it:

- The pending wakeup / cron job lives in the **CLI process**, not the conversation
  context — compaction (auto, or a manual `/compact` typed between ticks) does not
  touch the schedule.
- The runtime resets its "loop.md already delivered" marker on compaction, so the
  **next firing re-feeds the full loop.md text** instead of the short reminder.
- The loop's state was never in the chat to begin with — every firing recovers `N`
  and the last decision from the **ledger tail**.

So nothing special is needed: let auto-compact happen, or `/compact` manually while
the loop is idle between ticks, and the next tick continues where the ledger says.
Auto-compact is **on by default** (`autoCompactEnabled` defaults to true) and runs
inside each turn's query pipeline — a tick that crosses the context threshold compacts
itself *before* calling the model, with nobody at the keyboard. Just verify it hasn't
been turned off (`/config` → Auto-compact; no `DISABLE_AUTO_COMPACT` in the
environment). Do **not** try to force a compact every tick: compaction is lossy
summarization, and it would invalidate the cached prompt prefix the loop's cost model
leans on — the threshold trigger is the right cadence.
What is **not** safe is `/clear` (or starting a fresh conversation): that clears the
scheduled tasks themselves and the loop dies silently — restart it with `/loop`.

---

## Safeguards

Autonomy without an undo button is reckless; the contract bakes in six:

- **Per-scope lock** — `<ledger>.lock` (holding the iteration's start ts) allows only one loop per scope; a concurrent firing exits with `STOP("overlap")`. Every stop unlocks before ending, and a lock older than ~1h is treated as a dead iteration and reclaimed — so one crashed tick can't deadlock the scope.
- **External ledger** — the ledger lives **outside** the scope at `<project>/.reharm-loop/`. `EVOLUTION.md` §8 forbids in-scope state files, and keeping it out also means `wiki-lint` never flags it as an orphan.
- **Reversible deprecate** — discarding a node is a **status flip**, never a delete; the loop never raises a node's generation.
- **Double logging** — the skill writes `E####.md` *and* the loop appends a ledger line (including a `targets` field naming the nodes that iteration touched), so an unattended run can be retraced step by step.
- **Target cap** — `MAX_TARGETS` (default 2) bounds how many nodes one unattended reharmonization iteration may auto-pick in Phase B; excess candidates simply wait for the next tick. Small iterations stay auditable.
- **Manual-only rows stay manual** — the deep-research escalation recommendation (`EVOLUTION.md` §13) is never auto-taken: the loop skips that cascade row and moves to the next candidate. Escalation is a human decision by design.

---

## Experiment execution — one switch, two prerequisites

`experiment-design` always **designs** (pre-registers a `planned` node + a `## Handoff`
block). Whether the *real* experiment then launches comes down to **one switch you set**
— `RUN_EXPERIMENTS` in CONFIG — plus **two prerequisites the loop checks automatically**
at launch time (they are facts about your scope, not decisions):

```
you set        RUN_EXPERIMENTS = yes            ← the only knob; no = never runs code
auto-checked   the code-workspace path exists   (scope CLAUDE.md §2 / §12)
auto-checked   a runner is available            (entry point set — node  runner:  OR scope
                                                 CLAUDE.md §6 — else the DEFAULT RUNNER below)
```

If the switch is off or the workspace is missing, the loop **stops after DESIGN +
handoff** and records `gate = "exec-blocked"`: with `RUN_EXPERIMENTS: no` the loop
simply never runs code.

**Default runner — an empty workspace still works.** The manual protocol records the
runner entry point explicitly and never infers it (§12); the scope template even says
*"leave blank to decide per experiment"*. Under an unattended loop that blank would
mean a guaranteed `exec-blocked`, so the template adds a loop-only fallback: when the
switch is on and the workspace path exists but no entry point is set, the loop
**operationalizes the pre-registration itself** — it writes a self-contained script to
`<workspace>/.reharm-runner/<node-stem>/`, records that script path in the node's
`runner:` **before** launching (so §12's audit rule — recorded, never inferred — still
holds), and fires it in the background. The report lands in `.raw/experiments-results/`
and Phase C judges it against the pre-registered criterion, exactly as with an external
runner. If the goal needs things the workspace cannot offer (data, hardware,
credentials, external services), the loop does not force it — `exec-blocked` as before.

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
known-long one; **never 300 s**. (The short poll is a dynamic-mode move — in interval mode the
cadence is fixed, so a running experiment is simply re-checked on the next tick.) One experiment at
a time. If a run exceeds `EXP_TIMEOUT` with no result, the node is set `abandoned` and the loop
stops with `exec-blocked-needs-human`.

---

## Two invocation modes — dynamic (default) vs interval

The template runs under either `/loop` form — both re-read `.claude/loop.md` every firing,
and both enforce `MAX_ITERS` / `STOP_ON`. They differ in **who paces** and **how the run ends**:

| | **Dynamic** — bare `/loop` (recommended) | **Interval** — `/loop 2h` (interval only) |
|---|---|---|
| Pacing | The loop picks each delay (1200–1800 s normally, short poll while experiment-waiting) | Fixed cadence: exactly one tick per interval |
| How it ends | **Fail-safe**: just don't re-arm the next wakeup — forgetting to act ends the loop | **Fail-open**: the loop must CronDelete its own cron job; a missed delete keeps firing no-op `STOP` ticks until you CronDelete the job / 7-day expiry (`Esc` only skips the current tick — it does not remove the cron) |
| Prompt to the runtime | `ScheduleWakeup` with the `<<loop.md-dynamic>>` sentinel | A recurring cron with the `<<loop.md>>` sentinel, created at invocation |
| Feature gates it rides | loop.md loading **and** the dynamic wakeup (two flags) | loop.md loading only (one flag) |

The loop tells the modes apart from the firing's own text — a dynamic tick says "re-arm
ScheduleWakeup", an interval tick says "the recurring cron fires the next tick automatically" —
so there is still **no `MODE` field to configure**; the invocation is the single source of truth.

Two hard rules for interval mode: pass the **interval only** (`/loop 2h <prompt>` would use the
prompt *instead of* loop.md), and accept that a stop reason takes effect by an explicit
CronDelete. Dynamic remains the default recommendation because its ending needs no action at all.

If you need a run that survives a closed laptop, neither mode helps — that is a job for cloud
**Routines** (`/schedule`), not this template; see Execution model above.

---

## How to use

The one-command path: run **`/reharm:loop-setup`** from the research project root. It detects the
scope, interviews you for the CONFIG choices, validates the experiment gate up front, writes
`.claude/loop.md` from this template, and starts the native `/loop` in the same invocation —
**there is nothing to hand-copy**; the `cp` + fill-CONFIG steps below are the manual *alternative*,
not a prerequisite.

Either way, know what the file *is*: `.claude/loop.md` belongs to the **research project** (the
plugin never installs or touches it — the override stays opt-in), and it is a **point-in-time copy**
of this template. Installing or upgrading the plugin does not update it. After an upgrade, re-run
`/reharm:loop-setup`: it shows your existing CONFIG, keeps it on confirmation, and rewrites the rest
of the file from the new template. The ledger is not part of the file, so the refreshed loop resumes
exactly where the old one stopped — and your scope needs **no migration** for template changes
(nodes, ledger format, lock, and lint rules are untouched).

The manual equivalent, step by step:

```bash
# 1. Copy the template into your research project (where the scope lives)
cp templates/loop.md  /path/to/your-project/.claude/loop.md
```

```text
# 2. Fill in the CONFIG block, then leave it fixed.
SCOPE:           /abs/path/to/scope         # must contain .raw/ + wiki/
MAX_ITERS:       12                          # N | inf
MAX_TARGETS:     2                           # Phase B auto-pick cap per iteration
RUN_EXPERIMENTS: no                          # yes runs real code, gated above
SIBLING_SCOPE:   none                        # donor scope for modal-interchange
STOP_ON:         reseed, change-strategy
LEDGER:          /abs/your-project/.reharm-loop/scope.jsonl   # OUTSIDE the scope
```

```bash
# 3. From the project root, /loop (bare or interval-only) reads .claude/loop.md
/loop                     # recommended — dynamic, bounded by MAX_ITERS / self-terminating
/loop 2h                  # supported — fixed cadence; ends itself by CronDeleting its own job
```

One loop per scope (the lock enforces it). Stop a dynamic loop any time with `Esc`; an interval loop
must be cancelled with `CronDelete` (`Esc` only skips the current tick, the cron re-fires). Keep the session
open and the machine awake for the duration — or switch to cloud Routines for a
laptop-closed run. Compacting mid-run is fine (see above); `/clear` kills the loop.

---

## Limits & gotchas

- **Feature-gated — smoke-test first.** What this template rides on is gated by your Claude Code build (rollout flags, not a fixed version): `/loop` (bare or interval-only) reading `.claude/loop.md`, and — dynamic mode only — the self-pacing wakeup (`ScheduleWakeup`). If a flag is off, `/loop` ignores loop.md, or a dynamic run does a single tick and stops (the wakeup silently no-ops) — `MAX_ITERS` never engages. Before trusting an overnight run, do a one-tick smoke test: run `/loop`, confirm the first turn actually loads this file (CONFIG + LEDGER) **and** that it arms a next wakeup (dynamic) or created the recurring cron job (interval). Confirmed working on Claude Code 2.1.197; interval-mode loop.md loading (the `<<loop.md>>` cron sentinel) verified on 2.1.207.
- **Not laptop-closed.** `/loop` needs the session open and the machine awake. See Execution model.
- **7-day expiry** on recurring tasks; `--resume` restores unexpired ones.
- **Interval mode: interval ONLY, and ending is on the loop.** `/loop 2h <prompt>` bypasses loop.md (the prompt wins), and a stop reason ends the run only through the loop's own CronDelete — if that call is missed/denied, no-op STOP ticks keep firing until you CronDelete the job / the 7-day expiry (`Esc` only skips the current tick, it does not remove the cron). Dynamic mode has neither trap.
- **Compact ≠ clear.** `/compact` (and auto-compact) mid-run is safe; `/clear` or a fresh conversation silently kills the schedule.
- **One scope per loop.** The lock enforces it; point a second loop at a different scope.
- **Experiments stay gated.** With `RUN_EXPERIMENTS: no` — or `yes` but a missing runner/workspace prerequisite — the loop stops at design + handoff — by design.
