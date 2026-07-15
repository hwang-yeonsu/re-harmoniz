---
name: pushing
description: "re:Harmoniz next-step advisor — read-only. Inspects the current wiki + evolution state of a scope and recommends which skill to run next (root / reharmonization / critique / modal-interchange / experiment-design / ensemble, or a deep-research escalation), with the evidence that triggered it. Changes nothing and runs nothing; you decide. Triggers: reharm pushing, what next, what should I do next, where do I stand, next move, 다음 뭐 해, 다음 스텝, 뭐부터 할까, 상태 봐줘"
---

# reharm:pushing — Next-Step Advisor (read-only)

The anticipation beat — like *pushing* a note ahead of the bar, this looks at where a scope stands and calls the next move before you have to ask: seed (`root`), evolve (`reharmonization`), resolve ambiguity (`critique`), design the experiment (`experiment-design`), escalate stuck evidence (§13 deep research), synthesize the answer (`ensemble`), or borrow across scopes (`modal-interchange`).

**This is the only read-only skill: it inspects and recommends, never writes a file, never runs another skill.** That preserves the protocol's contract — nothing is auto-decided; you pick the targets and adjudicate (EVOLUTION.md §3, §4 Phase B). **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md`** for the state definitions it reads: §3 (maturity + re-verification cadence), §7 (session evaluation + stagnation).

## Procedure

1. **Resolve the scope** (`.raw/` + `wiki/` present). If the cwd is not a scope, take the path from arguments or ask once. If no scope exists at all → recommend `reharm:root` and stop.
2. **Gather state** — every signal already exists (§8); all reads, no writes:
   - **Frontier**: `python3 "${CLAUDE_SKILL_DIR}/../../scripts/boundary-score.py" --json --top 5` from the scope root. Positive-`score` pages are evolution-ready (outward-pointing, recently touched). Each row also exposes `status` / `generation` / `challenges_survived` / `sources_count` — the evidence-gate surface the escalation signal below reads.
   - **Health**: `python3 "${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py" --json` from the scope root. Read `clean` and `counts` (`contradictions`, `orphans`, `dead_wikilinks`, `missing_frontmatter`, `duplicate_stems`).
   - **Census**: `status_census` in the lint JSON above — the **computed** node totals per status (claims + mashups). The `**Census:**` line in `wiki/index.md` is display-only; a `census_drift` warning in the same JSON means the display line needs a refresh, never that the census signal is wrong.
   - **Last session**: the newest `wiki/meta/evolution/E####.eval.json` — `pass` and `stagnation.verdict` (`continue` / `reseed` / `change-strategy`).
   - **Decay**: node frontmatter `last_challenged` vs the §3 cadence (seed/developing every session, hardened 4 weeks, evergreen 12 weeks). Scopes are small — read dates directly, no script.
   - **Unprocessed material**: `.raw/` files (recursively) with no matching `wiki/sources/` page.
   - **Stuck at the evergreen gate**: `status: hardened` nodes whose `## Field Evidence` is empty (filter by frontmatter status, then read just those bodies). Only the §2 code workspace can produce the real-world result they need.
   - **Stuck at the evidence gate (§13)**: `status: developing` claims with `sources_count` < 2 (from the boundary-score JSON) and no new independent source in the last 2 `E####.md` reports; plus `status: open` questions with no progress across the last 4 reports. Only signal-worthy when the scope `CLAUDE.md` sets `Research escalation:`.
   - **Borrowed drift**: mashups carrying a `borrowed:` snapshot (§2) whose donor node's **current** status/generation no longer matches it — read the donor scope's frontmatter directly (a demoted or deprecated donor means the mashup's premise moved).
   - **Deliverable state (§14)**: `wiki/deliverables/` pages and their `updated` vs the newest `E####.md` session date; plus the hardened-or-above count from `status_census`. An answered-in-pieces scope with no (or a stale) deliverable is a synthesis backlog.
   - **Sibling scopes**: count sibling directories that are also scopes (for the modal-interchange signal).
3. **Apply the cascade** — first match wins; surface lower matches as secondary candidates so the user sees the whole board:

   | # | Condition | Recommend |
   |---|---|---|
   | 1 | no scope / 0 evolving nodes | `root` — seed first |
   | 2 | `.raw/` material not yet atomized | `root` — atomize new material before evolving |
   | 3 | lint `clean:false` (contradictions, dead links, orphans, missing frontmatter) **or** `questions/` backlog **or** low-confidence nodes stalled ≥2 sessions | `critique` — clear structural/ambiguity debt before evolving |
   | 4 | last `eval.json` `pass:false` **or** borrowed-snapshot drift on a mashup | `reharmonization` — integrity first: Phase A resumes failing checks and absorbs borrowed drift before anything new is frozen or evolved |
   | 5 | `status: hardened` node(s) with empty `## Field Evidence` (stuck at the evergreen gate) | **design the experiment** — `reharm:experiment-design` pre-registers it (hypothesis + a CONFIRM/REFUTE criterion fixed before the run, §12); the runner then executes it in the §2 code workspace and the report lands in `.raw/experiments-results/` to evolve (field evidence is the only evergreen gate, §3). If a `planned`/`running` `type: experiment` node already exists for the claim, point at its handoff instead of re-designing. Read-only: a recommendation, not an action |
   | 6 | scope `CLAUDE.md` sets `Research escalation:` **and** (a `developing` claim stuck < 2 independent sources with no new independent source for ≥2 sessions, **or** an `open` question with no progress for ≥4 sessions) | **escalate to deep research** (§13) — recommend the DESIGN step: flip the question to `status: escalated` + write its `## Escalation` block ("what would change our mind"), typically via `reharm:critique`; the user runs the external tool named by the toggle and its report returns through `.raw/deep-research/` → `reharm:root`. **Manual-only: the autonomous loop template skips this row.** Read-only: a recommendation, not an action |
   | 7 | positive-score frontier, **or** nodes past their §3 cadence | `reharmonization` — momentum: evolve the frontier, re-verify decayed nodes |
   | 8 | stagnation `verdict:"reseed"` (counters flat, no new seeds/sources) | `root` — needs new raw material, not more churn |
   | 9 | stagnation `verdict:"change-strategy"` | `critique` — rethink targets, not the same loop |
   | 10 | ≥5 nodes at `hardened`-or-above (from `status_census`) **and** the central question's deliverable is absent or stale (`updated` predates the newest `E####.md` — §14) | `ensemble` — the answer exists in pieces with nowhere it lives; synthesize the deliverable |
   | 11 | ≥2 scopes and nothing above fired | `modal-interchange` — optional cross-scope mashup |
   | 12 | nothing pending | report **current**; show the soonest next re-verification date |

   **Why the gate-stuck rows (5–6) sit above the momentum row (7):** the frontier/cadence pair is near-always on in a living scope (seed/developing nodes re-verify *every session*), so anything below it starves — a `hardened` claim would wait indefinitely for its experiment. An experiment recommendation costs one action and its run is fire-and-return (it proceeds in parallel with later sessions), so taking it first delays momentum by a single step while unblocking the scope's endgame. Row 4 still outranks both: freezing a CONFIRM/REFUTE criterion on top of an unsound last session (§4 Phase A debt) would pre-register the wrong formulation. The one-live-experiment-per-claim rule (§12) keeps row 5 from monopolizing — while its experiment is `planned`/`running`, the row only points at the existing handoff.

4. **Report** in the user's language: the recommended skill, the **evidence** (the specific counts / candidate pages / verdict that triggered it), the exact command to run next, and any secondary candidates. Then stop — the user runs the chosen skill.

## Constraints

- **Read-only. Writes no file, edits no node, runs no other skill, touches no git state.** It is a recommendation, not an action — the user always chooses (EVOLUTION.md "nothing is auto-decided").
- **One scope per run** (mirrors reharmonization). Cross-scope comparison is `modal-interchange`'s job; pushing only *suggests* it when ≥2 scopes exist.
- **No new state file** — it derives everything from the two stdlib scripts plus `index.md` / `E####.eval.json` / frontmatter. If `wiki/` is missing, say so and recommend `root`.
- If two branches tie, present both and let the user pick — do not force a single answer.
