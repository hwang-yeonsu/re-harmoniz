# Changelog

All notable changes to the `reharm` plugin are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
