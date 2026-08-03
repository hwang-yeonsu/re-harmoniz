---
name: ensemble
description: "re:Harmoniz answer synthesis — assemble what survived into ONE citable deliverable that answers a declared decision (or the scope's central question), every load-bearing sentence wired to its node with a status·confidence·generation snapshot, confidence set by the weakest link. Run it as soon as the decision can be taken, not when the census looks impressive. Writes only wiki/deliverables/ + close-out files; node states never change. Triggers: reharm ensemble, synthesize the answer, answer the decision, write the deliverable, 답변 합성, 결론 합성, 앙상블"
---

# reharm:ensemble — Answer Synthesis (deliverable)

The ensemble finale: every voice that survived rehearsal plays the theme together. The evolution loop hardens *claims*; this skill is the **exit** — it assembles the survivors into one `wiki/deliverables/` page that answers the scope's central question, with every load-bearing sentence wired back to the node that carries it. Nodes are cited, never changed.

**Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) and follow it.** Key sections: §14 (the deliverable protocol — body contract, confidence floor, update-in-place), §2 (the `deliverable` schema and node schemas), §11.2 (the index Deliverables table), §8 (git owns versions).

## Procedure

1. **Resolve the scope** (`.raw/` + `wiki/` present); read the scope `CLAUDE.md` and `overview.md`.
2. **Fix what it answers.** Take it from the arguments; else propose candidates — the scope's **open declared decisions** (§1) first, since a decision is what someone is actually waiting on, then the scope's central question (from `overview.md` / the `CLAUDE.md` purpose paragraph) and the `wiki/questions/` nodes most linked from hardened claims — and **let the user confirm**. That identity goes in `question:` as a decision ID or a question wikilink (§14): it is never guessed silently. If a deliverable for it already exists, this run **updates it in place** — never a second file.
3. **Collect (read-only).** Gather the claims/mashups that bear on it: for a decision, start from the nodes whose `serves:` names it (`boundary-score.py --json --serves <ID>` lists them cheaply); for a question, from its wikilinks. Then `index.md` and the lint JSON `status_census`; read the relevant `hardened`/`evergreen` nodes in full and `developing`/`seed` ones as needed. Skip `pruned` and `deprecated` nodes — both have left the graph (§3); if the answer seems to need one, that is a signal the prune was wrong, so say so in `## Open caveats` rather than quietly citing it. Record each cited node's **(status · confidence · generation) at synthesis time** — these snapshots go into the text.
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
- **Run early rather than late.** The threshold is whether a practitioner could act from the bottom line with the caveats stated — not a node count and not a maturity level (§14). A provisional answer leaning on `developing` nodes, with its soft spots under `## Load-bearing seeds` and an honest confidence floor, is more useful than no answer: it exposes exactly which branch the next session should take. Re-run it as the core hardens.
- **Settling the decision is not this skill's call.** Writing the answer does not flip a decision's row to `settled` in the scope `CLAUDE.md` — that is the user's ruling, via `critique`. Say plainly in the report that the decision now looks settleable; do not settle it.
- **No confidence optimism.** The header floor is the minimum over load-bearing citations; no sentence may claim more certainty than the node it cites.
- **No new research.** Ensemble synthesizes what is already in the wiki — no web search, no `.raw/` reading, no new claims. Gaps it exposes belong in `## Open caveats` (and, next session, in `questions/`).
