# EVOLUTION.md — The re:Harmoniz Protocol (v1.0)

> This is the single source of truth for how a research wiki evolves.
> The `reharm:*` skills are thin entry points; this protocol is the engine.
> System docs (this file, skills, README) are written in English. Scope content (notes, claims, reports) follows the user's language — Korean is expected and fully supported (§9).

**Core principle.** A scope exists to settle a fixed set of **decisions**, declared before the research starts (§1). Claims are the branches under those decisions; verification exists to **prune** the branches, not to establish truth for its own sake. Three moves drive a scope forward: **mutation** (revision), **natural selection** (refutation and culling of what is wrong), and **pruning** (cutting what no open decision depends on, however true it may be). Only nodes that survive refutation gain a generation, so what the wiki asserts stays reliable — but the measure of progress is the share of declared decisions that are settled, and the evidence behind them.

**What this is not.** It is not a truth engine. Splitting a mixed assertion into ever-finer propositions and grading each one raises a maturity number without moving a decision, and a proposition fine enough to be cleanly true is usually too fine to act on. Every gate below therefore asks the same question first — *which declared decision does this serve, and would settling it change what we do?* — and a node that cannot answer is pruned rather than hardened.

---

## 1. Scope Anatomy

A **research scope** is a self-contained folder anywhere (any directory tree):

```
<anywhere>/Research_X/
├── .raw/                     # immutable source documents (papers, clips, repo dumps)
│   ├── experiments-results/  # field-origin reports: the scope's own experiment/real-world results (§4 Phase C, §12)
│   └── deep-research/        # deep-research reports returning from a §13 escalation
├── .reharm-draft/            # transient reharm:root fan-out staging (emptied after promotion; outside the lint-scanned trees)
├── wiki/
│   ├── index.md              # master catalog + maturity census
│   ├── hot.md                # hot cache (~500 words, session continuity; overwritten each time)
│   ├── log.md                # append-only operations log (newest on top)
│   ├── overview.md           # scope-level summary
│   ├── sources/              # one summary page per source
│   ├── claims/               # ★ atomic knowledge nodes — the unit of evolution
│   ├── mashups/              # ★ synthesized insights (contrast / comparison / integration)
│   ├── questions/            # open questions, pending objections
│   ├── experiments/          # field-experiment pre-registrations (design records; never evolve — §2, §12)
│   ├── deliverables/         # answer syntheses — non-evolving snapshots of what survived (§2, §14)
│   └── meta/
│       ├── evolution/        # evolution session reports (E0001.md, E0002.md …)
│       └── lint/             # lint reports
└── CLAUDE.md                 # scope config incl. the goal/decision block below (template: templates/SCOPE_CLAUDE.md; required sections in §10)
```

### Goal & decisions — what the loop steers toward

Every scope declares, in its `CLAUDE.md` (§10), the **decisions it exists to settle** — one line each, with an ID:

```markdown
### Goal & Open Decisions

**Goal:** <one line: what acting on this research would accomplish>

| ID | Decision to settle | Status |
|---|---|---|
| D1 | Do we replace 32-bit Adam with 8-bit in the training config? | open |
| D2 | Do we need a stable-embedding layer before shipping? | settled |
| D3 | Which optimizer family do we standardize on? → split into D1, D5 | superseded |
```

A decision is **outside the wiki**: a design choice, a build/deploy step, a spend, a guardrail. "The claim reaches `hardened`" is not a decision — it is bookkeeping (the §12 rule, now applied scope-wide). Statuses are `open`, `settled`, and `superseded`; anything else reads as `open`, so a typo can never retire a decision by accident.

**When the decision itself changes.** Research routinely discovers that the question was wrong — too broad, badly framed, or made moot by something learned along the way. That outcome is neither `open` nor `settled`, and recording it as `settled` would leave a false record that the scope answered something it never did. It is **`superseded`**: the decision stopped being the right question. Three rules make it safe:

1. **The row stays.** A superseded decision is never deleted from the table — its text gains a pointer to whatever replaced it (`→ D1, D5`, or `→ none: moot because …`). This is what makes ID reuse impossible: recycling `D1` for a new decision would silently re-point every existing `serves: D1` at something it was never about. A repeated ID is reported as `duplicate_decision_id`.
2. **Its nodes are re-bound before they are judged dead.** A node whose `serves:` names a superseded decision is *not* an unassigned prune candidate — the successor is one row away. `wiki-lint.py` reports it separately as `stale_serves_target`, and `reharm:critique` offers *re-bind to the successor* first, pruning only what nothing took over.
3. **Reopening is a status flip, not a recovery job.** A `settled` decision may go back to `open` (the ruling did not hold, or conditions changed), and §3's pruned nodes flip back with it — which works only because every prune records the status it cut from (`Pruned from hardened: …`). Without that line the restore point exists only in git, so `wiki-lint.py` reports its absence as `prune_without_restore_point`.

Splitting is the common case, and it is just rules 1–2 applied together: mark the old decision `superseded → D4, D5`, add the two rows, re-bind each serving node to whichever successor it actually bears on. Nothing is deleted and no node loses its history.

Every evolving node may carry **`serves:`** (§2) — the decision IDs it bears on. That binding is what makes pruning possible:

- **Selection** (§4 Phase B) asks for the frontier *inside* one open decision, not across the whole scope: `boundary-score.py --serves D1`.
- **Verification depth** (§5) follows it: nodes load-bearing for an open decision get the full three-lens pass; the rest get one lens.
- **Pruning** (§3, §4 Phase C) cuts nodes bound to no open decision — `status: pruned`, which is *not* `deprecated`: the node was not refuted, it stopped mattering.
- **Progress** (§7) is counted in decisions settled and branches pruned, not in generations alone.

`serves:` is **optional**, so every pre-1.0.0 node stays valid with no migration. `wiki-lint.py` reports the gaps as warnings — `no_decisions_declared` (only once evolving nodes exist), `duplicate_decision_id`, `unknown_serves_target`, `stale_serves_target`, `prune_without_restore_point`, and `unassigned_claims`, the queue the pruning sweep works from — and never breaks `clean` over them. A scope that has not declared its decisions is not in violation; it is unconfigured, and every relevance rule above simply stays inert until it is.

### sources/ vs claims/ — the distinction that drives everything

| | `sources/` | `claims/` |
|---|---|---|
| What it is | A summary of **a document** — what this paper/article/note says | A **verifiable assertion** — what we currently believe is true |
| Cardinality | 1 source file → 1 page | N claims per source; 1 claim may cite M sources (N:M) |
| Mutability | Quasi-immutable (the document never changes) | **Evolves** — generation, absorbed objections, status promotion |
| Analogy | Witness testimony on record | The contested issue argued in court |

Only `claims/` and `mashups/` evolve. `sources/` pages exist so that claims can cite evidence without re-reading `.raw/`.

Rules: `.raw/` is read-only, never modified. Nodes stay 100–200 lines; split if a node covers two concepts. Update, don't duplicate.

**Result lanes are declared, not hardcoded.** The two `.raw/` result lanes above (`experiments-results/`, `deep-research/`) are the defaults. The scope `CLAUDE.md` §2 Metadata declaration is canonical: skills route results by what the scope declares, and a legacy lane name (e.g. the pre-0.6.0 `.raw/experiments/`) stays first-class in any scope that declares it — additive-only, no migration required.

### Root multi-source handling (fan-out)

When `reharm:root` seeds several sources at once, the main agent is an **orchestrator + synthesizer** that never loads a raw source body into its context. Each source is atomized by an isolated sub-agent; the main agent sees only file *paths* and the small, distilled draft claims the subs return. This is the **pollution-control invariant** — it stops one source's framing from leaking into another's claims, and it holds for a single source too (no count threshold).

- **Responsibility seam.** Sub-agent (one per source, isolated): land the source (`.raw/`, incl. the single-URL fetch under §6.2/§6.3 hygiene) → `sources/<x>.md` → draft claims under `.reharm-draft/<source-stem>/`. Main agent: normalize input to a source list, merge duplicate drafts and promote to `claims/`, wire supports/contradicts edges, file failed sources and per-source overflow candidates under `questions/`, write the single-file globals (`index/hot/log`), and lint. The split follows write contention: `sources/` is 1:1 and each sub owns its own draft dir (no collision), so only the N:M `claims/` and the global files are main-owned.
- **Draft staging is ephemeral and lint-invisible.** `.reharm-draft/` lives at the scope root, outside both `wiki/` and `.raw/` — the only trees `wiki-lint.py` scans — so even an aborted run's leftover drafts never count as nodes. The main agent empties it before fan-out and after promotion. This states the principle only; the detailed steps live in the `reharm:root` skill.

### Atomization is decision-gated

**A source becomes claims only where it bears on a declared decision.** For every assertion a source makes, ask: *if this flipped, would an open decision (§1) go the other way?* If yes it becomes a `claims/` node with `serves:` naming that decision. If no, it stays on the `sources/` page — recorded, citable, searchable, and free. A source page is not a lesser home; it is the right home for everything the decisions do not rest on.

This is the rule the whole protocol turns on, because atomization sets the cost of every later phase: each node minted here demands refuters, a re-verification cadence, and an index row for the rest of the scope's life. Splitting one mixed assertion into six clean propositions multiplies that cost by six and settles nothing extra.

- **Per-source cap: 15 nodes** — a volume backstop, not a target. Hitting it usually means the gate above was not applied. Overflow is parked in `questions/`, never dropped (§4 Phase C can promote it later if a decision starts to need it).
- **Field-origin sources: cap 3.** A report in a declared result lane (e.g. `.raw/experiments-results/`) is **measurement, not literature**: its `sources/` page owns the run detail — metrics, parameters, per-hypothesis outcomes with their conditions — and claims are minted only for findings that flip a claim's verdict, open a new failure mode, or bound an existing claim's scope. Everything else reaches the wiki as `## Field Evidence` entries on the claims the run served (§4 Phase C), never as freestanding nodes.
- **A scope with no declared decisions** cannot run the gate. Atomize by judged value under the 15 cap, as before, and say so — the honest report is "no decisions declared, so relevance was not filtered", not a silent fallback.

---

## 2. Node Schema

```yaml
---
type: claim                     # claim | mashup | source | question | meta | experiment | deliverable
title: "A single verifiable assertion, declarative form"
created: 2026-06-11
updated: 2026-06-11
status: seed                    # seed | developing | hardened | evergreen | deprecated | pruned
confidence: low                 # high | medium | low
generation: 1                   # +1 each time a revision survives verification
last_challenged: 2026-06-11     # date of last refutation attempt (decay-curve anchor)
challenges_survived: 0          # survived objections, full + single depth (§5.1)
full_depth_challenges: 0        # optional: of those, how many at FULL depth — the §3 gate's evidence
supports: []                    # wikilinks to nodes this claim supports
contradicts: []                 # wikilinks to conflicting nodes (kept on BOTH until resolved)
sources: []                     # wikilinks to evidence (.raw/ paths or sources/ pages)
serves: []                      # optional: declared decision IDs this node bears on (§1) — the relevance key
evidence_class: literature      # optional: literature | field | design — §3 gate currency; absent = literature
aliases: []                     # english kebab-case aliases (search aid, §9)
---
```

**Mandatory defaults for new nodes:** `status: seed`, `generation: 1`, `confidence: low`, `challenges_survived: 0`, `full_depth_challenges: 0`, `last_challenged: <creation date>`. `full_depth_challenges` is written on every *new* node but remains **optional in the schema**, so a node minted before 1.0.0 is not missing anything — that is the difference between "untracked" and "zero", and `wiki-lint.py` only judges the latter.

**`full_depth_challenges:` (optional) is the promotion evidence.** `challenges_survived` counts both depths (§5.1), so on its own it can no longer answer the question the §3 `developing → hardened` gate asks — *did this node ever survive the full three-lens pass?* This counter can: increment it alongside `challenges_survived` on a full-depth survival, and leave it alone on a single-lens one. Absent means a node that predates the key; `wiki-lint.py` then asserts nothing, and reports `gate_without_full_depth` only for a node at `hardened` or above that carries the key at 0. It is the machine-checkable form of what §11.1's depth marks record in prose.

**`serves:` (optional) is the relevance key.** It lists the IDs of the declared decisions (§1) this node bears on — the test being *would flipping this node change which way that decision goes?*, not *is this node topically related?*. It drives target selection (§4 Phase B), verification depth (§5.1), the pruning sweep (§4 Phase C), and the §7 counters. Absent or empty means unassigned: the node is a prune candidate, not an error, and `wiki-lint.py` lists it under `unassigned_claims` (warning). A node may serve several decisions; when every decision it serves is `settled`, it is a prune candidate too — settled decisions no longer need branches.

**Node bodies assert; they do not plan.** Two kinds of sentence are easy to confuse, and the protocol treats them oppositely:

- **A conditional recommendation is an assertion — keep it in the body.** *"At ≤65B use 8-bit Adam; above it keep 32-bit"* says something falsifiable about the world: the §5 refuters can attack it, field evidence can bound it, and a decision can be taken from it. Engineering research produces mostly this, and it is the most useful thing a claim can carry. Nothing here pushes it out of a node.
- **A plan is not an assertion — put it elsewhere.** *"The next step is to measure the >65B range"* has no truth value; it is a session intention, and it belongs in `hot.md`, the deliverable's next-steps section, or a `questions/` node.

The reason is mechanical, not stylistic: a plan expires when the decision it precedes lands, while claims carry no expiry, so a stale plan parked in a node body survives every cadence check. And because the synthesis step (`reharm:ensemble`) reads node *bodies* as raw material, such a line is copied into the deliverable, then into `hot.md`, then re-read by the next synthesis — prose citing prose in a closed loop that no `status` field can interrupt. `wiki-lint.py` reports plan phrasing (*"next step"*, *"다음 단계"*) as `forward_looking_in_node_body` (warning); it deliberately does **not** flag conditional recommendations, which are the point of the wiki.

**Evidence class (optional).** `evidence_class:` declares which currency the §3 evidence gate trades in: **`literature`** — the assertion stands on external documents (the default when the key is absent, so every legacy node stays valid with no migration); **`field`** — a fact measured on the scope's own data or system, for which an independent external source often *cannot* exist (its currency is replication, not citation); **`design`** — a decision the owner has adopted for this scope, recorded and challengeable but not provable by literature (its currency is the owner's adjudication). §3 calibrates the developing→hardened gate per class; `wiki-lint.py` validates the enum when present. A pure design *rationale* usually belongs in a design-intent `sources/` page rather than a claim — mint a `design`-class claim only when the decision itself must survive refutation.

**Cross-scope mashups carry a `borrowed:` snapshot** (minted by `reharm:modal-interchange`) — one entry per donor node, recording the state the knowledge had when borrowed:

```yaml
borrowed:
  - node: "[[donor-node]]"
    scope: /abs/path/to/donor-scope
    status_at_mint: hardened
    gen_at_mint: 4
    date: 2026-07-02
    donor_decision: "D2 settled → adopted mtime, the direction borrowed"   # optional
```

Phase A (§4) compares each donor's **current** status/generation against this snapshot. **Drift runs both ways.** A demotion, deprecation, prune, or conclusion-changing revision is a **new objection** — the borrowed premise moved under the mashup. A promotion, a survived challenge, or a gained generation is drift too, and absorbing *that* **retires** the inherited objection below and may lift the mashup's confidence floor: the premise the mashup was leaning on got attacked somewhere else and held. Wording matters here because the good direction is the one an implementation forgets — a check that only looks for bad news makes borrowing from an actively-evolving donor all cost and no recovered benefit.

A `pruned` donor is drift of a particular kind: it was not refuted, it stopped mattering to *its own* scope (§3), so what the objection records is that nobody maintains or re-verifies that premise any more. The optional `donor_decision:` line carries what status alone cannot express — which decision the donor served and, once that decision is `settled` or `superseded`, which way it went. A ruling that went **against** the direction borrowed is the drift that matters most and the only one invisible to a status comparison.

**A mashup inherits the state of what it borrows; it never launders it.** Two consequences at mint time, both from §14's floor rule one level down (`confidence` is the minimum over the load-bearing set, and optimism is forbidden):

- **Confidence floor.** The mashup's `confidence` is at most the weakest premise it leans on, borrowed ones included.
- **An unverified premise is a stated limit.** A load-bearing donor below `developing` in its own scope (nobody has attacked it yet) goes into `## Objections & Limits` naming that state. It is a *current* limit, so it leaves the node the session Phase A absorbs the donor's promotion — which is exactly why borrowing early is legitimate rather than reckless.

The one place this bites is promotion: the §3 `developing → hardened` gate does not open while a **load-bearing** borrowed premise sits below `developing` in its own scope. Verification depth is computed per node (§5.1), so the §5 lenses judge the mashup's own conclusion and never re-judge its imports — without this, a mashup could earn `hardened` on top of an assertion no refuter has ever seen. Minting is free and early borrowing is encouraged; the cost lands where every other quality cost in the protocol lands, at the gate.

**Absorbing drift re-stamps the snapshot** to the donor's state at absorption (`status_at_mint`, `gen_at_mint`, `date`); the mint-time values live on in the E#### report. The snapshot is a baseline, not a history: left un-restamped it makes one donor move re-trigger the same drift on every later Phase A and every `reharm:pushing` run (row 5), which outranks synthesis, the prune sweep and momentum — so a single donor demotion would pin an unattended loop on integrity work that is already done. `wiki-lint.py` validates the subkeys.

**Body structure (claim/mashup):**

```markdown
# Body — current-generation conclusion only

Declarative, present tense, objections already absorbed. No change history in the body
(git and evolution reports own the history).

## Objections & Limits
- The CURRENT boundary conditions only — active objections and limits, each <= 2 lines,
  present tense. Absorbing a refutation REWRITES this section to the new current set;
  it never appends archaeology. Resolved objections, refuter narratives, adjudication
  dates and rollback stories leave the node — the E#### report and git own them (§8).
  Conflicts use > [!contradiction] callouts.

## Field Evidence
- Append-only. Real-world validations / counterexamples / generalizations,
  each with a wikilink to its origin (the "import" direction) and the conditions
  the result held under (dataset, scale, hardware, hyperparameters — whatever bounds it).
  A field result without its conditions cannot be adjudicated by the §5 reproducibility lens.
```

### Experiment node (field-experiment pre-registration)

A separate node kind, kept in `wiki/experiments/`. It is a **design record**, not a knowledge node: it does **not** evolve, never gains a `generation`, and is excluded from frontier scoring. It exists to pre-register — *before* the run — what result would confirm or refute a claim, so the imported field evidence (§4 Phase C) is judged against a criterion fixed in advance, not chosen post-hoc. The full procedure lives in the experiment-design skill and the bridge in §12.

```yaml
---
type: experiment
title: "What this experiment puts under test, declarative"
created: 2026-06-19
updated: 2026-06-19
status: planned                 # planned | running | imported | abandoned | retired
claim: "[[target-claim]]"       # the claim(s)/question(s) this experiment serves — a wikilink or a list
runner: "/autoresearch:plan"    # optional: external bridge entry point (tool-agnostic, §12)
---

## Hypothesis
The target claim restated as the proposition under test.

## Decision at stake            <!-- §12 decision gate, pre-registered -->
- CONFIRM → <what changes **outside the wiki**: a design, build, deploy, or spend decision>
- REFUTE  → <what changes **outside the wiki**, and it must differ from the CONFIRM row>

## Confirm / Refute             <!-- §5 reproducibility lens, pre-registered -->
- CONFIRM if: <observable / numeric criterion fixed before the run>
- REFUTE if:  <failure condition or counterexample fixed before the run>

## Conditions to record         <!-- §2 Field Evidence requirement -->
- dataset / scale / hardware / hyperparameters the result must hold under and report.

## For the runner               <!-- input to the external operationalize step (§12) -->
- goal: "<plain-language objective>"
- shape: confirmatory | exploratory | debug
- result_sink: .raw/experiments-results/

## Handoff
- the exact next command, run by the user in the code workspace (never here).
```

**Mandatory keys:** `type: experiment`, `title`, `created`, `status`, `claim`. `claim:` is a single wikilink **or a list** — one run routinely serves several claims and even an open question at once (field-evidenced), and forcing a singular key just misdeclares that. The four evolution-mechanic keys (`confidence`, `generation`, `last_challenged`, `challenges_survived`) are **omitted by design** — an experiment node is not graded, only its imported *result* is (against the pre-registered criterion). `status` uses the experiment lifecycle, never the maturity ladder. **`## Decision at stake` is required for any pre-registration that is still live** (`planned`/`running`) — a pre-registration that cannot name a decision is a record-keeping exercise, not an experiment (§12 decision gate). The requirement is scoped to live nodes so the rule stays additive: records written before the gate existed already ran, and §4 forbids editing a frozen design record. `wiki-lint.py` reports a live node without the section as `experiment_missing_decision_at_stake` (**warning** — whether a named decision is *real* is a judgement the gate makes with the user, not something a linter can settle). **`retired`** is for a pre-registration whose decision died rather than whose run failed — the design record stays verbatim (§4 forbids post-hoc redefinition), only the queue state changes; it requires a pointer to the deciding source and a re-open condition, and is distinct from `abandoned` (a run that produced nothing usable). An already-`imported` experiment whose *re-run* is retired keeps `status: imported` and carries the retirement as a banner — the node is not the thing being retired, the queued re-run is.

### Question node (lifecycle)

`wiki/questions/` pages carry their own lifecycle — never the maturity ladder:

```yaml
---
type: question
title: "The open question, interrogative form"
created: 2026-07-02
status: open                    # open | answered | escalated | archived
---
```

- `open` (default for new questions) → `answered` (resolved into a claim or verdict — say where) | `escalated` (handed to deep research, §13 — requires an `## Escalation` block) | `archived` (aged out via a critique verdict; a status flip, never a delete).
- Required keys remain `type` + `title` (additive change). Legacy question pages that still carry maturity values (`status: seed`, tag conventions like `question/open`) stay **valid** — `wiki-lint.py` reports them as `legacy_question_status`, a warning, never an error. No migration required.

### Deliverable node (answer synthesis)

A non-evolving node kind, kept in `wiki/deliverables/` and written by `reharm:ensemble` (§14). It is a **snapshot synthesis**, not a knowledge node: it never evolves, never gains a `generation`, and is excluded from frontier scoring and the maturity census — the evolving truth stays in the claims it cites.

```yaml
---
type: deliverable
title: "One-line thesis of the answer"
created: 2026-07-02
updated: 2026-07-02
question: "[[central-question]]"    # what this answers — a question wikilink OR a declared decision ID (e.g. "D1"); its identity key
---
```

**Mandatory keys:** `type: deliverable`, `title`, `created`, `updated`, `question`. `question:` holds either a `questions/` wikilink or a **declared decision ID** (§1) — a deliverable that answers a decision is the normal case, since the decision is what someone is waiting on. The evolution-mechanic keys are **omitted by design** (as with `experiment`): a deliverable is never graded — it is *re-derived* from graded nodes, update-in-place (`updated` bumps; git owns versions, §8). Body contract and confidence rule in §14.

### Source page metadata (independence)

`sources/` pages may carry:

```yaml
origin: primary                 # primary | secondary
derived_from: []                # secondary only: wikilinks to the primary source page(s) it digests
```

Independence has ancestry: the §5 evidence lens treats two sources whose `derived_from` chains overlap — one derives from the other, or both digest the same primary — as **non-independent**, so they can never jointly satisfy the §3 developing→hardened literature gate (≥2 independent sources). Deep-research reports are secondary by construction (§13).

---

## 3. Maturity State Machine

```
 seed ──► developing ──► hardened ──► evergreen        (any state) ──► deprecated   (refuted)
                                                       (any state) ──► pruned       (stopped mattering)
```

| Transition | Condition |
|---|---|
| seed → developing | ≥1 source + completed body (a declarative conclusion exists) |
| developing → hardened | survived ≥1 **full-depth** adversarial verification (all three lenses, ≥2/3 — a single-lens pass does not open this gate, §5.1; the evidence is `full_depth_challenges` ≥ 1 (§2) plus the E#### report's depth marks (§11.1), *not* `challenges_survived`, which counts both depths) + the class currency (§2 `evidence_class`): **literature** — ≥2 **independent** sources · **field** — ≥2 `## Field Evidence` entries under materially different conditions (another seed/split/period: replication, since an independent external source often cannot exist for a fact measured on the scope's own data) · **design** — the decision recorded as adopted (a design-intent `sources/` page or a critique verdict; the owner's adjudication is the evidence) |
| hardened → evergreen | ≥1 entry in `## Field Evidence` (real-world feedback is the only gate). If that evidence is conditional, the claim's scope must be narrowed to match those conditions, and no open counterexample may remain (§5 reproducibility lens). A `field`-class claim arriving at `hardened` already carries this row's entry count (its replication entries *are* field evidence) — what remains is the reproducibility residue above, and when it holds, proposing both promotions in the same session is legitimate |
| any → deprecated | total collapse under verification, **or absorption into a parent claim via a critique merge verdict** (the assertion lives on in the parent; the absorbed node's body becomes a one-line pointer — `Absorbed into [[parent]] (YYYY-MM-DD critique)` — so inbound wikilinks keep resolving). **Never delete** — flip status so the node leaves the graph but the record stays |
| any → **pruned** | the node bears on no open decision: `serves:` is empty and no open decision depends on it, or every decision it serves is now `settled`. **This is not a verdict on truth** — a pruned node may be correct, well-sourced, and high-generation; it simply stopped bearing on anything the scope is deciding. The body stays verbatim and gains a one-line reason that **opens with the status being cut from** — `Pruned from <seed｜developing｜hardened｜evergreen>: <unassigned ｜ all served decisions settled ｜ superseded by [[decision-source]]> (YYYY-MM-DD)`. Like `deprecated` it is a status flip — never a delete — and it is **reversible**: if a decision reopens, flip the node back to the status that line names and it re-enters the cadence |

- Promotion is never auto-computed. Phase D **proposes** it with evidence; the evolution report records the rationale.
- **Pruning is proposed, never automatic** — the same rule, for the same reason. Phase C reports prune candidates with the reason quoted; the user picks (§4 Phase B spirit). A linter can see that `serves:` is empty; only the user knows whether that is a gap in the binding or a genuinely dead branch.
- Re-verification cadence (the decay curve is a *re-verification trigger*, never an auto-editor): seed/developing **every session**, hardened **4 weeks**, evergreen **12 weeks**. **`design`-class nodes sit outside the calendar** — they re-verify only when a neighbor moves against them (a new contradiction, or a supports/contradicts neighbor whose conclusion changed); a decision does not decay with time.
- **Nodes bearing on no open decision sit outside the calendar too.** An unassigned node, or one whose every served decision is `settled`, is not re-verified on schedule — it is a prune candidate instead. This is what stops the treadmill: without it, a scope that atomized 60 assertions owes 60 re-verifications a session forever, regardless of how few of them any decision rests on.
- **Decay candidates are capped.** When Phase B lists cadence-overdue nodes, seed/developing candidates show only the **top 5 by longest overrun** — an aging scope would otherwise flood every session with decay work and starve the frontier. The rest simply wait their turn; nothing is dropped.
- **Experiment nodes sit outside this ladder** — they have their own lifecycle (`planned → running → imported | abandoned | retired`, §2) and never gain a generation. `pruned` is a maturity value and is therefore *invalid* on an experiment node: a pre-registration whose decision died becomes `retired`. Their only tie to maturity is the `hardened → evergreen` gate: a `type: experiment` pre-registration fixes the confirm/refute criterion the §5 reproducibility lens applies to the imported result (§4 Phase C). The result — not the experiment node — is what opens (or fails to open) the gate.

---

## 4. Evolution Session Protocol — 5 Phases

One session = one cycle. `reharm:reharmonization` follows this exactly.

### Phase A. Retrospect
1. Read the latest report in `wiki/meta/evolution/` and `hot.md`.
2. Adversarially re-verify the nodes changed last session (§5). Taking long is fine.
3. **Borrowed-snapshot check**: for mashups carrying `borrowed:` (§2), compare each donor node's current status/generation against the snapshot. Drift **in either direction** is absorbed this session — a demotion/prune/revision as a new objection, a promotion or survived challenge by retiring the inherited-premise limit and re-checking the confidence floor. Either way, absorbing **re-stamps the snapshot** to the donor's current state (§2), with the mint-time values recorded in this session's report.
4. Roll back (revise) or demote (deprecated) anything that collapsed. If the last session evaluation (§7) failed, start from its failing checks.

### Phase B. Target Selection

**Pick the decision first, then the node.** Selection is scoped to one open decision (§1) so the session's cost lands where a decision is waiting on it.

1. **Active decision**: read the scope's open decisions and the lint `decisions` block. One open decision → it is the active one. Several → present them with the state of each (how many serving nodes, how many at `hardened`+) and let the user pick. None declared → say so and fall back to steps 2–4 unfiltered, reporting that relevance was not filtered.
2. Frontier candidates **inside that decision**: from the scope root run
   `python3 <plugin-root>/scripts/boundary-score.py --json --top 5 --serves <ID>`
   (`<plugin-root>` = the installed plugin directory containing this file; the script reads `./wiki/` under the cwd). The score formula is unchanged — `--serves` filters, it does not re-weight — so an empty result means "no frontier inside this decision", not an error.
3. Decay candidates: nodes serving that decision whose `last_challenged` exceeds their cadence (§3) — read the frontmatter dates and compare directly; scopes are small, no script involved. Nodes bearing on no open decision are **not** decay candidates (§3); they are prune candidates.
4. A user-named topic always wins, decision filter included.
5. Present the merged candidate list and **let the user choose — never auto-select**. Record the active decision in the report's `## Decision & Targets` (§11.1).

### Phase C. Mutation
Per target:
- If new `.raw/` material exists: decompose it and recombine with existing nodes.
- **Field-origin results** (the scope's own experiment/real-world output — by convention under `.raw/experiments-results/`) import into the target claim's `## Field Evidence`, carrying their conditions (§2) — not into `## Objections & Limits`. Their atomization at root time is conservative (§1: detail on the source page, ≤3 decision-changing claims). External material (papers, web, repos) is seed, as above. Ambiguous origin → confirm with the user in Phase B.
  - **If a `type: experiment` pre-registration exists for the target** (§2, §12): judge the result against its **pre-registered** `## Confirm / Refute` criterion — never a post-hoc one. CONFIRM → append to `## Field Evidence` with conditions (the evergreen gate, §3); REFUTE → the counterexample feeds Phase D's reproducibility lens (absorbed into `## Objections & Limits`, or `deprecated` on total collapse). Either way flip the experiment node to `status: imported`; a run that never produced a usable result → `status: abandoned`.
- **Owner design decisions** (`.raw/design-decisions/` by convention — scope-redefinition declarations, not literature) absorb like any `.raw/` material, but they carry a mandatory side-effect: they can **settle or collapse a declared decision**. Absorbing one means re-reading the scope's decision block (§1) and reporting — never auto-applying — which decisions the material just settled, plus every node and pre-registration that stood on the collapsed branch. Those flow into the prune sweep below. This step exists because a claim or pre-registration can be decision-relevant *when written* and lose that later, and nothing else in the loop re-checks it: a frozen design record cannot notice its own obsolescence.
- If new evidence or counterexamples are needed: **web search** (policy in §6).
- Contrast / compare / integrate with adjacent nodes → create `mashups/` nodes.
- **Prune sweep (every session, before Phase D spends anything).** Walk the nodes that are not this session's targets and report — never auto-apply (§3) — every **prune candidate**, each with its reason:
  - `serves:` empty and no open decision depends on it (the lint `unassigned_claims` list is the starting point);
  - every decision it serves is now `settled`;
  - an owner design decision absorbed this session collapsed the branch it stood on.
  **A node bound to a `superseded` decision is not on this list** (lint: `stale_serves_target`). Re-bind it to the successor decision first (§1); only what no successor took over becomes a prune candidate, and then under the *unassigned* reason, not the superseded one. Pruning on a superseded binding would cut branches for a question that was replaced rather than answered.
  Present them as one batch with the reason quoted; the user picks which flip to `status: pruned` (§3), and each flip records the status it cut from so it can be undone. Unpicked candidates stay exactly as they are. **This sweep is what keeps the scope's cost proportional to its open decisions** — without it, every assertion ever atomized keeps drawing refuters and cadence for the life of the scope. Nodes newly bound to a decision this session are *not* candidates: check the binding before the branch.
  - The same walk covers the **experiment queue**: for every `type: experiment` node that is neither `retired` nor already carrying a recorded re-run retirement, re-read its `## Decision at stake` (§2) and report those whose two branches this session's material collapsed into one outcome. Retiring a queued re-run does **not** touch the node's hypothesis or criterion (§4 forbids post-hoc redefinition of a frozen design record).

### Phase D. Natural Selection
Run §5 on every mutation, **at the depth the node's decision role earns** (§5.1):
- **Survives** → `challenges_survived +1`, refresh `last_challenged`; **at full depth only**, also `full_depth_challenges +1` (§2), `generation +1`, and propose promotion if §3 conditions hold. A single-lens pass buys currency, never a generation — that is what keeps "generation" meaning "survived all three lenses" (§5.1). Because `challenges_survived` counts both depths, the developing→hardened gate reads its evidence from `full_depth_challenges` and the E#### report's depth marks (§11.1), not from that counter alone. Keep the two in step: `full_depth_challenges` is the half of `challenges_survived` a promotion is allowed to rest on, and `wiki-lint.py` reports a post-gate node stuck at 0 (`gate_without_full_depth`).
- **Partial collapse** → absorb the valid objection into `## Objections & Limits` — compress it to its ≤2-line boundary condition and **rewrite the section to the current set** (§2); the refuter's full reason is archived in the E#### report (§11.1) — then revise and re-judge **once** (§5.3). A node still partially collapsing after that single re-judge keeps its current generation, keeps the residual objection on the record, and its unresolved part is filed as a `questions/` node — the session moves on rather than grinding.
- **Total collapse** → `status: deprecated`.
- **Not worth judging** → if a target turns out to bear on no open decision, do not run refuters on it at all: report it as a prune candidate (above) and drop it from the session. Refuting a node nothing depends on costs three sub-agents to learn something no decision uses.

### Phase E. Record
1. Write `wiki/meta/evolution/E####.md` (§11.1 template; zero-padded sequence).
2. Overwrite `hot.md`; update `index.md` (§11.2 maturity census); prepend a `log.md` entry.
3. Lint: from the scope root run `python3 <plugin-root>/scripts/wiki-lint.py --json` (orphans, dead wikilinks, missing/invalid frontmatter, unresolved contradictions). Store findings under `wiki/meta/lint/`.
4. Produce the session evaluation JSON (§7).

---

## 5. Adversarial Verification Rubric

The three lenses, each run by an **isolated sub-agent** restricted to exactly one of them:

- `coherence` — logical flaws, internal contradiction, leaps
- `evidence` — source reliability, independence, dates, quote distortion
- `reproducibility` — does it hold under real/experimental conditions; are there counterexamples

For each item under verification:

1. **Depth follows decision role.** How many lenses a node earns depends on what rests on it, not on how interesting it is. A node is **load-bearing** for a decision when flipping it would change which way that decision goes — the §14 test, applied to a decision instead of a sentence.

   | Depth | When | Lenses | On survival |
   |---|---|---|---|
   | **full** | load-bearing for an **open** decision | all 3, **≥2/3 must survive** | `generation +1`, `challenges_survived +1`, **`full_depth_challenges +1`** (§2 — the gate's evidence), refresh `last_challenged`, promotion eligible (§3) |
   | **single** | serves an open decision but is not load-bearing for it (a bound, a supporting detail, context) | **1**, derived from `evidence_class` (§2): `literature` → `evidence` · `field` → `reproducibility` · `design` → `coherence` (absent class = `literature`) | `challenges_survived +1`, refresh `last_challenged`, **no generation gain**, **`full_depth_challenges` untouched**, promotion capped at `developing` |
   | **none** | bears on no open decision | **0** — not judged | nothing; it is a prune candidate (§4 Phase C) |

   Two consequences are deliberate. **A generation still means "survived the full three-lens pass"**, so the guarantee the wiki makes about its own claims is unchanged — the cheap tier buys currency, not generations. And **cost follows need**: the moment a synthesis has to lean on a single-lens node, that node becomes load-bearing and takes the full pass on its next session. Depth is re-derived every session, because a decision settling or reopening changes what rests on what. The E#### report records the depth per node (§11.1) so a reader can always see which verdicts were cheap.

2. **Isolation is structural, not stylistic** — the §1 pollution-control invariant applied to the judging side. An in-context refuter has watched the mutation being made and is anchored toward accepting it; an isolated one judges only the artifact. Each refuter is spawned on the worker doc `skills/reharmonization/refuter.md` (resolved to an **absolute path** by the orchestrator) and receives, inline in its spawn prompt: its one lens, the target node verbatim (frontmatter + body, post-mutation), the cited `wiki/sources/` page originals, and the lens material refuter.md lists — and **never the session's mutation narrative**. Refuters are judgment-only: they write nothing, fetch nothing, and read nothing but `EVOLUTION.md`. The exact inputs and the return contract (`{ "lens": …, "refuted": true|false, "reason": …, "counter_evidence": … }`) live in refuter.md.
3. Verdict: at full depth, **pass only if ≥2 of 3 survive** (`refuted=false`); at single depth, pass iff that one lens returns `refuted=false`. Record every verdict and refutation reason in the report; absorb valid objections into the node. After a partial collapse is absorbed and the node revised, re-judge by **re-spawning the same isolated workers** against the revised node — never by an in-context second opinion — and **at most once per node per session**. A node that still collapses after that one re-judge is not ground down further: it keeps its current generation, the residual objection stays in `## Objections & Limits`, and the unresolved part is filed as a `questions/` node for a later session or a `critique` ruling. The cap exists because an assertion that mixes a true part with a false one can absorb-and-revise indefinitely, and each round costs a full re-spawn while the decision it serves waits.
4. **Degraded mode fails loud.** If sub-agents cannot be spawned in the current environment, run the three lenses in-context as three separate, sequential judgments — and record **`refuters ran non-isolated`** in the E#### report's Verdicts section, so the weaker isolation is on the record for anyone auditing the session.
5. Before high-stakes promotions (e.g. hardened → evergreen candidates), a deeper external research pass may be run if your setup offers one; its output report goes into `.raw/` and re-enters through `reharm:root`.
6. The reproducibility lens may also run **prospectively**: a `type: experiment` pre-registration (§2, §12) fixes its CONFIRM/REFUTE criterion *before* a field experiment, so Phase C/D applies the same lens to the result without redefining it after the fact. Same rubric, run ahead of the evidence.

---

## 6. Web Search Policy

- Web search is **agent-initiated inside bounded phases** — `reharm:root` (enrichment while seeding) and `reharm:reharmonization` Phase C (evidence/counterexample hunting). It does not require a separate explicit call; user control comes from Phase B target approval.
- Bounds per session: ≤3 search rounds, ≤5 fetched sources per round. Every fetched source lands in `.raw/` or `sources/` with a date and URL.
- The protocol fixes the **function, not the implementation**, and that function has two halves — **discovery** (finding candidate URLs) and **extraction** (turning a URL into clean markdown). Native **WebSearch** is the baseline for discovery; for extraction, native **WebFetch** is the always-available baseline and the `defuddle` CLI is **preferred when present** (procedure in §6.3). Any external research loop is acceptable as long as it respects §6.1–§6.2 and the bounds above.
- Per-scope opt-out: set `Web search: disabled` in the scope CLAUDE.md and all phases skip it. Per-scope source preference/exclusion lives in the scope CLAUDE.md toggles (§10).

### 6.1 Search procedure — decision-aligned, not topic-collection

The goal is not to *gather* material but to *move a decision*. For each target, decompose the search by **angle** — not by sub-topic:

1. **Decision angle** (always first) — what evidence would settle the open decision this target serves, or would show the branch is a dead end. This is the angle that can end the search early: material that settles the decision makes the other three unnecessary.
2. **Refutation angle** — evidence that would break the claim (feeds the coherence/evidence lenses).
3. **Independent-source angle** — corroboration from a source not already cited, so a survivor can earn the §3 developing→hardened literature gate (≥2 *independent* sources; a field-class claim needs replication instead — searching cannot supply it).
4. **Counterexample angle** — real or experimental conditions where the claim fails (feeds the reproducibility lens).

**Angles 2–4 are for full-depth targets** (§5.1). A single-depth target runs the decision angle only — one round, and stop. Round 1 broad (1–2 queries per angle); round 2 fills only the gaps or contradictions round 1 surfaced; stop at the bounds above. For every kept source record date, independence (1st- vs 2nd-hand), and URL on its `sources/` page — these are exactly what Phase D's evidence lens (§5) adjudicates.

### 6.2 Egress hygiene — fetched content is untrusted input

Fetched web content can carry prompt injections, fake wikilinks, and executable fences. Before each fetch and before writing any fetched body into `.raw/` or `sources/`:

- **URL**: `http(s)://` only; reject `file:`/`javascript:`/`data:`, RFC1918 private addresses and `localhost`/`127.0.0.1`, and redirects to hosts that never appeared in the search results (SSRF defense).
- **Sanitize before writing**: strip `<script>`/`<iframe>`/`<style>` blocks; escape `[[` and `]]` in the source body so adversarial content cannot inject edges into the wikilink graph; reject any `---` frontmatter delimiter inside fetched content (node frontmatter is authored by the skill, never by the upstream page); truncate bodies to ~50 KB.
- **Fail loud, not silent**: a failed or blocked fetch is logged to `log.md` with URL + reason and filed as a `questions/` open question — never dropped, since a skipped source is a fact Phase D needs.

### 6.3 Page extraction — defuddle (optional accelerator)

Inside the bounded fetch step above, prefer the `defuddle` CLI over native WebFetch for standard web pages — it strips navigation and clutter and returns cleaner, token-leaner markdown. It is never auto-installed (Detect rule below).

- **Detect, then choose**: if `command -v defuddle` succeeds, use it; otherwise fall back to native WebFetch for the rest of the session. A missing CLI is not an error (install: `npm install -g defuddle`, MIT).
- **Command**: `defuddle parse <url> --md` and capture **stdout**. Do **not** use `-o <file>` — the body must first pass §6.2 (URL validated before the call; content sanitized) before you Write it into `.raw/`/`sources/`. Writing the file directly would bypass that hygiene.
- **Skip** URLs already ending in `.md` (already markdown — read directly).

---

## 7. Session Evaluation & Stagnation Detection

At the end of every reharmonization session, self-grade against machine-checkable criteria and store the JSON next to the report (`E####.eval.json`) — **schema v3, counter-based**:

```json
{
  "pass": true,
  "score": 0.81,
  "checks": {
    "lint_clean": true,
    "no_unresolved_contradiction": true,
    "decisions_settled": 1,
    "branches_pruned": 3,
    "generation_progress": 3,
    "mutations_rejected": 1,
    "new_independent_sources": 2,
    "challenge_survival_rate": 0.75,
    "report_written": true
  },
  "stagnation": {
    "trailing": [
      { "session": "E0002", "decisions_settled": 0, "branches_pruned": 2, "generation_progress": 2, "mutations_rejected": 0, "new_seeds": 3, "new_independent_sources": 1, "failed_checks": [] },
      { "session": "E0003", "decisions_settled": 0, "branches_pruned": 0, "generation_progress": 0, "mutations_rejected": 2, "new_seeds": 0, "new_independent_sources": 0, "failed_checks": [] },
      { "session": "E0004", "decisions_settled": 1, "branches_pruned": 3, "generation_progress": 3, "mutations_rejected": 1, "new_seeds": 1, "new_independent_sources": 2, "failed_checks": [] }
    ],
    "verdict": "continue"
  }
}
```

- `pass` (required boolean) and `stagnation.verdict` (required enum: `continue` | `reseed` | `change-strategy`) are the only fields other tooling branches on; `wiki-lint.py` validates both on the latest eval (`eval_findings`, a warning). A failing session is still a valid session — it simply becomes Phase A's first target next time.
- **Decision counters — the primary progress signal:**
  - `decisions_settled` — declared decisions (§1) flipped `open → settled` this session, whether by an owner ruling or because the evidence now answers them. **This is what the scope is for.** A session that settles one decision has done more than a session that raised five generations.
  - `branches_pruned` — nodes flipped to `status: pruned` this session (§3). A high value is **healthy**, like `mutations_rejected`: it is the scope shedding cost it no longer owes. Pruning ten stale nodes makes every later session cheaper.
- **Secondary counters** (this session's row also closes the `trailing` array; earlier rows come from the previous evals):
  - `generation_progress` — total generation gains this session (full-depth passes only — the single-lens tier grants no generations, §5.1). Secondary on purpose: generations earned on nodes no open decision rests on are motion, not progress.
  - `mutations_rejected` — mutations Phase D refused (rolled back, absorbed-and-demoted, or dropped). **A high value is not failure** — correctly culling bad mutations is healthy selection; hiding it once mis-scored a healthy session as a 0.45 slump. It becomes a problem only as a *streak* (see change-strategy below).
  - `new_seeds` — nodes newly created this session (Phase C spin-offs, imports).
  - `new_independent_sources` — sources newly cited this session that are independent of the target claims' existing citations (the §3 developing→hardened literature currency).
  - `failed_checks` — names of the boolean checks that failed this session.
- `score` is **optional, display-only, and derived** — fixed formula, booleans as 0/1:
  `score = mean( lint_clean, no_unresolved_contradiction, report_written, challenge_survival_rate, min(generation_progress, 3) / 3, min(decisions_settled + branches_pruned, 3) / 3 )`.
  **No verdict, gate, or tool may branch on `score`.** It exists for a human scanning a list of sessions, nothing else.
- **Stagnation verdict — computed from counters only, never from scores.** Over the trailing 3 sessions (including this one; fewer than 3 completed sessions → `continue`, not enough trail to judge). A counter absent from an older row reads as 0:
  - `reseed` — Σ `generation_progress` == 0 **and** Σ `new_seeds` == 0 **and** Σ `new_independent_sources` == 0. Nothing moved and nothing new came in: the scope needs new raw material, not more churn.
  - `change-strategy` — any of:
    1. the **same** check name appears in `failed_checks` 3 sessions in a row;
    2. 3 sessions in a row rejected every attempted mutation (`mutations_rejected` > 0 with `generation_progress` == 0 in each);
    3. **3 sessions in a row moved no decision while gaining generations** — Σ `decisions_settled` == 0 **and** Σ `branches_pruned` == 0 **and** Σ `generation_progress` > 0, evaluated **only when all three trailing rows actually carry the two decision counters**. The wiki is getting more reliable about things nobody is waiting on. This is the exact failure the protocol's decision counters exist to catch, and it reads as healthy under every other check: lint clean, survival rate high, generations climbing. The fix is never another verification round — it is to re-read the decision block and pick a target that serves an open one, or to admit the decisions are stale and rewrite them (`superseded`, §1 — not deleted, so the branches under them get re-bound rather than silently orphaned).
       The carry-requirement is the one exception to the absent-reads-as-0 rule above, and it is why the exception exists: a row that never tracked `decisions_settled` is *unmeasured*, not measured-at-zero. Without the exception every pre-1.0.0 trail satisfies all three conditions the moment it gained a generation, and a healthy scope's first 1.0.0 session would be told it is stagnating — the false positive being, exactly, the failure this trigger is supposed to name.
  - `continue` — otherwise. In particular, a single all-rejected session with healthy neighbors is `continue` — that is selection working, not stagnation.
- Legacy evals stay readable: v1 carried `trailing_scores`, v2 lacked the decision counters, and in both only `pass` and `stagnation.verdict` are load-bearing — both have existed since v1. Missing counters read as 0 for the `reseed` case and for change-strategy cases 1–2; case 3 requires them present (above), so a v2 trail cannot trigger it until three v3 sessions exist. New sessions always write v3.

---

## 8. Record System & Git Rules

| Layer | File | Holds | Nature |
|---|---|---|---|
| State | `hot.md` | last ~500 words of context | cache; fully overwritten |
| Map | `index.md` + frontmatter | catalog + maturity census | always current |
| Result | node bodies | what is currently true | revised freely |
| Process | `meta/evolution/E####.md` | what changed and why; what was culled | append-only |
| Diff | git | line-level history | automatic |

No separate long-term memory state file — these three layers plus git are sufficient. The session boundary is the report itself (`E####.md`, append-only). Branches, PRs, **and tags** are all forbidden: branches/PRs fight auto-commit workflows and punish frequent revision, and per-scope tag sequences (`evolution/E####`) would collide across multiple scopes while rarely syncing across machines. The plugin never touches the scope's git state.

---

## 9. Language & Search Conventions

- **System docs in English; scope content in the user's language** (Korean expected). Claims, reports, and questions are written in the user's language; frontmatter keys stay English.
- Korean-content search caveat: common wiki search layers tokenize by whitespace under a Unicode `\w` regex — no morphological analysis, so Korean particles break matching ("최적화를" ≠ "최적화").
  1. Node titles: natural-language Korean. `aliases:`: english kebab-case duplicates.
  2. Tags: lowercase English, hierarchical (`#evolution/hardened`).
  3. Filenames: proper nouns without particles (preserves wikilink stem matching).

---

## 10. Scope CLAUDE.md — Required Sections

Every scope's `CLAUDE.md` must contain (template: `templates/SCOPE_CLAUDE.md`):

1. Purpose & topic boundaries (one paragraph) **and the `### Goal & Open Decisions` block** (§1): the goal in one line, plus one `| ID | decision | open｜settled｜superseded |` row per decision the scope exists to settle. This block is what every relevance rule reads — target selection (§4 Phase B), verification depth (§5.1), the pruning sweep (§4 Phase C), and the §7 counters. A scope may start with one decision; starting with none leaves the loop unsteered, and `wiki-lint.py` says so (`no_decisions_declared`) as soon as evolving nodes exist. Keeping it current is part of the work: settling a decision means flipping its row, which is what lets the next session prune what it carried.
   The table is read loosely on purpose: extra columns past the third are ignored (a `Notes` column is just a column), the status cell is read by its **first word** so a qualifier may follow it, `\|` is a literal pipe inside a cell, and the heading may be written with `and` for `&`. A row whose first cell is `D<digits>` **always** declares its decision — as `open` if the status cannot be read at all — because a row silently falling out of this table retires its decision, and a retired decision turns every node serving it into a prune candidate (§5.1, §4 Phase C). Anything unreadable is reported as `unparsed_decision_rows` rather than dropped, so the failure is visible instead of silent.
2. **Metadata**: real code-workspace path(s) — the scope is not a code workspace.
3. Protocol pointer: "This scope follows the re:Harmoniz protocol (`reharm` plugin, EVOLUTION.md)."
4. Adversarial verification summary (§5 — the channel that injects the rubric into any research loop running inside the scope), including the depth tiers (§5.1) so a loop running inside the scope does not spend three refuters on a node nothing rests on.
5. Seed source candidates (input queue for `reharm:root`).
6. Optional toggles: `Web search: disabled`, custom re-verification cadence, **source policy** (preferred/excluded sources — e.g. prefer peer-reviewed / official / primary, never cite social media or undated pages as high-confidence; this scopes the §6 evidence lens per domain), `Research escalation:` (the §13 deep-research entry point — unset keeps the bridge closed), and `Allowed external wikilinks:` (deliberate cross-scope stems; lint reports them as `allowed_external` instead of unresolved noise).

---

## 11. File Templates

### 11.1 Evolution Report — `wiki/meta/evolution/E####.md`

The report owns the *process* (what changed and why); node bodies own only results (§8). Decision-log style, append-only, written in the user's language (§9).

**Length discipline — the report is an audit record, not a second wiki (target ≤40 lines):**

- `## Mutations` — ≤2 lines per target: what changed, from which material.
- `## Verdicts` — one line per node, **opening with the depth it was judged at** (§5.1): `[[node]] — full: coherence ✓ · evidence ✗ · reproducibility ✓ → 2/3` or `[[node]] — single(evidence) ✓`. A reason clause is added **only for refuted lenses and re-judgings**. That clause is the archive of the full objection the node compresses away (§2) — a surviving lens gets the mark, never a narrative.
- `## Pruned` — one line per node cut, with its §3 reason. Prune lines are as load-bearing as promotions: they are how a reader later reconstructs why a decision stopped needing a branch.
- `## Promotions` — one line each, with its §3 evidence.
- `log.md` entries are exactly **one line** — `## [date] <skill> | <one-line summary>` — detail belongs to the report; `hot.md` stays ~500 words.

```markdown
---
type: meta
title: "E0001 — <one-line session verdict>"
created: 2026-06-12
session: E0001
decision: D1                        <!-- the open decision this session served (§4 Phase B) -->
targets: ["[[node-a]]", "[[node-b]]"]
---

# E0001 — <one-line session verdict>

## Decision & Targets    <!-- Phase B: the active decision, candidates presented, the user's picks, rationale -->

## Mutations             <!-- Phase C: per node — what changed, from which material; new mashups -->

## Verdicts              <!-- Phase D: per node — depth, lens outcomes, objections absorbed -->

## Pruned                <!-- §3 prunes applied, each with its reason; [] when none -->

## Culled & Rolled Back  <!-- deprecations and Phase A rollbacks, with reasons -->

## Promotions            <!-- promotions proposed/applied, each with its §3 evidence -->

## Decision movement     <!-- did the active decision move? settled / closer + what remains / unmoved + why -->

## Next                  <!-- candidates and open questions for the next session -->
```

`## Decision movement` is the section a reader checks first, and the one that makes a hollow session visible: three sessions of "unmoved" is exactly what §7's third change-strategy trigger counts.

### 11.2 Index — `wiki/index.md`

Master catalog + maturity census, always current (§8). Claims and mashups are mandatory rows; sources/ and questions/ may get separate tables. The **Decisions** table comes first: it is the scope's scoreboard, and reading it should answer "how far along are we?" without opening anything else.

```markdown
# Index — <scope name>

**Decisions:** 3 declared · 2 open · 1 settled (2026-06-12)

| ID | Decision | Status | Serving nodes | hardened+ |
|---|---|---|---|---|
| D1 | Replace 32-bit Adam with 8-bit? | open | 4 | 2 |
| D2 | Stable-embedding layer before shipping? | settled | 2 | 2 |

**Census:** 12 nodes · seed 5 · developing 3 · hardened 2 · evergreen 0 · deprecated 1 · pruned 1 (2026-06-12)

| Node | Type | Serves | Status | Gen | Confidence | Updated |
|---|---|---|---|---|---|---|
| [[claim-x]] | claim | D1 | developing | 3 | medium | 2026-06-11 |
| [[claim-y]] | claim | — | pruned | 2 | medium | 2026-06-11 |

## Deliverables            <!-- §14 — outside the maturity census -->

| Deliverable | Answers | Confidence floor | Updated |
|---|---|---|---|
| [[answer-x]] | D1 | medium | 2026-07-02 |
```

The `Serves` column is what makes the prune queue visible at a glance: a long run of `—` rows in a scope with open decisions is the signal that atomization outran the decisions (§1).

---

## 12. Field Experiment Bridge

The `hardened → evergreen` gate (§3) is the only one that cannot be opened from inside the wiki — it needs a real-world result, and *the scope is not a code workspace* (§10). This section fixes how a stuck claim becomes a field experiment and how the result returns, without re:Harmoniz ever running code or touching the code workspace's git.

Three layers, each owning one thing — and they must not bleed into each other:

| Layer | Who | Owns | Does **not** |
|---|---|---|---|
| **DESIGN** | the experiment-design skill (in this scope) | the pre-registration node (§2): hypothesis, confirm/refute criterion, conditions to record, runner goal + shape | author code-level metric / verify commands; run anything |
| **OPERATIONALIZE** | external runner's planner (reference: `/autoresearch:plan`) | turn the goal into a validated, dry-run-checked run config (scope globs, metric, verify command) **in the code workspace** | decide whether the claim is testable; touch the wiki |
| **EXECUTE** | external runner (reference: `autoresearch`) | run the bounded experiment; emit a result report | adjudicate the claim; write into the wiki |

- **Tool-agnostic.** The protocol fixes the *seam*, not the tool. Any runner is acceptable; `autoresearch` is the reference. The runner entry point is recorded per node as `runner:` (§2) and/or per scope in `CLAUDE.md` (§10) — never inferred.
- **The human crosses the workspace boundary.** The design skill stops at a handoff command and never executes it; the user carries the spec into the code workspace and runs the planner there. The research scope and the code workspace are usually different directories/repos, so this hop is a deliberate boundary crossing, not a missing automation.
- **Return path.** The runner's report lands in `.raw/experiments-results/` (the field-origin convention, §1) → `reharm:root` summarizes it into `sources/` → `reharm:reharmonization` Phase C imports it, judged against the node's pre-registered criterion (§4 Phase C), and flips the experiment node to `imported`.
- **Decision gate.** Only experiments that can change an action get pre-registered. Before fixing a criterion, name — in the node's `## Decision at stake` (§2) — what differs **outside the wiki** under CONFIRM versus REFUTE. Name the declared decision (§1) it serves; if the run bears on none, that is the answer. The two rows must differ, and neither may be a wiki-internal event: "the evergreen gate opens", "the node is promoted", "the claim's scope narrows" all **fail** the gate, because a maturity label is bookkeeping, not a decision. If the honest answer is that nothing outside the wiki moves either way, the run is a record-keeping exercise — redirect to `reharm:reharmonization` (the claim can still be scoped, corroborated, and refuted without a measurement). Note the gate is about the *decision context*, while the testability gate below is about the *claim*: the two are independent, and a proposal must clear both. A gate cleared at authoring time can still lapse later — Phase C's prune sweep (§4) is what catches that.
  - **This gate is no longer local to experiments.** It began here, as the most expensive step's admission test, and §1 now applies the same question at every step that spends anything: what a source atomizes into, which node a session targets, how many lenses it earns, and whether it is kept at all. What remains specific to §12 is the *pre-registration* discipline — freezing the criterion before the run.
- **Testability gate.** Only empirically testable claims get an experiment. Definitional / analytical / historical claims have no runnable result; their evidence path is independent-source corroboration (§3 developing→hardened) and the §5 refuters — the design skill detects this and redirects rather than forcing a metric.
- **`reharm:pushing` only points here.** It detects a claim stuck at the evergreen gate and recommends the design skill (read-only, §3/§4 "nothing is auto-decided"); it never authors the spec itself.

---

## 13. Deep Research Bridge

§12 opens the one gate the wiki cannot open from inside (`hardened → evergreen`). This section is its sibling for the **evidence gate** (`developing → hardened`, §3): when a literature-class claim sits short of ≥2 independent sources session after session — or an open question refuses to die — the bounded §6 web pass is often too shallow, and churning it again is exactly what §7 calls stagnation. A **deep research escalation** hands the question to an external deep-research loop and routes its report back in as raw material. **Manual-only (v1):** `reharm:pushing` recommends it, the user decides; the autonomous loop template never triggers it.

Three phases, on the same declared-seam pattern as §12 (tool-agnostic — the protocol fixes the seam, not the tool):

| Phase | Who | Owns | Does **not** |
|---|---|---|---|
| **DESIGN** | in-scope: the user, typically via a `reharm:critique` escalate verdict | flipping the question node to `status: escalated` (§2) and writing its `## Escalation` block | run any research |
| **EXECUTE** | the external deep-research tool named by the scope `CLAUDE.md` `Research escalation:` toggle (§10) | running the research outside the session; emitting a report | adjudicate claims; write into the wiki |
| **RETURN** | `reharm:root` → `reharm:reharmonization` | landing the report from `.raw/deep-research/` (§1) as sources + claims; importing through Phase C/D | skip §5 verification |

- **DESIGN — escalation is question-shaped.** The unit is a `wiki/questions/` node, never a claim: flip it to `status: escalated` and write an `## Escalation` block that answers one thing — **"what would change our mind?"**: the missing independent evidence, the counterexample that would settle it, and wikilinks to the claim(s) it serves. Without that block an escalation is just "search more," which §6 already does; with it, the returning report can be judged against a criterion fixed in advance (the same pre-registration discipline as §12).
- **EXECUTE — the toggle is the gate.** The entry point lives in the scope `CLAUDE.md` (`Research escalation:` — §10), same pattern as §12's `runner:`. Toggle unset → the bridge is closed and pushing never recommends it. The tool runs **outside** the session (the user carries the question across, as in §12); its report lands in `.raw/deep-research/`.
- **RETURN — secondary by construction.** `reharm:root` atomizes the report like any source, but its `sources/` page records `origin: secondary` and `derived_from:` the primaries it digests (§2); where a primary matters, land and cite it directly. The next reharmonization session imports the material through Phase C/D, and the question flips `escalated → answered` when its claims move. **That is how §13 opens the §3 developing→hardened gate**: by delivering the independent sources the gate demands — with independence still adjudicated by the §5 evidence lens (`derived_from` overlap = non-independent), so a deep-research digest can never double-count as two sources.
- **`reharm:pushing` only points here** (cascade, right after the §12 experiment rule): a **literature-class** `developing` claim that is **load-bearing for an open decision** (§5.1) with no new independent source for ≥2 sessions, or an `open` question with no progress for ≥4 sessions, while the toggle is set → recommend escalation, read-only. (A field-class claim stuck at the same gate routes to the §12 experiment rule instead — searching cannot supply replication. A claim that is *not* load-bearing for any open decision routes to the prune sweep instead — escalating deep research for a node nothing rests on is the most expensive way to learn something no decision uses.) The autonomous loop template **skips** this recommendation entirely (manual-only v1) and falls through to the next candidate.

---

## 14. Deliverables — Answer Synthesis

The loop prunes and hardens *claims*; a **deliverable** is the exit: one page that answers a declared decision (or a central question) from what survived, written by `reharm:ensemble`. A wiki that only accumulates hardened nodes has no outlet — a decision can sit fully answered in pieces with nowhere the answer actually lives (field-evidenced: a scope reached a hardened core and simply hit a ceiling). The deliverable is that outlet, and it is deliberately **not** a knowledge node (§2 schema: `type: deliverable`, non-evolving).

- **Identity = what it answers.** One deliverable per decision or question (`question:` is the identity key — a decision ID or a `questions/` wikilink). Re-synthesis **updates the same file in place** and bumps `updated`; versions belong to git (§8) — never a `-v2` file. Node states everywhere else are **invariant**: ensemble reads claims, it never touches them (flipping the answered question's status, or the decision's row to `settled`, is a critique/reharmonization act).
- **Synthesize as soon as the decision can be taken, not when the census looks impressive.** The threshold is whether a practitioner could act from the bottom line, with the caveats stated — not a node count and not a maturity level. A provisional answer resting on `developing` nodes, with its soft spots listed under `## Load-bearing seeds` and its confidence floor set honestly, is more useful than no answer: it exposes exactly which branch needs the next session. Re-run it as the core hardens.
- **Body contract** — four sections, in the scope's content language:
  - `## Answer` — the synthesis. **It opens with a bottom line**: at most 3 plain-language lines — the verdict, the condition it rides on, the next action. A practitioner must be able to act from those three lines alone; the synthesis that justifies them follows. **Every load-bearing sentence carries an inline snapshot citation**: `…conclusion… ([[node]] hardened · high · g6)`. The deliverable is point-in-time — the node keeps evolving after the sentence is written, so the sentence records what the node *was* when cited.
  - `## Load-bearing seeds` — the seed/developing nodes the answer had to lean on despite their immaturity, each with its snapshot. The answer's soft underbelly, listed rather than hidden.
  - `## Open caveats` — unresolved objections, contradictions, and open questions that bound the answer.
  - `## What would change this conclusion` — the §13 discipline applied to the whole answer: the evidence or counterexample that would force a rewrite.
- **Load-bearing = verdict-changing.** A cited claim is load-bearing **iff negating it would change a verdict sentence in `## Answer`** — exactly the set `## What would change this conclusion` enumerates (the two must agree; auditing one audits the other). Background, history, and color citations are not load-bearing and never set the floor.
- **Confidence propagates from the floor.** Directly under the H1, one header line: `**Confidence:** <floor> — floor set by the weakest load-bearing claim: [[node]] (status · confidence · gen)`. Fixed rule: the deliverable's confidence **is** the minimum confidence among its load-bearing claims (the verdict-changing set above) — deliverable-level optimism is forbidden, and the header names the weakest link so the reader knows exactly where the answer would crack first. When the answer carries several verdict axes (per-method or per-sub-question sections), each axis may state its own floor line over its own load-bearing claims — a strong axis is allowed to look strong; the header floor stays the minimum across axes.
- **Non-evolving by construction**: no generation, no refuters, excluded from frontier scoring (`boundary-score.py`) and the maturity census; `wiki-lint.py` validates only the §2 keys. Listed in the §11.2 Deliverables table, outside the census.
- **`reharm:pushing` recommends synthesis** (cascade, **above the momentum rule** — see the ordering note in the pushing skill) when an open decision is **answerable** and its deliverable is **absent or stale**. Answerable = the decision has ≥1 load-bearing claim at `hardened`-or-above, no unresolved contradiction among its serving nodes, and no `planned`/`running` experiment that would change the verdict. Stale = the deliverable's `updated` predates the newest `E####.md` session (evolution happened after the answer was last derived). The old threshold — five nodes anywhere in the scope at `hardened`-or-above — measured the census instead of the decision, and sat *below* the frontier/cadence rule that fires in every living scope, so the answer starved indefinitely while the wiki kept hardening.
