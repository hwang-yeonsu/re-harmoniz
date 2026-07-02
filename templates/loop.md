<!-- templates/loop.md — copy to  <your research project>/.claude/loop.md  and fill in CONFIG. -->
<!-- re:Harmoniz AUTONOMOUS evolution loop. Native /loop re-reads this file each firing (full text on the -->
<!-- first fire / after an edit / post-compact, else a short reminder while the full text persists in -->
<!-- context), so it must stay self-contained and recover its state from the LEDGER, not from chat memory. -->
<!-- It runs the existing /reharm:* skills; it is NOT a plugin skill itself. Invocation is at the bottom. -->
<!-- DYNAMIC-ONLY: this is the default prompt for a bare /loop (self-paced). Do NOT pass an interval — -->
<!-- a fixed-interval /loop cannot enforce MAX_ITERS or stop itself. For wall-clock schedules use Routines. -->

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
- MAX_ITERS:       «N | inf»          ← enforced by self-pacing (dynamic /loop only); state is in the LEDGER
- RUN_EXPERIMENTS: «no | yes»         ← yes LAUNCHES real code (fire-and-return, then polled); gated below
- EXP_TIMEOUT:     «duration | none»  ← a running experiment older than this → abandoned (no infinite wait)
- SIBLING_SCOPE:   «absolute path | none»   ← donor scope for modal-interchange
- STOP_ON:         reseed, change-strategy   ← stagnation verdicts that halt the loop
- LEDGER:          «<project>/.reharm-loop/<scope-name>.jsonl»   ← OUTSIDE the scope (EVOLUTION.md §8)

## DECISION POLICY — how the main session stands in for the user
- pushing recommendation  : take the cascade first-match as-is (already deterministic).
- reharmonization Phase B : auto-pick frontier-top + past-cadence nodes (no user-named topic);
                            record the picks and rationale in E####.md "Targets & Why".
- reharmonization Phase D : unchanged — 3 refuters as ISOLATED sub-agents (refuter.md; no mutation
                            narrative passed), ≥2/3 must survive; refute when unsure.
- critique adjudication   : adjudicate by evidence — clear support → adopt/reject; a contradiction
                            pair → resolve by evidence weight (absorb into ## Objections & Limits);
                            both sides weak → needs-research (sharpen into questions/, do NOT assert);
                            total collapse → deprecate. Touch confidence/status only; never raise generation.
- experiment-design target: auto-pick a `status: hardened` node with an empty ## Field Evidence;
                            judge testability from the body (non-empirical → redirect to reharmonization).
- modal-interchange       : auto-find one genuine crossover with SIBLING_SCOPE (seed only);
                            if none, file the reason in SCOPE/wiki/questions/ and treat as a no-op.

## PROCEDURE — do this exactly once per firing, then step 6
0. LOCK   — if `<LEDGER>.lock` exists, read the ISO ts written inside it: younger than ~1h → another
            iteration is genuinely mid-flight → STOP("overlap") (do NOT record or remove it — the lock is
            not yours). Older than ~1h → a crashed/abandoned iteration (no healthy iteration holds the lock
            that long: it wraps ONE skill run, and experiments are fire-and-return that UNLOCK before their
            wait) → reclaim it. Otherwise create `<LEDGER>.lock` and write the current ISO ts into it.
1. LOAD   — read the LEDGER tail: N = number of completed iterations, plus the last decision/result.
            If MAX_ITERS ≠ inf AND N ≥ MAX_ITERS → STOP("count-reached").
2. JUDGE  — FIRST check for an in-flight experiment: is there a `status: running` experiment node?
            • result has landed in SCOPE/.raw/experiments-results/ → R = reharmonization (its Phase C
              imports the result against the pre-registered criterion, flipping the node imported/abandoned).
            • no result yet, and (now − the launch ts in the LEDGER) < EXP_TIMEOUT → still running; do NOT
              relaunch. Let pushing pick a NON-experiment R to progress in parallel; if pushing says
              `current` (nothing else to do) → R = wait (poll only; no action this iteration).
            • no result yet, and ≥ EXP_TIMEOUT → set the node `status: abandoned`, then
              STOP("exec-blocked-needs-human").
            Otherwise (no experiment running) run `/reharm:pushing SCOPE`. From its read-only report take:
            R ∈ {root, reharmonization, critique, modal-interchange, experiment-design, current},
            its evidence, the latest stagnation verdict, and the soonest re-verification date.
            • R = current                          → STOP("nothing-pending"); report the soonest date.
            • stagnation verdict ∈ STOP_ON         → STOP("stagnation:" + verdict).
3. ACT    — perform EXACTLY ONE action for R, auto-deciding every choice per DECISION POLICY:
            • root              → `/reharm:root`  (atomize only the unprocessed .raw/ material;
                                   the loop never invents new external sources — that is what reseed signals).
            • reharmonization   → `/reharm:reharmonization SCOPE`
            • critique          → `/reharm:critique SCOPE`
            • modal-interchange → `/reharm:modal-interchange SCOPE SIBLING_SCOPE`
                                   (skip, treat as no-op, if SIBLING_SCOPE = none)
            • experiment-design → (only when NO experiment is running — one at a time; a running one is
                                   handled by JUDGE's poll above, not relaunched here):
                (a) DESIGN  : `/reharm:experiment-design «the chosen claim»`
                              → pre-registration node (status: planned) + a ## Handoff block.
                              If a `planned` node already exists, reuse it and go to (b).
                (b) EXECUTE : launch the real experiment ONLY if the GATE passes —
                              RUN_EXPERIMENTS = yes
                              AND a runner entry point is set (node `runner:` OR SCOPE/CLAUDE.md §6 Toggles)
                              AND the code-workspace path exists (SCOPE/CLAUDE.md §2 Metadata).
                              • Pass → FIRE-AND-RETURN: launch the ## Handoff command in the BACKGROUND
                                       (run_in_background, or submit to the external runner) — do NOT wait
                                       for it (blocking would hold the lock for the whole run). Flip the
                                       node to status: running; the runner's report must land in
                                       SCOPE/.raw/experiments-results/. This iteration ENDS here — a later
                                       JUDGE collects the result (do NOT judge it now).
                              • Fail → stop after DESIGN; record gate = "exec-blocked".
            • wait              → do nothing this iteration (an experiment is in flight); go to step 6.
            • on any action error → record it, then STOP("action-error").
4. RECORD — append ONE JSONL line to the LEDGER (this is the loop's ONLY state; it lives outside the scope —
            the scope's own files are updated by the skills above, per EVOLUTION.md §8):
            {"n": N+1, "scope": "SCOPE", "R": "<R>", "cmd": "<command run>", "summary": "<one line>",
             "eval_pass": <bool|null>, "stagnation": "<verdict>", "gate": <null|"exec-blocked">,
             "exp": <null|"launched"|"waiting"|"imported"|"abandoned">,
             "ts": "<ISO 8601 timestamp>", "stop": <null|"<reason>">}
            (For an experiment "launched" line, this ts IS the launch time JUDGE reads back for EXP_TIMEOUT.)
5. UNLOCK — remove `<LEDGER>.lock`.
6. NEXT   — if there is NO stop reason, call ScheduleWakeup with prompt set to the literal sentinel
            `<<loop.md-dynamic>>` — NOT "/loop" or an empty string (neither is the sentinel). The runtime
            re-expands `<<loop.md-dynamic>>` to this file at fire time and reminds you of the same each tick.
            Then choose the delay:
            • normal iteration (did evolution work, or no experiment running)  → delay 1200–1800s.
            • R = wait (only an experiment in flight, nothing else to do)       → poll: ~240s if the
              experiment is short/unknown (stays inside the 5-min cache window), or 1200s+ if it is
              known to be long. Avoid 300s (a cache miss that isn't even long).
            If there IS a stop reason, omit the call — that ends the loop.
            (Self-pacing is what enforces MAX_ITERS / STOP_ON and works only for a bare, dynamic /loop —
             hence dynamic-only. Heavy iterations (web search + 3 refuters) want the long delay; don't
             poll those. Only a bare experiment-wait uses the short poll.)

## STOP reasons (always written to ledger `stop`)
count-reached · nothing-pending · stagnation:reseed · stagnation:change-strategy ·
action-error · overlap · bad-scope · exec-blocked-needs-human

Any stop reached AFTER this iteration took the lock (step 0) still completes RECORD (the ledger line, with
`stop` set) and UNLOCK before ending — a stop reason only omits the step-6 ScheduleWakeup; it never skips
releasing the lock. The one exception is `overlap` (and a pre-lock `bad-scope`): the lock belongs to another
live iteration, so exit without recording or removing it.

## How to invoke — run from the research project root; bare /loop re-runs THIS file
This template is DYNAMIC-ONLY. Invoke it as a bare `/loop` with NO interval:
- Bounded run (stops at MAX_ITERS, or earlier on a stop reason):  `/loop`     (set MAX_ITERS: N)
- Open-ended, self-terminating when idle or stagnant:             `/loop`     (set MAX_ITERS: inf)
Why no interval: the main session enforces MAX_ITERS / STOP_ON by choosing whether to schedule its own
next wakeup, which works only for a bare (self-paced) /loop. Passing an interval (`/loop 6h`) hands pacing
to a fixed scheduler the prompt CANNOT stop — it would ignore MAX_ITERS / STOP_ON and run until Esc or the
7-day expiry. (`.claude/loop.md` is the default prompt for bare /loop anyway.) Run one loop per scope.
This loop is LOCAL + session-scoped: the session must stay open AND the machine awake to fire (a closed or
sleeping laptop will not run it). For a fixed wall-clock schedule (e.g. nightly) or a laptop-closed,
unattended run, use cloud Routines (`/schedule`) — NOT this template.
