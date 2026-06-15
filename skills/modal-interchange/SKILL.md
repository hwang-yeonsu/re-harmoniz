---
name: modal-interchange
description: "re:Harmoniz cross-scope mashup — borrow knowledge across two research scopes and mint cross-domain insights, like borrowing chords from a parallel mode. Triggers: reharm modal-interchange, modal interchange, 모달 인터체인지, 크로스 매쉬업, cross-scope mashup"
---

# reharm:modal-interchange — Cross-Scope Mashup

Borrow chords (knowledge) from a parallel key (another scope). **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root); §1, §2 and the SSoT rule govern this skill.**

## Procedure

1. **Resolve both scopes**: scope A (where results will live — the requester) and scope B (the donor). Both must be research scopes.
2. **Cheap reconnaissance only**: read each scope's `hot.md` → `index.md`. No full crawl — drill into at most 3–5 candidate pages after shortlisting.
3. **Contrast**: shortlist pairs where ① the same problem meets different solutions ② one side's `## Objections & Limits` is answered by the other side's mechanism ③ claims directly contradict across scopes.
4. **Synthesize** adopted pairs into **scope A's `wiki/mashups/`**:
   - Frontmatter per EVOLUTION.md §2 with mandatory new-node defaults (`type: mashup`, `status: seed`).
   - Scope B's knowledge is **cited by wikilink only — never copied or moved** (single source of truth). Scope B's nodes are never edited.
   - `sources:` lists wikilinks to both originating nodes.
5. **Close out scope A**: `index.md`, `hot.md`, `log.md` (`## [date] modal-interchange | A×B`).

## Constraints

- New mashups are born `seed` — verification and promotion happen in the next `reharm:reharmonization` session.
- If no genuine crossover exists, do not force one: file "no interchange found + why" in scope A's `wiki/questions/` and stop.
- Meaningful only once ≥2 scopes exist.
