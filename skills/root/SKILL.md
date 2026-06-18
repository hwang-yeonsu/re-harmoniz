---
name: root
description: "re:Harmoniz entry point — scaffold a research scope and/or seed it: throw in a repo URL, article, pseudocode, existing note, or rough idea and it lands in .raw/ and becomes atomic claim nodes. Triggers: reharm root, root this, 시드 투입, 스코프 만들어, seed the scope, plant, ingest into research scope"
---

# reharm:root — Scaffold & Atomic Seeding

Turns any input (a source or a rough topic) into atomic knowledge nodes inside a research scope. **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) first and follow it.** Key sections: §1 (anatomy, sources-vs-claims, the fan-out invariant), §2 (node schema), §6 (web search policy), §11.2 (index template).

You are the **orchestrator + synthesizer**: you never read a raw source body. Each source is atomized by an isolated sub-agent (`per-source.md`); you merge the small draft claims they return, wire cross-links, and write the global files. That isolation is the pollution-control invariant — one source's framing cannot leak into another's claims (EVOLUTION.md §1).

## Procedure

1. **Resolve the scope.** If the current directory is not a research scope (`.raw/` + `wiki/` present), either take the target path from the arguments or ask once.
   - **If the scope does not exist yet, scaffold it**: create the §1 tree, copy `${CLAUDE_SKILL_DIR}/../../templates/SCOPE_CLAUDE.md` → `CLAUDE.md` and fill what is known (purpose, seed candidates), create initial `index.md` (§11.2) / `hot.md` / `log.md` / `overview.md`. Then continue.
   - Read the scope `CLAUDE.md` (verification rules, toggles, seed queue).
2. **Normalize input → a source list.** A directory/glob → its **unprocessed** files (those with no matching `wiki/sources/` page yet); a single file / URL / paste → one source; a bare topic with no concrete source → not fan-out, use the single-path seeding below. Enforce **≤ 8 sources per run**: take the first 8, list the rest, recommend a second run — never silently truncate.
   - **0 unprocessed sources** → report "nothing to root," suggest `reharm:pushing`; spawn nothing.
3. **Fan out — one sub-agent per source** (always, even for a single source). First **empty any stale `.reharm-draft/`** (a clean slate from a prior aborted run). Resolve the **absolute** paths of the worker doc (`${CLAUDE_SKILL_DIR}/per-source.md`) and `EVOLUTION.md` (`${CLAUDE_SKILL_DIR}/../../EVOLUTION.md`) — e.g. with `realpath` — and launch each sub in parallel, instructed to "read `<abs worker-doc path>` and follow it," plus its **one** source ref, the absolute scope path, a digest of the scope `CLAUDE.md` toggles, and the absolute `EVOLUTION.md` path. Pass **paths only — never a raw source body** (the §1 invariant).
4. **Subs run isolated** (per `per-source.md`): each lands its source → writes `wiki/sources/<x>.md` → drafts claims into `.reharm-draft/<source-stem>/` (`status: seed`, ≤ 15, no web enrichment) → returns its JSON contract (the one defined in `per-source.md`). A sub never touches `index/hot/log/overview`, canonical `claims/`, or another sub's draft dir.
5. **Collect returns.** A sub that returned `failed` (or never returned) → record the source in `wiki/questions/` + a `log.md` line, then continue; partial success is valid. A `partial` / `overflow > 0` return → record the deferred count in `log.md` so the truncation is visible; the source carried more atomic claims than the per-source cap, so recommend splitting it or a focused follow-up run (assertions beyond the cap are not retained — only the count is).
6. **Merge & promote.** Group drafts across all subs by normalized `aliases` (preferred) then title stem. Reading the **small draft bodies is allowed** — they are distilled, not raw. Merge duplicates (union their `cites` / `sources:`) and **promote** each survivor into canonical `wiki/claims/`. If a canonical node already exists (this run or a prior one), **update it, don't duplicate**. Then **empty `.reharm-draft/`**. Nodes stay `seed` — root never verifies or promotes maturity, even when a merge unions ≥ 2 independent sources.
7. **Connect.** Confirm the subs' supports/contradicts **candidates** and write the real wikilinks; conflicts get `> [!contradiction]` callouts on both nodes. (For a single source the cross-source edges are simply none.)
8. **Close out.** Update `index.md` (§11.2 maturity census), overwrite `hot.md`, prepend a `log.md` entry (`## [date] root | <title>`).
9. **Lint.** From the scope root run `python3 ${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py --json`; expect `duplicate_stems` / `dead_wikilinks` / `orphans` = 0. `.reharm-draft/` sits outside the trees the linter scans, so any stray draft is invisible to it.

### Bare topic, no source

No source to land → not a fan-out case. Keep the single-path behavior in the main agent: seed the topic directly (optionally web-discovering sources within EVOLUTION.md §6 bounds), atomize into `wiki/claims/`, connect, close out, lint. (Web-discovered sources may fan out in a future version.)

## Constraints

- **Always fan out** — one sub-agent per source, even for a single source. The main agent never reads a raw source body; an N≥2 threshold was rejected (EVOLUTION.md §1). `merge` and the cross-source half of `connect` simply degrade to no-ops for one source.
- The orchestrator **resolves and passes absolute paths** (worker doc + `EVOLUTION.md`) into each sub's spawn prompt — subs don't inherit `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}`, so plugin-relative env vars won't resolve inside them.
- **≤ 8 sub-agents per run**; overflow → report the backlog and recommend a second run (point at `reharm:pushing`).
- Sub-agents write only `wiki/sources/` + `.reharm-draft/<src>/`; the main agent owns merge, cross-links, `index/hot/log`, and lint. **Empty stale `.reharm-draft/` before fan-out and after promotion.**
- **Max 15 new nodes per source** (unchanged from 0.4.2; now enforced inside each sub).
- **No verification, no promotion here** — that is `reharm:reharmonization` Phase D. Every seed is born `seed`.
- **No web enrichment in subs** (v1) — evidence hunting is `reharm:reharmonization` Phase C. A sub may still fetch the one source URL to land it; the per-scope `Web search: disabled` toggle turns even that off.
