# Changelog

All notable changes to the `reharm` plugin are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
