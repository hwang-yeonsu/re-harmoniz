---
name: reharmonization
description: "re:Harmoniz evolution session — one full cycle of Retrospect → Target → Mutate → Select → Record. Nodes are hammered with refutations; only survivors gain a generation. Triggers: reharm reharmonization, reharmonize the wiki, evolve the wiki, 진화 세션, 진화 돌려, run evolution"
---

# reharm:reharmonization — Evolution Session (5 Phases, One Cycle)

**Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) and follow §4 (protocol), §5 (adversarial rubric), §6 (web policy), §7 (evaluation), §11 (templates) exactly.** This skill is the entry point; the protocol is the engine. On conflict, EVOLUTION.md wins.

## Procedure (summary of §4)

1. **Resolve the scope**, read scope `CLAUDE.md`.
2. **Phase A — Retrospect**: read the latest `wiki/meta/evolution/E####.md` + `hot.md`; adversarially re-verify last session's changed nodes; roll back or demote collapses. Start from failing checks if the last `E####.eval.json` failed.
3. **Phase B — Target Selection**: ① `python3 "${CLAUDE_SKILL_DIR}/../../scripts/boundary-score.py" --json --top 5` from the scope root (it reads `./wiki/`) ② decay candidates: compare frontmatter `last_challenged` dates against the §3 cadence ③ user-named topics first. **Present the merged candidates and let the user choose — never auto-select.**
4. **Phase C — Mutation**: decompose new `.raw/` material into existing nodes; **field-origin results (`.raw/experiments/`) import into the target's `## Field Evidence` with their conditions — not into Objections; external material is seed (§4)**; hunt evidence/counterexamples via web search within §6 bounds; contrast adjacent nodes → `mashups/`.
5. **Phase D — Natural Selection**: three refuters per mutation (coherence / evidence / reproducibility; refutation is the default), pass on ≥2/3 survival → `generation +1`, `challenges_survived +1`, refresh `last_challenged`, propose promotions per §3. Partial collapse → absorb into `## Objections & Limits`, re-judge. Total collapse → `status: deprecated`.
6. **Phase E — Record**: write `E####.md` report (§11.1 template) → overwrite `hot.md` → update `index.md` (§11.2 census) → prepend `log.md` → lint via `python3 "${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py" --json` from the scope root (findings → `wiki/meta/lint/`) → write `E####.eval.json` with stagnation verdict (§7).

## Constraints

- One session = one cycle = one scope. No multi-scope evolution.
- No change history inside node bodies — process belongs to the report, results to the node.
- Never modify `.raw/`. Never create branches, PRs, or git tags — the repo's auto-commit owns git history; the `E####.md` report is the session boundary.
- Verification is allowed to take long — do not rush Phases A and D.
