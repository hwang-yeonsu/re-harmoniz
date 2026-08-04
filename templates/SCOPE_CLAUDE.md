# Research_<TOPIC> — Research Scope

## 1. Purpose & Boundaries

<One paragraph: what this scope researches, and what is explicitly out of scope.>

### Goal & Open Decisions

<!-- EVOLUTION.md §1/§10 — the block every relevance rule reads. Target selection (§4 Phase B),
     verification depth (§5.1), the pruning sweep (§4 Phase C) and the §7 progress counters are all
     measured against these rows. Keep them current: settling a decision means flipping its Status,
     which is what lets the next session prune the branches it carried. -->

**Goal:** <one line: what acting on this research would accomplish>

| ID | Decision to settle | Status |
|---|---|---|
| D1 | <a decision taken OUTSIDE the wiki — a design choice, a build/deploy step, a spend, a guardrail> | open |

<!-- Rules of thumb:
     · A decision is something you DO, not something the wiki records. "The claim reaches hardened"
       is bookkeeping, not a decision.
     · Statuses are `open`, `settled`, and `superseded`. Anything else reads as open, so a typo can
       never retire a decision by accident. The same holds for the row's shape: extra columns are
       ignored, only the status cell's FIRST WORD is read (`open (2026-07 재확인)` is fine), and a row
       the linter still cannot read is reported (`unparsed_decision_rows`) rather than dropped — a
       dropped row would retire its decision and put every claim serving it on the prune queue.
     · `superseded` is for a decision that stopped being the RIGHT QUESTION — reframed, split, or made
       moot — as opposed to one that was answered. Leave its row here, write the successor into its
       text (`→ D4, D5`, or `→ none: moot because …`), and re-bind its claims via /reharm:critique.
     · NEVER delete a row to reuse its ID. Every `serves: D1` in the wiki would silently re-point at
       the new decision; wiki-lint reports the collision as `duplicate_decision_id`.
     · Start with one if that is all you have. Starting with none leaves the loop unsteered, and
       wiki-lint reports it (`no_decisions_declared`) once evolving nodes exist.
     · Claims bind to these IDs via `serves:` (§2). A claim bound to nothing is a prune candidate,
       not an error — but a scope full of them means atomization outran the decisions. -->

## 2. Metadata (the scope is not a code workspace)

- **Code workspace path(s): `<absolute path — fill in>`**
- Experiment lane: experiment reports produced in the workspace land in this scope's `.raw/experiments-results/` (the field-origin convention) and re-enter through `reharm:root`; `reharm:reharmonization` Phase C imports their conclusions — with the conditions they held under — into the relevant claim's `## Field Evidence` (the evergreen gate). External material (papers, web, repos) lands elsewhere under `.raw/` and is treated as seed.
- Deep-research lane: reports returning from a §13 escalation land in `.raw/deep-research/` and re-enter through `reharm:root` (their `sources/` pages are `origin: secondary` with `derived_from:` ancestry).
- These lane declarations are **canonical** (EVOLUTION.md §1): skills route results by what this section declares, so a legacy lane name (e.g. `.raw/experiments/`) stays valid in a scope that declares it here.

## 3. Protocol

- This scope follows the **re:Harmoniz protocol** (`reharm` plugin, `EVOLUTION.md`): node schema, maturity state machine, 5-phase evolution sessions, report templates.
- `.raw/` is immutable. Frequent revision of wiki nodes is encouraged.
- Unsure what to do next here? Run `/reharm:pushing` (read-only) — it reads this scope's decisions and state, then recommends the next skill (declare the goal / seed / evolve / adjudicate / prune / answer).

## 4. Adversarial Verification (applies to any research loop running in this scope)

- Every claim carries explicit confidence: high (multiple independent sources agree) / medium (single good source) / low (speculation, unverified).
- **Verification depth follows decision role (EVOLUTION.md §5.1)** — spend the full pass only where a decision rests on the node:
  - **load-bearing for an open decision** (flipping it changes which way the decision goes) → all three lenses (coherence / evidence / reproducibility), pass only if **≥2 of 3** fail to refute it.
  - **serves an open decision but is not load-bearing** → **one** lens, chosen by `evidence_class`: `literature`→evidence, `field`→reproducibility, `design`→coherence. Earns currency and a refreshed `last_challenged`, but no generation, and cannot pass the `hardened` gate.
  - **bears on no open decision** → not verified at all; it is a prune candidate (§3).
- When uncertain, refute. Refuters judge in isolation and never see the mutation narrative — or which depth they are running at.
- Valid objections are never discarded — absorb them into the node's `## Objections & Limits`, kept compressed to the *current* set (≤2 lines each; resolved objections live on in the session report and git — EVOLUTION.md §2). A node is re-judged **at most once per session** after absorbing; residue becomes an open question rather than another round.

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
