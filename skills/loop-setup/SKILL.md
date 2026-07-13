---
name: loop-setup
description: "re:Harmoniz autonomous-loop wizard — one command from zero to a running loop: detects the scope, interviews you for the CONFIG choices, validates the experiment gate up front, writes .claude/loop.md, then starts the native /loop in the same invocation. Triggers: reharm loop setup, set up the autonomous loop, start the evolution loop, run the loop, 자율 루프 설정, 루프 설정, 루프 시작, 자율 모드 시작"
---

# reharm:loop-setup — Autonomous-Loop Wizard (setup → start, one command)

Turns the manual "copy `templates/loop.md`, fill CONFIG by hand, then run `/loop`" flow into one
interactive command. Everything mechanically derivable is derived; only real decisions are asked;
mistakes that would otherwise surface at tick N (`bad-scope`, `exec-blocked`) surface **now**; and
the loop is started in the same invocation — no second command.

This wizard is **manual and interactive by design**: the EVOLUTION.md §3/§4 override lives in the
loop.md it writes, not here. Autonomy begins only after the user has answered the interview and the
loop starts.

## Procedure

1. **Fast path.** If `<project>/.claude/loop.md` already exists AND its CONFIG block has no
   unfilled `«»` placeholders: diff its non-CONFIG body against
   `${CLAUDE_SKILL_DIR}/../../templates/loop.md`.
   - Body matches the current template → print the current CONFIG and ask (AskUserQuestion) —
     *start with this config* / *re-run the wizard* / *stop*. Start → go to step 7.
   - Body differs (a copy from an older plugin) → say so, and recommend **refresh** as the default:
     rewrite the file from the current template keeping the shown CONFIG values, then go to step 7.
     The ledger lives outside this file, so a refreshed loop resumes where the old one stopped.
     Offer *start as-is* and *stop* as the alternatives.
2. **Detect the scope.** Scan the current project (depth ≤ 3, skip hidden dirs except `.claude`)
   for directories containing both `.raw/` and `wiki/`. Exactly one → confirm it; several → ask
   which (plus which, if any, is the `SIBLING_SCOPE` donor); none → stop and point to
   `reharm:root` (there is nothing to evolve yet).
3. **Derive, don't ask.** Compute and display — but do not question — the mechanical fields:
   - `LEDGER` = `<project>/.reharm-loop/<scope-name>.jsonl` (outside the scope, per EVOLUTION.md §8)
   - `MAX_TARGETS` = 2 (the auditability default)
   - `STOP_ON` = reseed, change-strategy
4. **Interview** (one AskUserQuestion call, 4 questions):
   - `MAX_ITERS` — bounded 12 (recommended for a first run) / bounded, custom N / `inf`
   - `RUN_EXPERIMENTS` — `no` (recommended until the scope has hardened claims) / `yes`
   - `SIBLING_SCOPE` — `none` / one of the other detected scopes
   - Invocation mode — dynamic, self-paced (recommended: ending is fail-safe) / fixed interval
     (ask the cadence, e.g. `2h`; warn it ends only via the loop's own CronDelete)
5. **Experiment gate pre-check** (only when `RUN_EXPERIMENTS = yes`). Read the scope `CLAUDE.md`:
   - Workspace path (§2 Metadata) missing or nonexistent → warn that every experiment tick will
     stop at design + `exec-blocked`, and offer to flip `RUN_EXPERIMENTS` back to `no`.
   - Workspace exists, runner entry (§6 Toggles) set → report the external-runner lane.
   - Workspace exists, runner entry blank → report that the loop will use its **DEFAULT RUNNER**
     (it operationalizes each pre-registration into `<workspace>/.reharm-runner/` itself — see the
     template's ACT step b). An empty workspace is fine.
   - Then ask `EXP_TIMEOUT` (second AskUserQuestion: e.g. `2h` / `8h` / `none`).
6. **Write `.claude/loop.md`.** Copy `${CLAUDE_SKILL_DIR}/../../templates/loop.md` **verbatim**,
   replacing only the CONFIG `«»` values with the answers. Never edit any other section — the rest
   is the contract, and re-running this wizard after a plugin upgrade is how template fixes
   propagate. Before overwriting an existing file, show the CONFIG diff and require explicit
   confirmation; if `<LEDGER>.lock` exists and is younger than ~1h, stop — a loop may be mid-flight.
7. **Start the loop — same invocation, no second command.** Invoke the native loop via the Skill
   tool: dynamic → `Skill(skill: "loop")` with empty args; interval → `Skill(skill: "loop",
   args: "<cadence>")` (the cadence ONLY — any prompt text would bypass loop.md). Then follow the
   instructions it returns: they schedule the pacing and run the first tick immediately.
8. **Smoke-check the first tick.** Confirm (a) the tick actually worked from `.claude/loop.md`
   (its CONFIG/LEDGER visibly drove the turn) and (b) the next firing is armed — a ScheduleWakeup
   (dynamic) or the recurring cron job (interval). If loop.md was ignored or no next firing exists,
   the build's loop feature gates are off — say so plainly and stop; do not fake a loop by hand.
   Close by telling the user: keep the session open and the machine awake; a dynamic loop stops with
   `Esc`, an interval loop is cancelled with `CronDelete` (`Esc` only skips the current tick);
   mid-run compaction is safe, `/clear` kills it.

## Constraints

- **CONFIG only.** The wizard fills `«»` placeholders; every other line of loop.md ships verbatim
  from the plugin template.
- **Never overwrite silently.** An existing `.claude/loop.md` is replaced only after showing the
  CONFIG diff and getting explicit confirmation; a fresh `<LEDGER>.lock` stops the wizard.
- **Validate at the boundary.** A scope without `.raw/` + `wiki/` is rejected here, not at tick 1;
  an impossible experiment gate is surfaced here, not at iteration N.
- **One scope per loop.** If the user wants a second loop, it must target a different scope
  (the ledger lock enforces this at runtime anyway).
- **This skill decides nothing about knowledge.** It writes configuration and starts the loop;
  all target/verdict/seed decisions remain the loop template's documented override.
