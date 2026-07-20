---
name: reharmonization
description: "re:Harmoniz evolution session — one full cycle of Retrospect → Target → Mutate → Select → Record. Nodes are hammered with refutations; only survivors gain a generation. Triggers: reharm reharmonization, reharmonize the wiki, evolve the wiki, 진화 세션, 진화 돌려, run evolution"
---

# reharm:reharmonization — Evolution Session (5 Phases, One Cycle)

**Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) and follow §4 (protocol), §5 (adversarial rubric), §6 (web policy), §7 (evaluation), §11 (templates) exactly.** This skill is the entry point; the protocol is the engine. On conflict, EVOLUTION.md wins.

## Procedure (summary of §4)

1. **Resolve the scope**, read scope `CLAUDE.md`.
2. **Phase A — Retrospect**: read the latest `wiki/meta/evolution/E####.md` + `hot.md`; adversarially re-verify last session's changed nodes; **for mashups carrying `borrowed:` (§2), compare each donor node's current status/generation against the snapshot — drift is a new objection to absorb**; roll back or demote collapses. Start from failing checks if the last `E####.eval.json` failed.
3. **Phase B — Target Selection**: ① `python3 "${CLAUDE_SKILL_DIR}/../../scripts/boundary-score.py" --json --top 5` from the scope root (it reads `./wiki/`) ② decay candidates: compare frontmatter `last_challenged` dates against the §3 cadence ③ user-named topics first. **Present the merged candidates and let the user choose — never auto-select.**
4. **Phase C — Mutation**: decompose new `.raw/` material into existing nodes; **field-origin results (`.raw/experiments-results/`) import into the target's `## Field Evidence` with their conditions — not into Objections; external material is seed (§4)**; hunt evidence/counterexamples via web search within §6 bounds; contrast adjacent nodes → `mashups/`.
5. **Phase D — Natural Selection**: per mutation, spawn **three isolated refuter sub-agents in parallel** (coherence / evidence / reproducibility; refutation is the default). Resolve the **absolute** paths of the worker doc (`${CLAUDE_SKILL_DIR}/refuter.md`) and `EVOLUTION.md` (`${CLAUDE_SKILL_DIR}/../../EVOLUTION.md`) — e.g. with `realpath` — and spawn each sub instructed to "read `<abs refuter.md path>` and follow it," passing inline: its one lens, the target node verbatim (frontmatter + body), the cited `wiki/sources/` page originals, and the lens material refuter.md lists. **Never pass the session's mutation narrative** (§5 isolation). Pass on ≥2/3 survival → `generation +1`, `challenges_survived +1`, refresh `last_challenged`, propose promotions per §3 (the developing→hardened currency is class-calibrated — §2 `evidence_class`). Partial collapse → absorb into `## Objections & Limits` by **rewriting the section to the current set** (§2: compress each objection to its ≤2-line boundary condition; the refuter's full reason is archived in the E#### report), revise, **re-spawn the same lens workers** to re-judge. Total collapse → `status: deprecated`. If spawning is unavailable, degrade to three in-context sequential judgments and record `refuters ran non-isolated` in the E#### report (§5 fail-loud).
6. **Phase E — Record**: write `E####.md` report (§11.1 template **and its length discipline**: target ≤40 lines; verdicts one line per node, reason clauses only for refuted lenses and re-judgings) → overwrite `hot.md` → update `index.md` (§11.2 census) → prepend a **one-line** `log.md` entry → lint via `python3 "${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py" --json` from the scope root (findings → `wiki/meta/lint/`) → write `E####.eval.json` with stagnation verdict (§7).

## Constraints

- One session = one cycle = one scope. No multi-scope evolution.
- No change history inside node bodies — process belongs to the report, results to the node.
- Never modify `.raw/`. Never create branches, PRs, or git tags — the repo's auto-commit owns git history; the `E####.md` report is the session boundary.
- Verification is allowed to take long — do not rush Phases A and D.
