---
name: critique
description: "re:Harmoniz adjudication — gather the ambiguous backlog (open questions, stalled low-confidence nodes, unresolved contradictions, lint warnings) and resolve it through a user interview. Triggers: reharm critique, critique the wiki, 모호한 것 정리, 노드 리뷰, adjudicate"
---

# reharm:critique — User Adjudication of the Ambiguous Backlog

Collects what the evolution loop could not resolve on its own and puts it in front of the user as concrete choices. **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root); §2, §3 govern what user verdicts may change.**

## Procedure

1. **Resolve the scope**, then gather the backlog:
   - everything in `wiki/questions/`
   - claims at `confidence: low` that appear in neither of the last two `E####.md` reports' Mutations/Promotions sections (= two sessions without generation movement)
   - unresolved `> [!contradiction]` callout pairs
   - warnings from the latest `wiki/meta/lint/` report
2. **Bundle** by theme; per item prepare a one-line summary and 2–4 concrete verdict options.
3. **Interview**: present one item at a time (AskUserQuestion-style options). "Defer" is always a valid answer and leaves the item untouched.
4. **Apply verdicts**:
   - adopt/reject → update body and frontmatter (`confidence`, `status`); on contradiction resolution remove both callouts and absorb the history into `## Objections & Limits`
   - deprecate → flip `status` (never delete)
   - needs-research → rewrite as a sharpened question in `wiki/questions/` (next reharmonization session's Phase B candidate)
5. **Close out**: `index.md`, `hot.md`, `log.md` (`## [date] critique | N verdicts`).

## Constraints

- **User verdicts never raise `generation`** — generations are earned only by surviving adversarial verification (reharmonization Phase D). Verdicts may adjust `confidence` and `status`.
- No auto-adjudication without the interview — converging on the user's judgment is this skill's entire purpose.
