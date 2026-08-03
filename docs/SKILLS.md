# re:Harmoniz skills — which one, and when

**English** · [한국어](SKILLS.ko.md)

Seven evolution skills plus one setup wizard, each one command. You don't have to memorize them: when you're not sure what to do next, run [`reharm:pushing`](#reharmpushing--ask-what-now) and it reads the scope and names the move. This guide is for when you'd rather choose yourself — it maps *situations* to skills, and says what each one will and won't touch.

Every skill also fires on plain language (English or Korean), so you can say what you want instead of typing the command. The trigger phrases are listed with each skill.

## Quick chooser

| If you want to… | Run |
|---|---|
| Start a topic, or bring in a paper / repo / note / idea | [`reharm:root`](#reharmroot--bring-new-material-in) |
| Know where things stand and what to do next | [`reharm:pushing`](#reharmpushing--ask-what-now) |
| Push a claim through another generation | [`reharm:reharmonization`](#reharmreharmonization--put-a-claim-through-one-generation) |
| Resolve open questions, contradictions, stalled nodes | [`reharm:critique`](#reharmcritique--clear-the-messy-middle) |
| Cut nodes nothing is waiting on any more | [`reharm:critique`](#reharmcritique--clear-the-messy-middle) — it owns pruning too |
| Link two research scopes | [`reharm:modal-interchange`](#reharmmodal-interchange--connect-two-scopes) |
| Get real-world proof for a claim stuck one step from the top | [`reharm:experiment-design`](#reharmexperiment-design--design-real-world-proof) |
| Write up the answer to a decision | [`reharm:ensemble`](#reharmensemble--write-the-answer) |
| Run the loop unattended — set up and start in one command | [`reharm:loop-setup`](#reharmloop-setup--set-up-and-start-the-autonomous-loop) |

**Before any of them: say what the scope is for.** The scope's `CLAUDE.md` carries a `### Goal & Open Decisions` block — one row per decision you need to settle, each a thing you will *do* rather than a thing you want to know. Every skill below reads it: it decides what a source turns into, which node a session targets, how many refuters a claim earns, and what gets cut. `reharm:root` asks for it when it scaffolds a scope; `reharm:pushing` tells you if it is missing. Without it nothing breaks — the relevance rules just stay switched off.

---

## The skills, one by one

### `reharm:root` — bring new material in

**Reach for it when:** you're starting a fresh topic, or you have something new to feed an existing one — a repo URL, a paper or article, pseudocode, an old note, even a rough idea in your head.

**What happens:** the raw material is saved untouched under `.raw/` and gets a one-page `sources/` summary. Then the gate: the assertions that **bear on one of the scope's declared decisions** become `claims/` — each born at `seed · generation 1 · confidence low`, with `serves:` naming that decision. Everything else stays on the source page, still cited and searchable. Feed several things at once and each is digested in its own isolated sub-agent, so one source's framing can't bleed into another's claims. Scaffolding a new scope, it asks what decisions the scope exists to settle before it seeds anything.

**What it won't do:** it doesn't judge or harden anything — everything starts at generation 1. Grading is reharmonization's job. And it won't turn a whole paper into twenty nodes because it can: the per-source cap of 15 is a backstop, not a target, and a run that mints four nodes out of a rich source is the gate working. Each node minted here draws refuters and re-verification for the life of the scope.

**Then what:** run `reharm:reharmonization` to start pressure-testing, or `reharm:pushing` to be told which fresh node is worth evolving first.

**Just say:** *"reharm root"*, *"seed the scope"*, *"시드 투입"* — or paste a URL.

### `reharm:pushing` — ask "what now?"

**Reach for it when:** you've come back to a scope after a while, or you simply don't know what the highest-value next move is. **This is the one to run when in doubt.**

**What happens:** it reads the whole state — the declared decisions and how far each has come, the maturity census, frontier scores *per decision*, the prune queue, open contradictions, the last session's stagnation verdict, stalled evidence, whether a deliverable is missing or stale — and names one next move (declare the goal / seed / evolve / adjudicate / prune / connect scopes / design an experiment / answer a decision / escalate stuck evidence to deep research), with the evidence that triggered it.

The order is not arbitrary: **realizing value you already earned, or lowering the cost of every later session, comes before adding work.** So "this decision is answerable now" and "these branches are dead" both rank above "evolve the frontier" — as do both stagnation verdicts, which exist to stop the loop repeating itself.

**What it won't do:** it changes nothing and runs nothing. It only points. And it won't pretend to prioritize a scope that hasn't said what it is for — with no declared decisions, its answer is to go write them.

**Then what:** run whatever it recommends.

**Just say:** *"what next"*, *"where do I stand"*, *"다음 뭐 해"*, *"상태 봐줘"*.

### `reharm:reharmonization` — put a claim through one generation

**Reach for it when:** new doubt or new material has landed on a claim, or a frontier node is ripe to push. This is the core loop — the skill the project is named after.

**What happens:** one full cycle, **serving one open decision** — **Retrospect → Target (pick the decision, then the node inside it; you approve) → Mutate (revise, decompose new sources, hunt counter-evidence decision-angle-first) + prune sweep (report the branches nothing is waiting on) → Natural Selection (depth follows role: three refuters if the node is load-bearing for the decision, one lens if it only supports, none at all if nothing rests on it) → Record (`E####.md` + `index`/`hot` refresh)**. Full-depth survivors gain a generation and may promote (`seed → developing → hardened → evergreen`).

**What it won't do:** it won't promote anything that doesn't survive refutation, and it won't touch a node you didn't approve as a target. It also won't spend refuters on a node no open decision rests on — that node is reported as a prune candidate instead, because three sub-agents to grade something nobody is waiting on is pure cost. And it won't grind: after absorbing a partial collapse it re-judges **once**, then files the residue as an open question and moves on. Getting past the gates takes the claim's own evidence currency (EVOLUTION.md §3): independent sources for a literature claim, replication for a fact you measured yourself, an adoption record for a design decision — and real-world field evidence for `evergreen`. It can't be willed.

**One thing worth knowing:** a single-lens pass earns currency and a refreshed challenge date but **no generation**, and it can't open the `hardened` gate. So "generation" still means what it always did — survived the full three-lens pass — and the cheap tier never quietly inflates it. If a synthesis later needs to lean on a single-lens node, that node becomes load-bearing and takes the full pass next session. Cost follows need.

**Then what:** `reharm:critique` if the session left ambiguous residue; `reharm:pushing` to pick the next target.

**Just say:** *"evolve the wiki"*, *"run evolution"*, *"진화 돌려"*.

### `reharm:critique` — clear the messy middle, and cut the dead branches

**Reach for it when:** the backlog has piled up — open questions, contradictions sitting on two nodes, low-confidence nodes that stalled, lint warnings — **or** when nodes have accumulated that no open decision rests on any more. Both need a human ruling, not another refutation round.

**What happens:** it gathers the backlog *and* the prune queue, then interviews you. Themed items are bundled into a single multi-select triage (promote / merge / hold / archive); questions untouched for 4+ sessions are proposed as one aging batch; and the prune queue is presented in one batch grouped by reason — *unassigned*, *all its decisions are settled*, *superseded by a design decision*. Your rulings are applied: contradictions absorbed into `## Objections & Limits`, duplicates folded into their parent (the absorbed node keeps a pointer, never deleted), dead branches flipped to `pruned`.

**Two things about pruning specifically.** It is **not a judgement on the claim** — a node at `hardened · g5` can be pruned, because the only question is whether an open decision still rests on it, and the body, objections and generation are all left exactly as they were. And an unassigned node is often a **binding gap rather than a dead branch**, so *bind to a decision* is offered right next to *prune*: if the node does serve something and nobody wrote it down, say which decision and it stays.

**What it won't do:** it never raises a generation — those are earned by surviving full-depth refutation, not by your verdict — so it only adjusts `confidence`/`status`. It never auto-archives or auto-prunes: both are always *proposed*, never silent. And it never edits a claim while pruning it.

**Then what:** `reharm:reharmonization` to evolve what your rulings freed up.

**Just say:** *"critique the wiki"*, *"adjudicate"*, *"모호한 것 정리"*.

### `reharm:modal-interchange` — connect two scopes

**Reach for it when:** you have two research scopes and suspect one side's open problem is answered by the other side's mechanism.

**What happens:** light recon of both scopes surfaces the crossover, and mints a `mashups/` insight in the *current* scope whose `sources:` wikilink both originating nodes. (The name is a music term — borrowing a chord from a parallel mode.)

**What it won't do:** it never copies or edits the other scope's node — it *cites* it, keeping a single source of truth, and stamps a `borrowed:` snapshot so later donor drift surfaces as an objection instead of silent rot. The new mashup is born `seed` and must survive selection later like any node. And it won't mint a mashup that serves none of this scope's open decisions: that becomes a `questions/` entry instead. Cross-domain insight is exactly the kind of finding that feels too good not to keep and then sits unused, drawing refuters and cadence for years.

**Then what:** `reharm:reharmonization` to harden the new mashup.

**Just say:** *"modal interchange"*, *"cross-scope mashup"*, *"크로스 매쉬업"* — with the two scope names.

### `reharm:experiment-design` — design real-world proof

**Reach for it when:** a claim is stuck one step from the top — surviving refutation but blocked at the `hardened → evergreen` gate because it has no field evidence — **and a result would actually change what you do.** Being stuck at the gate is the *occasion*, not the justification; the skill checks the justification first (below).

**What happens:** first the **decision gate** — you name, in one line each, what differs *outside the wiki* under CONFIRM versus REFUTE. Then it pre-registers the experiment that would settle it: a hypothesis, that `## Decision at stake` pair, a **CONFIRM/REFUTE criterion fixed before the run** (so the result can't be rationalized after the fact), the conditions to record, and a plain-language goal handed to a runner — your external runner if the scope names one, else the plugin's default **runner-worker**, recorded on the node so you (or the autonomous loop) can launch it later.

**What it won't do:** it never runs code — it designs and records only; the actual run happens elsewhere, and its result comes back as a new source. It also **won't pre-register a decision-free experiment**: if CONFIRM and REFUTE lead to the same action, or the only thing that moves is a maturity label ("the evergreen gate opens"), it stops and sends you to `reharm:reharmonization` instead. A run whose every outcome is a relabel is record-keeping, not an experiment.

**Then what:** launch the run per the `## Handoff` block (spawn the default runner-worker, or invoke your external runner) → `reharm:root` the result → the next `reharm:reharmonization` imports it under `## Field Evidence`, which is what opens the `evergreen` gate.

**Just say:** *"design an experiment"*, *"pre-register experiment"*, *"실험 설계"*.

### `reharm:ensemble` — write the answer

**Reach for it when:** a declared decision can be **taken** — for a report, an actual choice, or a handoff. This is the loop's **exit**. Note the threshold: not "a hardened core is in place", not a node count, but *could a practitioner act from the bottom line with the caveats stated?* If yes, run it. A provisional answer that names its own weak spots beats no answer, and it shows you exactly which branch the next session should take.

**What happens:** it assembles the survivors into one `deliverables/` page that **opens with a three-line bottom line — verdict, condition, next action**. Every load-bearing sentence cites its node with a `(status · confidence · generation)` snapshot, the **weakest verdict-changing claim sets the page's confidence floor** (background citations don't — and each verdict axis may state its own floor), and unresolved caveats stay on the record under `## Open caveats`.

**What it won't do:** it never changes any node's state — the answer tracks the wiki, not the other way round. Re-running it re-derives the same page in place; it writes only `deliverables/` and the close-out files (`index`/`hot`/`log`).

**Then what:** keep evolving the core; re-run ensemble later and the page updates itself.

**Just say:** *"synthesize the answer"*, *"answer the central question"*, *"답변 합성"*, *"결론 합성"*.

### `reharm:loop-setup` — set up and start the autonomous loop

**Reach for it when:** you want the seven skills above to run *unattended* (overnight batches, long-horizon accumulation) and don't want to hand-edit the loop template.

**What happens:** it detects the scope, interviews you for the real decisions (`MAX_ITERS`, `RUN_EXPERIMENTS`, sibling scope, dynamic vs interval pacing), derives the mechanical fields itself, validates the experiment gate *before* the first tick, writes `.claude/loop.md`, and starts the native `/loop` — all in one invocation.

**What it won't do:** it decides nothing about knowledge. The unattended auto-decisions live in the loop template it writes (see the [autonomous-loop guide](../templates/loop.guide.md)), and they activate only after you answer the interview and the loop starts. It also **refuses to start on a scope with no open decision** — a loop with nothing to steer by will spend real tokens hardening whatever happens to top the frontier, and unlike you, it won't notice.

**Then what:** keep the session open and the machine awake; to stop it early, tell the loop to stop and it ends itself explicitly; re-run the wizard after a plugin upgrade to pick up template fixes.

**Just say:** *"reharm loop setup"*, *"start the evolution loop"*, *"자율 루프 설정"*, *"루프 시작"*.

---

## A natural order (but it's not linear)

A scope usually flows like this:

```
declare decisions ──▶ root ──▶ reharmonization ──▶ critique ──▶ experiment-design ──▶ ensemble
(what it's for)      (seed)    (harden)            (adjudicate    (real-world proof)   (answer
                                                    + prune)                            the decision)
                                        ╲
                                         ╲──▶  modal-interchange   (whenever a second scope exists)
```

But you rarely walk it front to back. New material re-enters at `root` at any time; `critique` fires whenever residue or dead branches build up; `modal-interchange` only matters once you have two scopes; `ensemble` runs the moment a decision is takeable and re-runs as the core hardens. Settling a decision loops back to `critique`, because the branches that served it are now prunable. When you're unsure which step you're on, `reharm:pushing` reads the state and tells you — that's the whole point of it.

## Three guarantees worth remembering

- **Generations are earned, never granted.** Only `reharm:reharmonization` raises a generation, only for nodes that survive the **full three-lens** pass. `critique` and `pushing` never do, and neither does the cheap single-lens tier.
- **`pruned` is not `deprecated`.** `deprecated` says the claim failed under refutation. `pruned` says nothing depends on it any more — the claim may be perfectly sound. Keeping them apart is what lets you read a scope's history and tell "we were wrong" from "we stopped needing this."
- **Nothing is destroyed.** Collapsed claims are `deprecated` and pruned ones are `pruned` — never deleted, and pruning is reversible if the decision reopens. The donor in a mashup is cited, not copied; a deliverable never edits the nodes it quotes. You can always trace back.

## See also

- [`README.md`](../README.md) — what re:Harmoniz is and why.
- [`EVOLUTION.md`](../EVOLUTION.md) — the full protocol, one file.
- [`templates/loop.guide.md`](../templates/loop.guide.md) — the opt-in autonomous loop that drives these skills unattended.
