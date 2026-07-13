# Changelog

All notable changes to the `reharm` plugin are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.1] — 2026-07-13

**Fix: `Esc` is not a stop mechanism for interval loops.** The loop docs listed `Esc` as a way to
end a run, but that only holds for **dynamic** mode (bare `/loop`), where `Esc` clears the pending
`ScheduleWakeup`. In **interval** mode (`/loop <cadence>`) the run is a backend-registered cron job
that fires independently of the session — `Esc` interrupts only the current tick, and the cron
re-fires on schedule. The one true terminator there is `CronDelete` (or the 7-day expiry). Verified
against the Claude Code scheduled-tasks docs.

### Fixed

- **Corrected the `Esc`-stops-the-loop claim across the loop docs** (`templates/loop.md`,
  `templates/loop.guide.md`, `templates/loop.guide.ko.md`, `skills/loop-setup/SKILL.md`). Every
  interval-mode terminator that read "until `Esc` / 7-day expiry" now names `CronDelete` (or "cancel
  by job ID") as the actual stop and demotes `Esc` to "skips the current tick only." The general
  "Stop any time with `Esc`" lines are split by mode: `Esc` for dynamic, `CronDelete` for interval.
  The wizard close-out message (`loop-setup`) carries the same correction.

## [0.12.0] — 2026-07-13

**One command to a running loop + experiments that work out of the box.** The eighth skill —
`reharm:loop-setup` — collapses "copy the template, fill CONFIG by hand, run `/loop`" into a single
interactive command, and the loop template gains a DEFAULT RUNNER so `RUN_EXPERIMENTS: yes` no
longer dead-ends on a scope whose code workspace is empty.

### Added

- **`reharm:loop-setup` — autonomous-loop wizard** (`skills/loop-setup/SKILL.md` + the
  `commands/loop-setup.md` dispatcher for `/reharm:loop-setup`). Detects the scope (`.raw/` +
  `wiki/` scan), derives the mechanical CONFIG fields (LEDGER path, MAX_TARGETS, STOP_ON) without
  asking, interviews only the real decisions (MAX_ITERS, RUN_EXPERIMENTS, SIBLING_SCOPE, dynamic vs
  interval), pre-validates the experiment gate **before the first tick**, writes `.claude/loop.md`
  from the plugin template (CONFIG placeholders only — the contract ships verbatim), and then
  starts the native `/loop` in the same invocation via the Skill tool (empty args → dynamic;
  cadence-only args → interval). Ends with a one-tick smoke-check. Never overwrites an existing
  loop.md without showing the CONFIG diff; a fresh ledger lock stops it.
- **`templates/loop.md` — DEFAULT RUNNER** (ACT step b). The manual protocol records a runner entry
  point and never infers one (EVOLUTION.md §12), so a blank `runner:` under the unattended loop
  meant a guaranteed `exec-blocked`. Now, when `RUN_EXPERIMENTS: yes` and the workspace path exists
  but no entry point is set, the loop operationalizes the pre-registration itself: it writes a
  self-contained script to `<workspace>/.reharm-runner/<node-stem>/`, records that path in the
  node's `runner:` **before** launching (§12's recorded-never-inferred audit rule holds), and fires
  it in the background. Goals the workspace cannot serve (missing data/hardware/credentials) still
  stop at `exec-blocked`. Protocol (EVOLUTION.md) and the experiment-design skill are unchanged —
  the fallback lives only in the loop template, where the delegated-authority override already lives.

### Changed

- **Guides (EN/KO)** — experiment section reworked around the default runner ("an empty workspace
  still works"); compact section now states that auto-compact is on by default
  (`autoCompactEnabled`), runs inside each turn's query pipeline (an over-threshold tick compacts
  itself unattended), and that forcing a compact every tick is an anti-pattern (lossy + breaks the
  cached prompt prefix).
- **READMEs (EN/KO), `docs/SKILLS.md`/`SKILLS.ko.md`** — `/reharm:loop-setup` documented as the
  quickest path to a running loop; skill count updated (seven evolution skills + one wizard).

### Migration

- **Existing wikis/scopes: none needed.** EVOLUTION.md, the seven evolution skills, the lint/score
  scripts, the node schema, the ledger JSONL format, and the lock protocol are all unchanged across
  0.11.0–0.12.0 (verified by diff). Ledgers keep counting; nodes are untouched.
- **The one artifact that can go stale is a hand-copied `.claude/loop.md`** from ≤ 0.10.x — it
  still runs (dynamic mode), but predates interval mode, the mode-branching step 6, and the DEFAULT
  RUNNER. Refresh it by re-running `/reharm:loop-setup`: the wizard detects the older body, keeps
  your CONFIG, and rewrites the rest from the current template. The file is a point-in-time copy
  owned by the research project — plugin upgrades never touch it, so this refresh is always an
  explicit step, never automatic.

## [0.11.0] — 2026-07-13

**Autonomous loop: interval mode + clearer contract.** Review-driven release; no skill or protocol
changes. Re-verified the native `/loop` internals on Claude Code 2.1.207: an interval-only
`/loop 2h` now also reads `.claude/loop.md` (via a dedicated `<<loop.md>>` cron sentinel,
re-expanded from disk each fire), and a cron loop can end itself by `CronDelete`-ing its own job —
so the old "dynamic-only, an interval can't stop itself" rationale no longer holds as an absolute.

### Added

- **`templates/loop.md` — interval mode** (`/loop 2h`, interval ONLY — a prompt would bypass the
  file). Step 6 NEXT now branches by invocation mode, detected from the firing's own text: dynamic
  → re-arm `ScheduleWakeup` with `<<loop.md-dynamic>>` (omit to end, fail-safe); interval → do
  nothing to continue (the cron re-fires), `CronList` + `CronDelete` the loop's job to end
  (fail-open: a missed delete keeps firing no-op STOP ticks until `Esc` / 7-day expiry). Dynamic
  stays the recommended default. `MAX_ITERS` / `STOP_ON` are enforced in both modes.
- **Guides — "Compacting mid-run is safe (`/clear` is not)"** (`loop.guide.md` /
  `loop.guide.ko.md`): the schedule lives in the CLI process, not the context; the runtime resets
  its delivered-marker on compaction so the next firing re-feeds the full loop.md; state recovers
  from the ledger tail. Verified in the 2.1.207 bundle (compact cleanup calls
  `resetAutonomousLoopDelivered`).

### Changed

- **Experiment gate rewritten as "one switch, two prerequisites"** (template ACT step b + both
  guides): `RUN_EXPERIMENTS` is the only knob you set; the runner entry point and the
  code-workspace path are auto-checked scope facts. Same 3-AND semantics, no behavior change —
  the presentation made all three look like user decisions.
- **READMEs (EN/KO)** — the "dynamic-only, don't pass an interval" paragraphs replaced with the
  two-mode contract (dynamic recommended, interval supported with its fail-open caveat) plus the
  compact-vs-clear rule.

## [0.10.0] — 2026-07-02

**`reharm:ensemble`** (protocol **v0.5 → v0.6**): the loop finally gets an *exit*. A scope can
reach a fully hardened core and still have nowhere the answer actually lives (field-evidenced: a
central question sat answered-in-pieces across 10 hardened nodes with no synthesis outlet). The
seventh skill assembles what survived into one citable deliverable — and the deliverable is
deliberately **not** a knowledge node.

### Added

- **`reharm:ensemble` — answer synthesis** (`skills/ensemble/SKILL.md` + the `commands/ensemble.md`
  0.4.1-style wrapper for `/reharm:ensemble`). Fix the question (user-confirmed — it is the
  deliverable's identity) → collect the bearing claims/mashups **read-only** → synthesize
  `wiki/deliverables/<question-slug>.md`: an `## Answer` whose every load-bearing sentence carries
  an inline `[[node]] (status · confidence · generation)` snapshot, `## Load-bearing seeds` (the
  immature nodes the answer leans on, listed not hidden), `## Open caveats`, and
  `## What would change this conclusion`. A **confidence propagation header** under the H1 names
  the weakest load-bearing claim and sets the deliverable's confidence to that floor — derived,
  never asserted. Update-in-place (git owns versions, §8); **node states are invariant** — the
  skill writes only `deliverables/` plus the index/hot/log close-out.
- **`EVOLUTION.md` §14 + §2 `type: deliverable`** — a non-evolving node kind (required keys:
  `type`/`title`/`created`/`updated`/`question`; evolution mechanics omitted by design, like
  `experiment`). §1 tree gains `wiki/deliverables/`; §11.2 gains a Deliverables index table
  (outside the maturity census).

### Changed

- **`wiki-lint.py`** scans `wiki/deliverables/` and validates the §2 deliverable keys;
  `deliverable` joins the type enum. **`boundary-score.py`** adds `deliverable` to
  `EXCLUDE_TYPES` — snapshots never skew the frontier graph.
- **`reharm:pushing`** — new cascade rule (before the modal-interchange rule): ≥5 nodes at
  `hardened`-or-above with the central question's deliverable absent or stale (`updated` predating
  the newest `E####.md`) → recommend `ensemble`. Gather-state reads the deliverable lane.
- **`templates/loop.md`** — `ensemble` joins the JUDGE R-set and ACT list (safe to automate:
  add-only, update-in-place, node states untouched; the question is auto-picked from the scope's
  central question per DECISION POLICY). Guides (EN/KO) synced — the loop now drives seven skills.
- **`plugin.json` / `marketplace.json` descriptions** list the seventh skill; **README (EN/KO)**
  gain the skill row, the `deliverables/` tree entry, and a walkthrough step ⑦.

## [0.9.0] — 2026-07-02

Reinforcement + question-driven research (protocol **v0.4 → v0.5**): the ambiguous backlog gets a
batch triage and an aging path, cross-scope borrowings get a drift baseline, the autonomous loop
gets a target cap, and a new **Deep Research Bridge** (§13) gives stuck evidence a deep-research
escape hatch — manual-only, gated by a scope toggle. Additive-only; legacy question statuses and
legacy result lanes stay valid.

### Added

- **`EVOLUTION.md` §13 — Deep Research Bridge.** The §12 sibling for the *evidence* gate
  (`developing → hardened`): DESIGN (flip a question node to `status: escalated` + an
  `## Escalation` block answering "what would change our mind?") → EXECUTE (the external tool named
  by the scope `CLAUDE.md` `Research escalation:` toggle — unset keeps the bridge closed) → RETURN
  (`.raw/deep-research/` → `reharm:root`, with the report's `sources/` page recorded
  `origin: secondary` + `derived_from:` ancestry). Manual-only in v1: `reharm:pushing` gains a
  cascade rule (after the experiment rule) recommending escalation for a `developing` claim with no
  new independent source for ≥2 sessions or an `open` question stalled ≥4 sessions; the autonomous
  loop template explicitly skips that row.
- **Question lifecycle (§2)** — `wiki/questions/` pages get their own enum:
  `status: open | answered | escalated | archived`, never the maturity ladder. Legacy pages
  carrying maturity values stay valid — `wiki-lint.py` reports them as non-breaking
  `legacy_question_status` warnings.
- **Source independence metadata (§2)** — `sources/` pages may carry `origin: primary|secondary`
  and `derived_from:` (wikilinks to the primaries a secondary digests). The per-source root worker
  records them; the refuter's evidence lens treats overlapping `derived_from` chains as
  **non-independent** (they cannot jointly satisfy the ≥2-independent-sources gate); lint
  validates the `origin` enum.
- **`borrowed:` snapshots on cross-scope mashups (§2)** — `reharm:modal-interchange` mints one
  entry per donor node (`node` / `scope` / `status_at_mint` / `gen_at_mint` / `date`);
  `reharm:reharmonization` Phase A compares the donor's current state against the snapshot and
  absorbs drift as a new objection; `reharm:pushing` surfaces drift as a reharmonization trigger;
  `wiki-lint.py` validates the subkeys (its stdlib frontmatter parser now reads one-level
  `- key: val` mapping lists).
- **External-wikilink allowlist** — a scope `CLAUDE.md` `Allowed external wikilinks:` toggle;
  matching stems are reported by lint under a new `allowed_external` count instead of
  `unresolved_external`, so deliberate vault/cross-scope citations stop reading as standing noise.
  The parser strips the template's inline HTML comments (caught against a live scope: a
  `<!-- … -->` annotation on the toggle line silently defeated every match).
- **`boundary-score.py --json` rows expose `status` / `generation` / `challenges_survived` /
  `sources_count`** — the evidence-gate surface pushing's escalation signal reads without
  re-opening node files.

### Changed

- **`reharm:critique` — batch triage + aging.** Themed bundles are adjudicated in at most two
  multiSelect passes (promote — including *escalate* per §13 when the toggle is set — then archive;
  unpicked = hold), while genuinely ambiguous single items keep the one-at-a-time interview. Open
  questions untouched for ≥4 sessions are proposed as **one** batch-archive question — user-picked
  only, never auto-archived. "Verdicts never raise `generation`" unchanged.
- **`reharm:modal-interchange` — staged reconnaissance.** Between the hot/index pass and the
  drill-down, a new frontmatter sweep scans *every* claim/mashup's frontmatter + first body line in
  both scopes (grep-cheap), making the shortlist evidence-based; the full-read drill-down is capped
  at 5 pages.
- **`templates/loop.md` — `MAX_TARGETS` (default 2)** caps how many nodes one unattended
  reharmonization iteration may auto-pick in Phase B (excess waits for the next tick), the ledger
  line gains a `targets` field naming the nodes each iteration touched, and the DECISION POLICY
  never auto-takes the §13 escalation row. Guides (EN/KO) synced. **`EVOLUTION.md` §3** caps the
  Phase B decay-candidate list at the top 5 seed/developing nodes by longest cadence overrun.
- **`EVOLUTION.md` §1 — result lanes are declared, not hardcoded.** The scope `CLAUDE.md` §2
  Metadata declaration is canonical; `.raw/deep-research/` joins `.raw/experiments-results/` as a
  default lane, and a declared legacy lane (e.g. pre-0.6.0 `.raw/experiments/`) stays first-class.
  `templates/SCOPE_CLAUDE.md` gains the lane declarations plus the `Research escalation:` and
  `Allowed external wikilinks:` toggles.
- **Experiment `claim:` accepts a list (§2)** — one run routinely serves several claims/questions
  at once (field-evidenced); the schema, lint, and the experiment-design skill now say so.
- **README (EN/KO)** — scope tree gains the `deep-research/` lane and the question lifecycle;
  skill-table rows for critique / modal-interchange / pushing updated; autonomous-mode safeguards
  mention `MAX_TARGETS` and the ledger `targets` field.

## [0.8.0] — 2026-07-02

The trust core (protocol **v0.3 → v0.4**): the three steering signals an autonomous or long-running
loop depends on — Phase D verdicts, the session eval, and the maturity census — stop being
in-context roleplay, hand-scored numbers, and a hand-edited line, and become structurally isolated,
counter-based, and computed. Additive-only; no scope migration required.

### Added

- **`skills/reharmonization/refuter.md` — Phase D refuters are now isolated sub-agents.** A new
  frontmatter-less worker doc (the `skills/root/per-source.md` pattern) the session spawns three of
  in parallel, one lens each (`coherence` / `evidence` / `reproducibility`). Each refuter receives
  its material **inline** — the target node verbatim, the cited `wiki/sources/` page originals
  (quote-distortion surface for the evidence lens), and per-lens extras (supports/contradicts
  neighbor conclusions; the pre-registered CONFIRM/REFUTE block when one exists) — and **never the
  session's mutation narrative**: the §1 pollution-control invariant applied to the judging side.
  Refuters are judgment-only (write nothing, fetch nothing, read nothing but `EVOLUTION.md`) and
  return the existing §5 JSON contract. `EVOLUTION.md` §5 promotes isolated parallel execution to
  the standard, moves the prompt template into refuter.md, and adds a fail-loud degraded mode: if
  spawning is unavailable, the lenses run in-context and the E#### report must record
  `refuters ran non-isolated`.
- **`wiki-lint.py` computes the maturity census** — the report JSON gains a top-level
  `status_census` (claims + mashups frontmatter aggregation) plus a non-breaking `census_drift`
  warning when the display-only `**Census:**` line in `index.md` disagrees (or is missing while
  nodes exist). `reharm:pushing` now reads `status_census` as its census signal instead of parsing
  the index line.
- **`wiki-lint.py` validates the latest session eval** — the newest `E####.eval.json` must carry a
  boolean `pass` and a `stagnation.verdict` enum (§7); a missing, unparseable, or invalid file is
  reported as non-breaking `eval_findings` warnings. Neither new check affects `clean`.

### Changed

- **`EVOLUTION.md` §7 — session eval schema v2, counter-based stagnation.** `checks` gains
  `mutations_rejected` and `new_independent_sources`; `stagnation.trailing` carries per-session
  counter rows (`generation_progress` / `mutations_rejected` / `new_seeds` /
  `new_independent_sources` / `failed_checks`) instead of scores. The verdict is computed **from
  counters only**: `reseed` = 3 trailing sessions with zero generation progress, zero new seeds,
  zero new independent sources; `change-strategy` = the same check failing 3 sessions in a row or
  3 consecutive all-mutations-rejected sessions; otherwise `continue`. `score` becomes optional,
  display-only, and derived by a fixed formula — nothing may branch on it. Motivated by field
  evidence: a healthy session that correctly rejected a bad mutation was mis-scored as a 0.45
  slump; rejected mutations are now a first-class, visible counter (healthy culling), and only a
  *streak* of them signals a strategy problem. Legacy v1 evals stay readable (only
  `pass`/`stagnation.verdict` are load-bearing).
- **`skills/reharmonization/SKILL.md` Phase D** spawns the isolated refuters (realpath-resolved
  worker doc + `EVOLUTION.md`, inline materials, parallel), re-spawns the same lens workers after a
  partial-collapse revision, and states the fail-loud degraded mode. **`templates/loop.md`**
  DECISION POLICY wording follows.

## [0.7.1] — 2026-07-02

Correctness and precision fixes to the 0.7.0 autonomous loop template, verified against the native
`/loop` implementation (decompiled Claude Code 2.1.197). No API, skill, or behavior-shape changes.

### Fixed

- **`templates/loop.md` — the dynamic reschedule now names the correct sentinel.** Step 6 said to call
  `ScheduleWakeup(prompt = the exact same /loop input)`, but a bare `/loop`'s "input" is not a sentinel:
  the runtime re-expands a loop.md-backed loop only when the wakeup carries the literal
  `<<loop.md-dynamic>>`. The template now passes that sentinel explicitly (the runtime also reminds the
  model of it each tick), so self-pacing — and therefore `MAX_ITERS` / `STOP_ON` enforcement — cannot
  silently fail on a mis-named prompt.
- **`templates/loop.md` — the per-scope lock can no longer orphan.** Every `STOP` reached after the lock
  is taken now completes `RECORD` (with `stop` set) and `UNLOCK` before ending — only `overlap` (another
  live iteration's lock) exits untouched — and the lock now carries an ISO timestamp so a lock older than
  ~1h is treated as a crashed iteration and reclaimed. Previously a stop or crash could leave
  `<ledger>.lock` behind and deadlock every future run on that scope with `STOP("overlap")`.

### Changed

- **Feature-gate caveat + smoke test (`templates/loop.guide.md` / `loop.guide.ko.md`).** Bare `/loop`
  reading `.claude/loop.md` and the dynamic `ScheduleWakeup` are behind Claude Code rollout flags; if
  either is off, `/loop` ignores loop.md or runs a single tick and stops (the wakeup no-ops), so
  `MAX_ITERS` never engages. The guides now say to smoke-test one tick before trusting an overnight run.
  Confirmed working on Claude Code 2.1.197.
- **Accurate re-feed description (`templates/loop.md` header + guide "does it run as intended" tables).**
  "re-feeds this file verbatim each firing" → the file is re-read each firing, delivered in full on the
  first fire / after an edit / post-compact and as a short reminder otherwise (the full text persists in
  context). The self-contained, ledger-based recovery design is unchanged and, if anything, better
  motivated.

## [0.7.0] — 2026-06-23

### Added

- **`templates/loop.md` — an opt-in autonomous evolution loop** that drives the existing
  skills unattended through the native `/loop` command. Copied to a research project's
  `.claude/loop.md`, it runs one iteration per firing: `reharm:pushing` selects the next move
  and the recommended skill (`root` / `reharmonization` / `critique` / `modal-interchange` /
  `experiment-design`) executes, with the main session auto-deciding the targets, verdicts, and
  seeds the skills normally route to the user. It **deliberately overrides the protocol's
  "nothing is auto-decided" rule** (EVOLUTION.md §3/§4) and therefore ships as a project-local
  template, **not** as a plugin skill — the override stays out of the plugin core, and the
  skill count is unchanged (still 6).
- **A loop-control contract** baked into the template: it runs as a **dynamic, self-paced** bare
  `/loop` (paced via ScheduleWakeup — enforces `MAX_ITERS` and self-terminates when idle or stagnant;
  a fixed-interval/cron `/loop` is intentionally unsupported, since only a bare `/loop` can self-pace
  and stop itself); a per-scope lock; a ledger kept **outside** the scope (EVOLUTION.md
  §8 forbids in-scope state files); reversible `deprecate` (never delete); and double logging
  (`E####.md` + ledger) for audit. Optional real experiment execution is triple-gated on
  `RUN_EXPERIMENTS=yes` **and** a configured runner (node `runner:` or scope `CLAUDE.md` §6)
  **and** an existing code-workspace path (§12) — otherwise it stops at DESIGN + handoff. When it does
  run it is **fire-and-return**: the experiment is launched in the background and a later iteration polls
  for its result (riding along with normal work; a dedicated `~240s` / `1200s+` poll only when otherwise
  idle), so a long run never blocks the loop or holds the lock; `EXP_TIMEOUT` abandons a stuck run.
- **`templates/loop.guide.md` + `templates/loop.guide.ko.md` (EN/KO)** — a long-form companion to the
  loop template: what it is and why, a *native `/loop` ↔ template design* verification table, the
  **execution model** (`/loop` is local + session-scoped — the session must stay open and the machine
  awake to fire; a laptop-closed unattended run needs cloud Routines, not `/loop`), the safeguards, the
  experiment gate, and the exact commands. Linked from the README "Autonomous mode" sections.

### Changed

- **`plugin.json` description** notes the opt-in autonomous loop template (skill set unchanged).
- **README (EN/KO)** gain an "Autonomous mode (opt-in)" section, including a **"Where it runs"** note
  (`/loop` is local + session-scoped — session open + machine awake; a closed laptop needs cloud
  Routines) and a link to the new autonomous-loop guide.
- **`templates/loop.md`** states the same execution-model limit in its invocation notes, so the
  copied-in contract stays self-contained.

## [0.6.0] — 2026-06-22

### Added

- **`type: experiment` node + a field-experiment designer skill** (`reharm:experiment-design`).
  A new node kind under
  `wiki/experiments/` that **pre-registers** the experiment which would confirm or refute a
  claim stuck at the `hardened → evergreen` gate: hypothesis, a CONFIRM/REFUTE criterion fixed
  *before* the run (the §5 reproducibility lens applied prospectively), the conditions to
  record, and a plain-language goal for an external runner. The skill is the DESIGN layer of
  the new §12 bridge — it designs and records only, never runs code and never authors
  code-level metric/verify commands (that is the runner's planner, e.g. `autoresearch`'s
  `/autoresearch:plan`). Invoked by the user; `reharm:pushing` only recommends it.
- **`EVOLUTION.md` §12 — Field Experiment Bridge** — documents the DESIGN / OPERATIONALIZE /
  EXECUTE layering, the tool-agnostic seam, the `.raw/experiments-results/` return path, and the
  testability gate (only empirically testable claims get an experiment). The experiment node
  schema lands in §2; §3, §4 Phase C, and §5 gain the pre-registration cross-references.

### Changed

- **`wiki-lint.py` validates `type: experiment` nodes** — `wiki/experiments/` is scanned,
  `experiment` joins the type enum, experiment nodes require `type/title/created/status/claim`
  (no evolution-mechanic keys), and `status` is validated against the experiment lifecycle
  (`planned/running/imported/abandoned`) instead of the maturity ladder.
- **`boundary-score.py` excludes `type: experiment`** from frontier scoring — pre-registration
  records are design artifacts, not knowledge nodes, so they never skew a claim's score.
- **Scope `CLAUDE.md` template** gains an optional experiment-runner toggle (§6).
- **README (EN/KO)** document the skill, the `experiments/` directory, and a
  pre-registration step in walkthrough ⑥.
- **Field-origin result lane renamed** `.raw/experiments/` → `.raw/experiments-results/` —
  disambiguates the run-result landing directory (the field-origin convention, §1/§12) from the
  new `wiki/experiments/` pre-registration nodes, which share the `experiment` name. Updated in
  `EVOLUTION.md`, both READMEs, the scope `CLAUDE.md` template, and the `reharm:experiment-design` /
  `reharm:reharmonization` / `reharm:pushing` skills. The `experiment` node type and the
  `wiki/experiments/` node directory are unchanged.

## [0.5.0] — 2026-06-18

### Added

- **`reharm:root` per-source fan-out** — the skill is now an *orchestrator +
  synthesizer* that never loads a raw source body into its context. Each source is
  handed to an isolated sub-agent that owns its read → summary → draft atomize; the
  main agent merges the drafts, wires cross-links, and writes the global files. This
  makes the **pollution-control invariant** structural — one source's framing can no
  longer leak into another's claims — and it keeps per-source token cost out of the
  main context. Fan-out is unconditional (one sub even for a single source); an N≥2
  threshold was considered and rejected so the invariant stays exceptionless.
- **`skills/root/per-source.md`** — a new front-matter-less worker doc the
  orchestrator spawns once per source. It lands the source, writes its
  `wiki/sources/` page, drafts claims (`status: seed`, ≤ 15) into `.reharm-draft/`,
  and returns a small JSON contract (draft paths + merge keys + supports/contradicts
  candidates) so the main agent can merge without reading raw bodies. It is handed
  **absolute paths** (worker doc + `EVOLUTION.md`) because a spawned sub does not
  inherit `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}`. Workers never verify or
  promote — every draft is born `seed`; maturity stays `reharm:reharmonization`'s job.
- **Scope-root `.reharm-draft/` staging** — sub-agents draft into
  `.reharm-draft/<source-stem>/` at the scope root, **outside both `wiki/` and
  `.raw/`** (the only trees `wiki-lint.py` scans). One dir per sub means zero path
  contention when two sources yield the same claim stem, and an aborted run's leftover
  drafts are inert to lint — never ingested as nodes. The main agent empties the dir
  before fan-out and after promotion. No Python changed: the staging area is invisible
  to the existing scripts by construction.

### Changed

- **`EVOLUTION.md` documents the fan-out as protocol** — the §1 scope tree gains the
  transient `.reharm-draft/` entry, and a new "Root multi-source handling" subsection
  states the pollution-control invariant and the main/sub responsibility seam (sub =
  land / summary / draft; main = merge / connect / global files / lint).
- **`reharm:root` now lints at the end of a run** (`wiki-lint.py --json`), so the
  fan-out merge is verified to leave `duplicate_stems` / `dead_wikilinks` / `orphans`
  at zero before the skill reports done.
- **Per-source overflow is preserved as `questions/` candidates** — assertions beyond
  the 15-node cap are returned by each sub as `overflow_candidates` and filed under
  `wiki/questions/` by the orchestrator, restoring 0.4.2's overflow→`questions/`
  behavior within the fan-out architecture (the sub itself never writes canonical
  `questions/`; the main agent owns that write).

## [0.4.2] — 2026-06-17

### Changed

- **`reharm:root`'s new-node cap is now per source, not per run** — the limit of
  15 new nodes applies to each source independently; overflow still lands in
  `wiki/questions/` as candidates. The procedure was already written around a
  single source ("Land the source"), so a per-run cap unfairly squeezed batch
  seeding where one run ingests several sources. The skill now also states that
  sources are processed one at a time (`skills/root/SKILL.md`).

## [0.4.1] — 2026-06-17

### Added

- **Namespaced slash commands** — each skill now ships a thin `commands/<name>.md`
  dispatcher (`/reharm:root`, `/reharm:reharmonization`, `/reharm:modal-interchange`,
  `/reharm:critique`, `/reharm:pushing`) that reads and follows the bundled
  `SKILL.md`. Plugin skills alone surface only as `/name (reharm)`; the wrappers add
  the colon-namespaced `/reharm:*` invocation while the skills keep auto-triggering.
  `plugin.json` now declares `"commands": "./commands/"`.

## [0.4.0] — 2026-06-16

### Added

- **Experiment lane** — a `.raw/experiments/` convention that routes a scope's own
  experiment / real-world results into the relevant claim's `## Field Evidence`.
  `reharm:reharmonization` Phase C owns the import; external material (papers, web,
  repos) stays seed, and ambiguous origin is confirmed in Phase B. `reharm:root` is
  unchanged — it still summarizes any source, experiment reports included
  (`EVOLUTION.md` §1, §4).
- **`reharm:pushing`** now flags a `hardened` node stuck at the empty
  `## Field Evidence` evergreen gate and recommends running an experiment — the one
  promotion only the §2 code workspace can unblock.

### Changed

- **Field Evidence entries record the conditions a result held under** (dataset,
  scale, hardware, hyperparameters), so the §5 reproducibility lens can adjudicate
  them (`EVOLUTION.md` §2).
- **The `hardened → evergreen` gate is now condition-aware** — conditional field
  evidence requires the claim's scope to match those conditions with no open
  counterexample remaining (`EVOLUTION.md` §3).
- Protocol bumped to **v0.3** (`EVOLUTION.md` header) to reflect the §1–§4 revisions.
- README (EN/KO): walkthrough ⑥ and the scope tree document the `.raw/experiments/`
  convention and the condition-aware gate.

## [0.3.0] — 2026-06-16

### Added

- **`reharm:pushing`** — a read-only next-step advisor. It inspects a scope's
  current wiki + evolution state (frontier scores, lint health, maturity
  census, the last session's stagnation verdict) and recommends which skill to
  run next — `root` (seed), `reharmonization` (evolve), or `critique`
  (adjudicate) — with the evidence behind each. It writes nothing and runs
  nothing; the user decides. Built on the existing `boundary-score.py` and
  `wiki-lint.py` scripts — no new code paths.
- Scope `CLAUDE.md` template now points to `/reharm:pushing` for orientation
  when unsure what to do next in a scope.

### Changed

- README (EN/KO): added a "why not just a wiki?" section that sharpens the
  research-specialized differentiation (claims are graded and hardened, not
  merely accumulated), plus a `reharm:pushing` usage scenario and skill-table
  entry.

## [0.2.0] — 2026-06-15

- Initial public release. Four skills — `reharm:root` (scaffold + atomic
  seeding), `reharm:reharmonization` (5-phase evolution session),
  `reharm:modal-interchange` (cross-scope mashup), `reharm:critique` (user
  adjudication of ambiguous nodes) — over the `EVOLUTION.md` protocol (v0.2).
  Ships the stdlib `boundary-score.py` (frontier scorer) and `wiki-lint.py`
  (scope health check); web search uses native tools.
