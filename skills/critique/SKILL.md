---
name: critique
description: "re:Harmoniz adjudication and pruning — gather the ambiguous backlog (open questions, stalled low-confidence nodes, unresolved contradictions, lint warnings) plus the prune queue (nodes bearing on no open decision) and resolve both through a user interview. Triggers: reharm critique, critique the wiki, prune the wiki, 모호한 것 정리, 가지치기, 노드 리뷰, adjudicate"
---

# reharm:critique — User Adjudication of the Ambiguous Backlog

Collects what the evolution loop could not resolve on its own and puts it in front of the user as concrete choices — both the ambiguous residue *and* the branches that stopped mattering. **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root); §1 (the goal/decision block), §2, §3 (incl. `pruned`) govern what user verdicts may change.**

## Procedure

1. **Resolve the scope**, read its `### Goal & Open Decisions` block (§1), then gather the backlog:
   - everything in `wiki/questions/` (any `status`, legacy values included)
   - claims at `confidence: low` that appear in neither of the last two `E####.md` reports' Mutations/Promotions sections (= two sessions without generation movement)
   - unresolved `> [!contradiction]` callout pairs
   - warnings from the latest `wiki/meta/lint/` report
   - **aged open questions**: `status: open` (or legacy-status) questions untouched for ≥4 sessions — they appear in none of the last 4 `E####.md` reports and their `updated` predates all four.
   - **the re-binding queue (§1)** — the lint `stale_serves_target` list: nodes bound to a decision that is now `superseded` (the question was reframed or split, not answered). These are **not** prune candidates; they are the queue that gets re-pointed at the successor decision first.
   - **the prune queue (§3)** — the branches, not the residue. Three sources, each with its own reason:
     - **unassigned** — the lint `unassigned_claims` list: evolving nodes with no `serves:` while the scope has open decisions.
     - **served-out** — nodes whose `serves:` names only `settled` decisions. Nothing is waiting on them any more.
     - **superseded** — nodes an owner design decision closed out (reharmonization Phase C reports these; they arrive here for the ruling).
   - **inert seeds**: `status: seed` claims with `challenges_survived: 0` untouched for ≥3 sessions — merge candidates. Judge them by **relevance first**: a seed nothing is waiting on is a *prune* candidate, not a merge candidate. Merge is for a seed that does serve an open decision but is really a detail or premise of a stronger sibling.
2. **Bundle** by theme; per item prepare a one-line summary.
3. **Batch triage per bundle** (multiSelect, at most two passes) — the default for homogeneous bundles:
   - Pass ① **promote**: multi-select the items to act on now — adopt / reject / **merge into a parent claim** / sharpen into a Phase B candidate; a question may be promoted to `status: escalated` when the scope's `Research escalation:` toggle is set (write its `## Escalation` block per §13: *what would change our mind*).
   - Pass ② **archive**: among the rest, multi-select the items to retire — questions flip to `status: archived` (a status flip, never a delete).
   - Anything unpicked in both passes = **hold** (the old "Defer": untouched).
   Genuinely ambiguous single items — contradiction pairs above all — keep the one-at-a-time interview with 2–4 concrete verdict options.
4. **Aging batch (never automatic)**: if aged open questions exist, present them as **one** multiSelect "archive these?" question. Only the user-picked ones flip to `archived`; unpicked ones stay `open` and untouched. The skill may propose, never decide.
   **Prune batch (never automatic)**: present the prune queue as **one** multiSelect grouped by reason, each item one line — node, its current status/generation, and why it is a candidate. Only the user-picked ones flip to `status: pruned`; unpicked ones stay exactly as they are. Two things to say out loud when presenting it, because both are easy to get wrong:
   - **Pruning is not a judgement on the claim.** A node at `hardened · g5` can be pruned; the question is only whether an open decision still rests on it.
   - **An unassigned node may be a binding gap, not a dead branch.** Offer *bind to a decision* alongside *prune* for those, and take the binding when the user names one — a missing `serves:` is often just a node minted before the decision existed.
5. **Apply verdicts**:
   - adopt/reject → update body and frontmatter (`confidence`, `status`); on contradiction resolution remove both callouts and absorb the history into `## Objections & Limits`
   - merge → absorb the claim into the parent it details or duplicates: union `sources:`, fold the assertion into the parent's body, `## Objections & Limits`, or `## Field Evidence` (whichever it is); the absorbed node's body becomes a one-line pointer — `Absorbed into [[parent]] (YYYY-MM-DD critique)` — and its `status` flips to `deprecated` (§3: never delete; the stem keeps resolving inbound links). A `> [!contradiction]` pair is **adjudicated, never merged**.
   - deprecate → flip `status` (never delete)
   - **prune** → flip `status: pruned` and append the one-line reason to the body, **opening with the status being cut from**: `Pruned from <seed｜developing｜hardened｜evergreen>: <unassigned ｜ all served decisions settled ｜ superseded by [[source]]> (YYYY-MM-DD)` (§3). That prefix is the restore point — without it the reversibility below is only recoverable from git, and `wiki-lint.py` reports its absence as `prune_without_restore_point`. The body is otherwise left verbatim, the node keeps its `generation`, and inbound wikilinks keep resolving. **Reversible**: if the decision reopens, the node flips back to the status that line names. Never confuse this with `deprecate` — `deprecated` says the claim failed, `pruned` says nothing depends on it
   - **bind** → the node was unassigned only because its `serves:` was never written: add the decision ID the user names and leave everything else alone (it re-enters the cadence next session)
   - **re-bind** → the node's `serves:` names a `superseded` decision: replace that ID with the successor the user picks (a split may send siblings to different successors). Nothing else about the node changes. Only a node no successor claims falls through to the prune batch, and then as *unassigned*
   - needs-research → rewrite as a sharpened question in `wiki/questions/` (`status: open`; next reharmonization session's Phase B candidate)
   - escalate → flip the question to `status: escalated` + `## Escalation` block (§13 DESIGN); the user carries it to the external tool
   - archive → question `status: archived`
6. **Move a decision's row when a ruling moves it** — always with the user's confirmation, since that row is theirs:
   - **settled** — a verdict answers the decision outright. Its serving nodes become next-session prune candidates, which is the point.
   - **superseded** — the ruling shows the decision was the wrong question: too broad, badly framed, or made moot (§1). Never delete the row and never reuse its ID — mark it `superseded`, write the successor into its text (`→ D4, D5`, or `→ none: moot because …`), add the successor rows, then run the **re-bind** verdict above on every node the lint lists under `stale_serves_target`. Splitting an over-broad decision is this path, not a rewrite in place.
   - **reopened** — a `settled` decision goes back to `open` (the ruling did not hold, conditions changed). Then walk the nodes pruned under it: each one's `Pruned from <status>:` line names what to flip it back to (§3).
7. **Close out**: `index.md` (Decisions table + census incl. `pruned` + `Serves` column), `hot.md`, `log.md` (`## [date] critique | N verdicts · M pruned`).

## Constraints

- **User verdicts never raise `generation`** — generations are earned only by surviving full-depth adversarial verification (reharmonization Phase D, §5.1). Verdicts may adjust `confidence` and `status`.
- **Pruning never edits the claim.** Status flip plus a one-line reason carrying the restore point; the body, its objections, and its generation stay as they were. A pruned node is a record, not a correction.
- **A decision ID is permanent.** Retire a decision with `superseded` and leave its row in place; never delete a row so a new decision can take the name. Recycling an ID silently re-points every existing `serves:` at a decision it was never about — `wiki-lint.py` reports the collision as `duplicate_decision_id`.
- No auto-adjudication without the interview — converging on the user's judgment is this skill's entire purpose. Aging and pruning in particular only ever *propose* a batch.
- New question statuses use the §2 lifecycle (`open|answered|escalated|archived`); legacy maturity values on existing questions are left alone unless the verdict touches that node.
