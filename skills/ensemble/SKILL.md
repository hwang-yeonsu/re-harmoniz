---
name: ensemble
description: "re:Harmoniz answer synthesis — assemble what survived (hardened claims, mashups) into ONE citable deliverable that answers the scope's central question, every load-bearing sentence wired to its node with a status·confidence·generation snapshot, confidence set by the weakest link. Writes only wiki/deliverables/ + close-out files; node states never change. Triggers: reharm ensemble, synthesize the answer, answer the central question, write the deliverable, 답변 합성, 결론 합성, 앙상블"
---

# reharm:ensemble — Answer Synthesis (deliverable)

The ensemble finale: every voice that survived rehearsal plays the theme together. The evolution loop hardens *claims*; this skill is the **exit** — it assembles the survivors into one `wiki/deliverables/` page that answers the scope's central question, with every load-bearing sentence wired back to the node that carries it. Nodes are cited, never changed.

**Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) and follow it.** Key sections: §14 (the deliverable protocol — body contract, confidence floor, update-in-place), §2 (the `deliverable` schema and node schemas), §11.2 (the index Deliverables table), §8 (git owns versions).

## Procedure

1. **Resolve the scope** (`.raw/` + `wiki/` present); read the scope `CLAUDE.md` and `overview.md`.
2. **Fix the question.** Take it from the arguments; else propose candidates — the scope's central question (from `overview.md` / the `CLAUDE.md` purpose paragraph) and the `wiki/questions/` nodes most linked from hardened claims — and **let the user confirm**. The question is the deliverable's identity (§14): it is never guessed silently. If a deliverable for that question already exists, this run **updates it in place** — never a second file.
3. **Collect (read-only).** Gather the claims/mashups that bear on the question: start from the question node's wikilinks, `index.md`, and the lint JSON `status_census`; read the relevant `hardened`/`evergreen` nodes in full and `developing`/`seed` ones as needed. Record each cited node's **(status · confidence · generation) at synthesis time** — these snapshots go into the text.
4. **Synthesize** `wiki/deliverables/<question-slug>.md` per the §2 deliverable schema (`type: deliverable`, `title`, `created`, `updated`, `question: "[[…]]"`), body per the §14 contract, in the scope's content language:
   - `## Answer` — **opens with a bottom line** (§14): at most 3 plain-language lines — verdict, the condition it rides on, next action — a practitioner can act on alone; the justifying synthesis follows. Every load-bearing sentence cites its node inline with the snapshot: `…conclusion… ([[node]] hardened · high · g6)`.
   - `## Load-bearing seeds` — the seed/developing nodes the answer leans on despite their immaturity, each with its snapshot. Listed, not hidden.
   - `## Open caveats` — unresolved objections, contradictions, open questions that bound the answer.
   - `## What would change this conclusion` — the evidence or counterexample that would force a rewrite (§13's discipline applied to the whole answer).
5. **Confidence propagation header.** Directly under the H1: `**Confidence:** <floor> — floor set by the weakest load-bearing claim: [[node]] (status · confidence · gen)`. The floor is **derived, never asserted**: it equals the minimum confidence among load-bearing citations, where **load-bearing = verdict-changing** (§14) — a claim whose negation would change a verdict sentence, exactly the set `## What would change this conclusion` enumerates. Background citations never set the floor. Multi-axis answers may add a per-axis floor line under each axis section; the header keeps the minimum across axes.
6. **Close out**: update `index.md` (§11.2 — add/refresh the **Deliverables** table row; deliverables never enter the maturity census), overwrite `hot.md`, prepend a `log.md` entry (`## [date] ensemble | <question>`).
7. **Lint**: from the scope root run `python3 "${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py" --json`; expect `clean: true` (the new page must carry the §2 deliverable keys and resolvable wikilinks).

## Constraints

- **Node states are invariant.** This skill writes `wiki/deliverables/` plus the three close-out files (`index.md` / `hot.md` / `log.md`) and **nothing else** — no claim, mashup, question, or experiment is edited; no `status` / `confidence` / `generation` moves anywhere. Even flipping the answered question to `status: answered` belongs to critique/reharmonization, not here.
- **Update-in-place, one deliverable per question.** A re-run overwrites the same file and bumps `updated`; git owns the version history (§8). Never mint `-v2` files.
- **A deliverable never evolves** (§14): no generation, no refuters, excluded from frontier scoring and the census. It is a snapshot synthesis, re-derived at will — the evolving truth stays in the nodes.
- **No confidence optimism.** The header floor is the minimum over load-bearing citations; no sentence may claim more certainty than the node it cites.
- **No new research.** Ensemble synthesizes what is already in the wiki — no web search, no `.raw/` reading, no new claims. Gaps it exposes belong in `## Open caveats` (and, next session, in `questions/`).
