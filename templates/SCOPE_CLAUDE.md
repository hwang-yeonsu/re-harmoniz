# Research_<TOPIC> — Research Scope

## 1. Purpose & Boundaries

<One paragraph: what this scope researches, and what is explicitly out of scope.>

## 2. Metadata (the scope is not a code workspace)

- **Code workspace path(s): `<absolute path — fill in>`**
- Experiment lane: experiment reports produced in the workspace land in this scope's `.raw/experiments-results/` (the field-origin convention) and re-enter through `reharm:root`; `reharm:reharmonization` Phase C imports their conclusions — with the conditions they held under — into the relevant claim's `## Field Evidence` (the evergreen gate). External material (papers, web, repos) lands elsewhere under `.raw/` and is treated as seed.
- Deep-research lane: reports returning from a §13 escalation land in `.raw/deep-research/` and re-enter through `reharm:root` (their `sources/` pages are `origin: secondary` with `derived_from:` ancestry).
- These lane declarations are **canonical** (EVOLUTION.md §1): skills route results by what this section declares, so a legacy lane name (e.g. `.raw/experiments/`) stays valid in a scope that declares it here.

## 3. Protocol

- This scope follows the **re:Harmoniz protocol** (`reharm` plugin, `EVOLUTION.md`): node schema, maturity state machine, 5-phase evolution sessions, report templates.
- `.raw/` is immutable. Frequent revision of wiki nodes is encouraged.
- Unsure what to do next here? Run `/reharm:pushing` (read-only) — it reads this scope's state and recommends the next skill (seed / evolve / adjudicate).

## 4. Adversarial Verification (applies to any research loop running in this scope)

- Every claim carries explicit confidence: high (multiple independent sources agree) / medium (single good source) / low (speculation, unverified).
- Mutations and new assertions pass only if **≥2 of 3 refuters** (coherence / evidence / reproducibility lenses) fail to refute them. When uncertain, refute.
- Valid objections are never discarded — absorb them into the node's `## Objections & Limits`.

## 5. Seed Source Candidates (input queue for reharm:root)

| Priority | Source | Notes |
|---|---|---|
| 1 | <note / URL / file> | |

## 6. Toggles & Status

- Web search: enabled <!-- or: disabled -->
- Source policy: prefer peer-reviewed / official docs / primary sources; do not cite social media, forums, or undated pages as high-confidence <!-- edit per domain; scopes the §6 evidence lens -->
- Experiment runner (optional): `<external runner entry point, e.g. /autoresearch:plan>` — the field-experiment designer hands off here (EVOLUTION.md §12). Leave blank to use the plugin's default runner-worker: the designer records its worker-doc path per node at design time (recorded, never inferred).
- Research escalation: <!-- external deep-research entry point (EVOLUTION.md §13) — leave unset to keep the bridge closed; pushing only recommends escalation when this is set -->
- Allowed external wikilinks: (none) <!-- comma-separated stems (e.g. 볼트노트, [[다른스코프노드]]) that are deliberate cross-scope citations; wiki-lint reports them as allowed_external instead of unresolved noise -->
- <YYYY-MM-DD>: scope created. Nodes: 0.
