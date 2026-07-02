# Changelog

All notable changes to the `reharm` plugin are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
