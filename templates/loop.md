<!-- templates/loop.md — copy to  <your research project>/.claude/loop.md  and fill in CONFIG. -->
<!-- re:Harmoniz AUTONOMOUS evolution loop. Native /loop re-reads this file each firing (full text on the -->
<!-- first fire / after an edit / post-compact, else a short reminder while the full text persists in -->
<!-- context), so it must stay self-contained and recover its state from the LEDGER, not from chat memory. -->
<!-- It runs the existing /reharm:* skills; it is NOT a plugin skill itself. Invocation is at the bottom. -->
<!-- MODES: bare /loop (dynamic, self-paced — RECOMMENDED) or /loop <interval> (fixed cadence — supported; -->
<!-- ends itself via CronDelete). Never add a prompt after the interval — a prompt bypasses this file. -->
<!-- For a schedule that must survive a closed laptop use Routines, not /loop. -->

# re:Harmoniz Autonomous Evolution Loop — one iteration

## ⚠️ Contract override (read once)
This loop DELIBERATELY overrides the protocol's "nothing is auto-decided" rule
(EVOLUTION.md §3/§4). The main session acts with the user's delegated authority and
auto-decides every target / verdict / seed. It lives here — in your project's
`.claude/loop.md`, outside the `reharm` plugin — so the override stays out of the
plugin's core. Everything it does is reversible (deprecate = status flip, never delete)
and double-logged (`E####.md` + the loop LEDGER) for after-the-fact audit.

## CONFIG — fill in, then leave fixed
- SCOPE:           «absolute path to the scope (must contain .raw/ + wiki/)»
- MAX_ITERS:       «N | inf»          ← enforced by step 6 NEXT in both modes; state is in the LEDGER
- MAX_TARGETS:     «N, default 2»     ← Phase B auto-pick cap per iteration (reharmonization only)
- RUN_EXPERIMENTS: «no | yes»         ← the only experiment switch you set: no = design + handoff only,
                                        never runs code; yes = may LAUNCH real code (fire-and-return,
                                        then polled) once the GATE's auto-checks pass (ACT step b) —
                                        the launch spawns the runner recorded on the node as an isolated
                                        background sub-agent (default: the plugin's runner-worker doc,
                                        recorded by experiment-design; see ACT step b)
- EXP_TIMEOUT:     «duration | none»  ← a running experiment older than this → abandoned (no infinite wait)
- SIBLING_SCOPE:   «absolute path | none»   ← donor scope for modal-interchange
- STOP_ON:         reseed, change-strategy   ← stagnation verdicts that halt the loop
- LEDGER:          «<project>/.reharm-loop/<scope-name>.jsonl»   ← OUTSIDE the scope (EVOLUTION.md §8)

## DECISION POLICY — how the main session stands in for the user
- ACTIVE DECISION         : read SCOPE/CLAUDE.md `### Goal & Open Decisions` (EVOLUTION.md §1) EVERY
                            tick. Zero open decisions → STOP("no-decisions"): the loop must never
                            author, settle, or supersede a decision, and with none open it has nothing
                            to steer by. `settled` and `superseded` rows are NOT open — read the lint
                            `decisions.open` list, never the row count.
                            One open → that is the active decision. Several → pick the one CLOSEST TO
                            ANSWERABLE (most serving nodes at hardened-or-above; tie → lowest ID), so
                            value lands soonest. Record the ID in the ledger and in E####.md.
- pushing recommendation  : take the cascade first-match as-is (already deterministic) — EXCEPT two rows:
                            · "declare the goal" (row 2) → STOP("no-decisions"); writing that block is
                              the owner's call, not the loop's.
                            · deep-research escalation (§13, manual-only) → NEVER auto-escalate; skip
                              the row and take pushing's next secondary candidate (or current).
- reharmonization Phase B : auto-pick frontier-top + past-cadence nodes WITHIN the active decision
                            (`boundary-score.py --serves <ID>`; no user-named topic), CAPPED at
                            MAX_TARGETS per iteration — excess candidates wait for the next tick (an
                            unattended session must stay small enough to audit); record the picks and
                            rationale in E####.md "Decision & Targets".
- prune sweep (Phase C)   : auto-apply ONLY the unambiguous case — a node whose every served decision
                            is `settled`, or whose branch a design decision absorbed this tick
                            collapsed. Every auto-prune writes its restore point: append
                            `Pruned from <status>: <reason> (YYYY-MM-DD)` to the body BEFORE flipping
                            `status: pruned` (EVOLUTION.md §3) — a prune the human cannot undo is not
                            a prune the loop is allowed to make.
                            NEVER auto-prune two kinds of node:
                            · `unassigned` (lint `unassigned_claims`) — a missing `serves:` is usually
                              a binding gap, not a dead branch; pruning it hides work rather than
                              shedding it.
                            · `stale` (lint `stale_serves_target`) — bound to a `superseded` decision,
                              i.e. a question that was REPLACED, not answered. Its successor is a
                              re-binding judgement, and picking successors is the owner's call.
                            File both in SCOPE/wiki/questions/ as one "needs binding" entry for the
                            human. Log the counts in the ledger (`pruned`, `needs_binding`).
- reharmonization Phase D : depth per EVOLUTION.md §5.1 — load-bearing for the active decision → all
                            3 lenses (≥2/3 must survive); serves it but not load-bearing → 1 lens by
                            evidence_class; bears on no open decision → do NOT judge, report as a
                            prune candidate. Refuters stay ISOLATED sub-agents (refuter.md; no mutation
                            narrative, and never told their depth); refute when unsure. Re-judge after
                            absorbing a partial collapse AT MOST ONCE per node per tick (§5.3) — then
                            file the residue as a question and move on.
- critique adjudication   : adjudicate by evidence — clear support → adopt/reject; a contradiction
                            pair → resolve by evidence weight (absorb into ## Objections & Limits);
                            both sides weak → needs-research (sharpen into questions/, do NOT assert);
                            total collapse → deprecate. Touch confidence/status only; never raise
                            generation, and never flip a decision's row to `settled` — that is the
                            owner's ruling. When a verdict looks like it settles one, say so in the
                            ledger `summary` and leave the row alone.
- experiment-design target: auto-pick a `status: hardened` node with an empty ## Field Evidence;
                            judge testability from the body (non-empirical → redirect to reharmonization).
- modal-interchange       : auto-find one genuine crossover with SIBLING_SCOPE (seed only);
                            if none, file the reason in SCOPE/wiki/questions/ and treat as a no-op.
- ensemble                : auto-pick what it answers — the ACTIVE DECISION's ID first (that is what
                            someone is waiting on), else the scope's central question (overview.md /
                            CLAUDE.md purpose), else the questions/ node most linked from hardened
                            claims. Safe to automate: add-only into wiki/deliverables/, update-in-
                            place, node states untouched (EVOLUTION.md §14).

## PROCEDURE — do this exactly once per firing, then step 6
0. LOCK   — if `<LEDGER>.lock` exists, read the ISO ts written inside it: younger than ~1h → another
            iteration is genuinely mid-flight → STOP("overlap") (do NOT record or remove it — the lock is
            not yours). Older than ~1h → a crashed/abandoned iteration (no healthy iteration holds the lock
            that long: it wraps ONE skill run, and experiments are fire-and-return that UNLOCK before their
            wait) → reclaim it. Otherwise create `<LEDGER>.lock` and write the current ISO ts into it.
1. LOAD   — read the LEDGER tail: N = number of completed iterations, plus the last decision/result.
            If MAX_ITERS ≠ inf AND N ≥ MAX_ITERS → STOP("count-reached").
2. JUDGE  — FIRST resolve the ACTIVE DECISION per DECISION POLICY (read SCOPE/CLAUDE.md's
            `### Goal & Open Decisions`). No open decision → STOP("no-decisions") before spending
            anything: every downstream choice is measured against it.
            THEN check for an in-flight experiment: is there a `status: running` experiment node?
            • result has landed in SCOPE/.raw/experiments-results/ → R = reharmonization (its Phase C
              imports the result against the pre-registered criterion, flipping the node imported/abandoned).
            • no result yet, and (now − the launch ts in the LEDGER) < EXP_TIMEOUT → still running; do NOT
              relaunch. Let pushing pick a NON-experiment R to progress in parallel; if pushing says
              `current` (nothing else to do) → R = wait (poll only; no action this iteration).
            • no result yet, and ≥ EXP_TIMEOUT → set the node `status: abandoned`, then
              STOP("exec-blocked-needs-human").
            Otherwise (no experiment running) run `/reharm:pushing SCOPE`. From its read-only report take:
            R ∈ {root, reharmonization, critique, modal-interchange, experiment-design, ensemble, current}
            (a deep-research escalation recommendation is SKIPPED per DECISION POLICY — take the next
            candidate), its evidence, the latest stagnation verdict, and the soonest re-verification date.
            • R = current                          → STOP("nothing-pending"); report the soonest date.
            • stagnation verdict ∈ STOP_ON         → STOP("stagnation:" + verdict).
3. ACT    — perform EXACTLY ONE action for R, auto-deciding every choice per DECISION POLICY:
            • root              → `/reharm:root`  (atomize only the unprocessed .raw/ material;
                                   the loop never invents new external sources — that is what reseed signals).
            • reharmonization   → `/reharm:reharmonization SCOPE`
            • critique          → `/reharm:critique SCOPE`
            • modal-interchange → `/reharm:modal-interchange SCOPE SIBLING_SCOPE`
                                   (skip, treat as no-op, if SIBLING_SCOPE = none)
            • ensemble          → `/reharm:ensemble SCOPE` (question auto-picked per DECISION POLICY)
            • experiment-design → (only when NO experiment is running — one at a time; a running one is
                                   handled by JUDGE's poll above, not relaunched here):
                (a) DESIGN  : `/reharm:experiment-design «the chosen claim»`
                              → pre-registration node (status: planned) + a ## Handoff block.
                              If a `planned` node already exists, reuse it and go to (b).
                (b) EXECUTE : launch the real experiment ONLY if the GATE passes. The GATE is one switch
                              plus two auto-checked prerequisites:
                              1. RUN_EXPERIMENTS = yes         (CONFIG — the only part you set)
                              2. code-workspace path exists    (SCOPE/CLAUDE.md §2 Metadata)
                              3. a runner is recorded          — the node's `runner:` OR SCOPE/CLAUDE.md
                                                                 §6 Toggles. experiment-design records the
                                                                 plugin's runner-worker doc as the default
                                                                 at design time, so a fresh node normally
                                                                 passes; a node with neither (an older
                                                                 design) → re-run (a) on the claim — the
                                                                 design skill refreshes it with the lane.
                              • Pass → FIRE-AND-RETURN: launch the runner in the BACKGROUND and do NOT
                                       wait for it (blocking would hold the lock for the whole run):
                                       - entry point is a worker doc (a .md — the default runner-worker):
                                         spawn ONE background sub-agent (the RUNNER) instructed to "read
                                         <that absolute path> and follow it", passing absolute paths
                                         inline: the pre-registration node, the code workspace, the
                                         result sink (SCOPE/.raw/experiments-results/), and EVOLUTION.md
                                         (subs don't inherit plugin env vars). Per the worker doc it
                                         OPERATIONALIZEs in the workspace (authoring + dry-running under
                                         <workspace>/.reharm-runner/<node-stem>/), EXECUTEs under the
                                         pre-registered Conditions, and writes its report — or a BLOCKED
                                         report when the goal cannot be operationalized (missing data,
                                         hardware, credentials) — to the result sink. It never touches
                                         the wiki and never judges the claim.
                                       - entry point is a command (an external runner): launch that
                                         command (run_in_background, or submit to the external runner).
                                       Flip the node to status: running; the runner's report must land in
                                       SCOPE/.raw/experiments-results/. This iteration ENDS here — a later
                                       JUDGE collects the result (do NOT judge it now; a blocked report
                                       imports as abandoned and goes back to a human).
                              • Fail → stop after DESIGN; record gate = "exec-blocked".
            • wait              → do nothing this iteration (an experiment is in flight); go to step 6.
            • on any action error → record it, then STOP("action-error").
4. RECORD — append ONE JSONL line to the LEDGER (this is the loop's ONLY state; it lives outside the scope —
            the scope's own files are updated by the skills above, per EVOLUTION.md §8):
            {"n": N+1, "scope": "SCOPE", "R": "<R>", "cmd": "<command run>", "summary": "<one line>",
             "decision": "<active decision ID, or null when none applied>",
             "targets": ["<node stems this iteration mutated/judged — [] for non-node actions>"],
             "pruned": <count auto-pruned this iteration>, "needs_binding": <count filed for the human>,
             "eval_pass": <bool|null>, "stagnation": "<verdict>", "gate": <null|"exec-blocked">,
             "exp": <null|"launched"|"waiting"|"imported"|"abandoned">,
             "ts": "<ISO 8601 timestamp>", "stop": <null|"<reason>">}
            (For an experiment "launched" line, this ts IS the launch time JUDGE reads back for EXP_TIMEOUT.)
5. UNLOCK — remove `<LEDGER>.lock`.
6. NEXT   — continue or end per the INVOCATION MODE. The firing's own text tells you which mode you are
            in: a dynamic tick instructs you to re-arm ScheduleWakeup; an interval tick says the recurring
            cron fires the next tick automatically. Follow that instruction:
            • DYNAMIC (bare /loop) — no stop reason → call ScheduleWakeup with prompt set to the literal
              sentinel `<<loop.md-dynamic>>` — NOT "/loop" or an empty string (neither is the sentinel);
              the runtime re-expands it to this file at fire time. Delay: normal iteration → 1200–1800s;
              R = wait (only an experiment in flight, nothing else to do) → poll ~240s if the run is
              short/unknown (stays inside the 5-min cache window; avoid 300s), 1200s+ if known-long.
              Heavy iterations (web search + 3 refuters) always take the long delay — never poll those.
              A stop reason → OMIT the ScheduleWakeup call; that ends the loop.
            • INTERVAL (/loop <interval>) — no stop reason → do NOTHING (the cron re-fires by itself;
              never call ScheduleWakeup in this mode). A stop reason → CronList, find this loop's
              recurring job, CronDelete it — that ends the loop. (If the delete fails, the next tick
              re-derives the same stop from the LEDGER and retries; if the delete keeps failing, tell
              the user to cancel the cron manually — CronList → CronDelete, or ask to cancel it by job
              ID.) The cadence is fixed, so there is no experiment short-poll in this mode — a
              running experiment is simply re-checked on the next tick.

## STOP reasons (always written to ledger `stop`)
count-reached · nothing-pending · stagnation:reseed · stagnation:change-strategy ·
action-error · overlap · bad-scope · exec-blocked-needs-human · no-decisions

`no-decisions` means the scope declares no OPEN decision (none written, or all settled). That is a
clean, healthy stop, not a failure: either the work is done, or the owner needs to write the next
decision into SCOPE/CLAUDE.md. The loop deliberately cannot do it — a loop that invents its own goals
optimizes whatever it happens to find.

Any stop reached AFTER this iteration took the lock (step 0) still completes RECORD (the ledger line, with
`stop` set) and UNLOCK before ending — a stop reason only changes step 6 (dynamic: omit the wakeup;
interval: CronDelete the loop's cron job); it never skips releasing the lock. The one exception is `overlap` (and a pre-lock `bad-scope`): the lock belongs to another
live iteration, so exit without recording or removing it.

## How to invoke — run from the research project root; both forms re-read THIS file each firing
- RECOMMENDED — dynamic, self-paced:  `/loop`      (delay chosen per tick; ending = not re-arming — fail-safe)
- SUPPORTED  — fixed cadence:         `/loop 2h`   (interval ONLY — `/loop 2h <prompt>` would bypass this file)
Both modes enforce MAX_ITERS / STOP_ON via step 6 (set MAX_ITERS: N for a bounded run, inf for open-ended).
Why dynamic is the default: its ending is fail-safe — the loop ends by NOT re-arming its own wakeup —
while interval mode keeps firing until the loop actively CronDeletes its job; a missed delete means no-op
STOP ticks until you cancel the job (CronDelete, or ask to cancel it by job ID) or the 7-day expiry.
Pick interval mode when a predictable wall-clock cadence is
worth that trade. Run one loop per scope.
Either way the loop is LOCAL + session-scoped: the session must stay open AND the machine awake to fire
(a closed or sleeping laptop will not run it). Mid-run compaction (auto, or a manual /compact between
ticks) is SAFE: the schedule lives in the process, not the context; the next firing re-feeds this file in
full; state is in the LEDGER. /clear or a fresh conversation KILLS the schedule. For a fixed wall-clock
schedule (e.g. nightly) or a laptop-closed, unattended run, use cloud Routines (`/schedule`) — NOT this
template.
