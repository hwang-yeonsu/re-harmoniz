# Changelog

All notable changes to the `reharm` plugin are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
