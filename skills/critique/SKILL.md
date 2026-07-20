---
name: critique
description: "re:Harmoniz adjudication — gather the ambiguous backlog (open questions, stalled low-confidence nodes, unresolved contradictions, lint warnings) and resolve it through a user interview. Triggers: reharm critique, critique the wiki, 모호한 것 정리, 노드 리뷰, adjudicate"
---

# reharm:critique — User Adjudication of the Ambiguous Backlog

Collects what the evolution loop could not resolve on its own and puts it in front of the user as concrete choices. **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root); §2, §3 govern what user verdicts may change.**

## Procedure

1. **Resolve the scope**, then gather the backlog:
   - everything in `wiki/questions/` (any `status`, legacy values included)
   - claims at `confidence: low` that appear in neither of the last two `E####.md` reports' Mutations/Promotions sections (= two sessions without generation movement)
   - unresolved `> [!contradiction]` callout pairs
   - warnings from the latest `wiki/meta/lint/` report
   - **aged open questions**: `status: open` (or legacy-status) questions untouched for ≥4 sessions — they appear in none of the last 4 `E####.md` reports and their `updated` predates all four.
   - **inert seeds**: `status: seed` claims with `challenges_survived: 0` untouched for ≥3 sessions (in none of the last 3 `E####.md` reports) — merge/archive candidates: most are details or premises of a stronger sibling, inflating the census without earning their index row.
2. **Bundle** by theme; per item prepare a one-line summary.
3. **Batch triage per bundle** (multiSelect, at most two passes) — the default for homogeneous bundles:
   - Pass ① **promote**: multi-select the items to act on now — adopt / reject / **merge into a parent claim** / sharpen into a Phase B candidate; a question may be promoted to `status: escalated` when the scope's `Research escalation:` toggle is set (write its `## Escalation` block per §13: *what would change our mind*).
   - Pass ② **archive**: among the rest, multi-select the items to retire — questions flip to `status: archived` (a status flip, never a delete).
   - Anything unpicked in both passes = **hold** (the old "Defer": untouched).
   Genuinely ambiguous single items — contradiction pairs above all — keep the one-at-a-time interview with 2–4 concrete verdict options.
4. **Aging batch (never automatic)**: if aged open questions exist, present them as **one** multiSelect "archive these?" question. Only the user-picked ones flip to `archived`; unpicked ones stay `open` and untouched. The skill may propose, never decide.
5. **Apply verdicts**:
   - adopt/reject → update body and frontmatter (`confidence`, `status`); on contradiction resolution remove both callouts and absorb the history into `## Objections & Limits`
   - merge → absorb the claim into the parent it details or duplicates: union `sources:`, fold the assertion into the parent's body, `## Objections & Limits`, or `## Field Evidence` (whichever it is); the absorbed node's body becomes a one-line pointer — `Absorbed into [[parent]] (YYYY-MM-DD critique)` — and its `status` flips to `deprecated` (§3: never delete; the stem keeps resolving inbound links). A `> [!contradiction]` pair is **adjudicated, never merged**.
   - deprecate → flip `status` (never delete)
   - needs-research → rewrite as a sharpened question in `wiki/questions/` (`status: open`; next reharmonization session's Phase B candidate)
   - escalate → flip the question to `status: escalated` + `## Escalation` block (§13 DESIGN); the user carries it to the external tool
   - archive → question `status: archived`
6. **Close out**: `index.md`, `hot.md`, `log.md` (`## [date] critique | N verdicts`).

## Constraints

- **User verdicts never raise `generation`** — generations are earned only by surviving adversarial verification (reharmonization Phase D). Verdicts may adjust `confidence` and `status`.
- No auto-adjudication without the interview — converging on the user's judgment is this skill's entire purpose. Aging in particular only ever *proposes* an archive batch.
- New question statuses use the §2 lifecycle (`open|answered|escalated|archived`); legacy maturity values on existing questions are left alone unless the verdict touches that node.
