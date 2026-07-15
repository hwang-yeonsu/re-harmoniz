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
| Link two research scopes | [`reharm:modal-interchange`](#reharmmodal-interchange--connect-two-scopes) |
| Get real-world proof for a claim stuck one step from the top | [`reharm:experiment-design`](#reharmexperiment-design--design-real-world-proof) |
| Write up the answer to the central question | [`reharm:ensemble`](#reharmensemble--write-the-answer) |
| Run the loop unattended — set up and start in one command | [`reharm:loop-setup`](#reharmloop-setup--set-up-and-start-the-autonomous-loop) |

---

## The skills, one by one

### `reharm:root` — bring new material in

**Reach for it when:** you're starting a fresh topic, or you have something new to feed an existing one — a repo URL, a paper or article, pseudocode, an old note, even a rough idea in your head.

**What happens:** the raw material is saved untouched under `.raw/`, gets a one-page `sources/` summary, and its factual assertions become atomic `claims/` — each born at `seed · generation 1 · confidence low`. Feed several things at once and each is digested in its own isolated sub-agent, so one source's framing can't bleed into another's claims.

**What it won't do:** it doesn't judge or harden anything — everything starts at generation 1. Grading is reharmonization's job.

**Then what:** run `reharm:reharmonization` to start pressure-testing, or `reharm:pushing` to be told which fresh node is worth evolving first.

**Just say:** *"reharm root"*, *"seed the scope"*, *"시드 투입"* — or paste a URL.

### `reharm:pushing` — ask "what now?"

**Reach for it when:** you've come back to a scope after a while, or you simply don't know what the highest-value next move is. **This is the one to run when in doubt.**

**What happens:** it reads the whole state — the maturity census, frontier scores, open contradictions, the last session's stagnation verdict, stalled evidence, whether a deliverable is missing or stale — and names one next move (seed / evolve / adjudicate / connect scopes / design an experiment / synthesize an answer / escalate stuck evidence to deep research), with the evidence that triggered it.

**What it won't do:** it changes nothing and runs nothing. It only points.

**Then what:** run whatever it recommends.

**Just say:** *"what next"*, *"where do I stand"*, *"다음 뭐 해"*, *"상태 봐줘"*.

### `reharm:reharmonization` — put a claim through one generation

**Reach for it when:** new doubt or new material has landed on a claim, or a frontier node is ripe to push. This is the core loop — the skill the project is named after.

**What happens:** one full cycle — **Retrospect → Target (you approve which nodes) → Mutate (revise, decompose new sources, hunt counter-evidence) → Natural Selection (three refuters, one lens each — coherence · evidence · reproducibility; ≥2/3 must survive) → Record (`E####.md` + `index`/`hot` refresh)**. Survivors gain a generation and may promote (`seed → developing → hardened → evergreen`).

**What it won't do:** it won't promote anything that doesn't survive refutation, and it won't touch a node you didn't approve as a target. Getting past `hardened` needs independent sources and real-world field evidence — it can't be willed.

**Then what:** `reharm:critique` if the session left ambiguous residue; `reharm:pushing` to pick the next target.

**Just say:** *"evolve the wiki"*, *"run evolution"*, *"진화 돌려"*.

### `reharm:critique` — clear the messy middle

**Reach for it when:** the backlog has piled up — open questions, contradictions sitting on two nodes, low-confidence nodes that stalled, lint warnings. The residue that needs a human ruling, not another refutation round.

**What happens:** it gathers that backlog and interviews you. Themed items are bundled into a single multi-select triage (promote / hold / archive); questions untouched for 4+ sessions are proposed as one aging batch. Your rulings are applied — contradictions absorbed into `## Objections & Limits`, questions sharpened or filed.

**What it won't do:** it never raises a generation — those are earned by surviving refutation, not by your verdict — so it only adjusts `confidence`/`status`. And it never auto-archives: aging is always *proposed*, never silent.

**Then what:** `reharm:reharmonization` to evolve what your rulings freed up.

**Just say:** *"critique the wiki"*, *"adjudicate"*, *"모호한 것 정리"*.

### `reharm:modal-interchange` — connect two scopes

**Reach for it when:** you have two research scopes and suspect one side's open problem is answered by the other side's mechanism.

**What happens:** light recon of both scopes surfaces the crossover, and mints a `mashups/` insight in the *current* scope whose `sources:` wikilink both originating nodes. (The name is a music term — borrowing a chord from a parallel mode.)

**What it won't do:** it never copies or edits the other scope's node — it *cites* it, keeping a single source of truth, and stamps a `borrowed:` snapshot so later donor drift surfaces as an objection instead of silent rot. The new mashup is born `seed` and must survive selection later like any node.

**Then what:** `reharm:reharmonization` to harden the new mashup.

**Just say:** *"modal interchange"*, *"cross-scope mashup"*, *"크로스 매쉬업"* — with the two scope names.

### `reharm:experiment-design` — design real-world proof

**Reach for it when:** a claim is stuck one step from the top — surviving refutation but blocked at the `hardened → evergreen` gate because it has no field evidence.

**What happens:** it pre-registers the experiment that would settle it: a hypothesis, a **CONFIRM/REFUTE criterion fixed before the run** (so the result can't be rationalized after the fact), the conditions to record, and a plain-language goal handed to a runner — your external runner if the scope names one, else the plugin's default **runner-worker**, recorded on the node so you (or the autonomous loop) can launch it later.

**What it won't do:** it never runs code. It designs and records only; the actual run happens elsewhere, and its result comes back as a new source.

**Then what:** launch the run per the `## Handoff` block (spawn the default runner-worker, or invoke your external runner) → `reharm:root` the result → the next `reharm:reharmonization` imports it under `## Field Evidence`, which is what opens the `evergreen` gate.

**Just say:** *"design an experiment"*, *"pre-register experiment"*, *"실험 설계"*.

### `reharm:ensemble` — write the answer

**Reach for it when:** a hardened core is in place and you want the scope's central question actually answered on one page — for a report, a decision, or a handoff. This is the loop's **exit**.

**What happens:** it assembles the survivors (hardened claims, mashups) into one `deliverables/` page. Every load-bearing sentence cites its node with a `(status · confidence · generation)` snapshot, the **weakest load-bearing claim sets the page's confidence floor**, and unresolved caveats stay on the record under `## Open caveats`.

**What it won't do:** it never changes any node's state — the answer tracks the wiki, not the other way round. Re-running it re-derives the same page in place; it writes only `deliverables/` and the close-out files (`index`/`hot`/`log`).

**Then what:** keep evolving the core; re-run ensemble later and the page updates itself.

**Just say:** *"synthesize the answer"*, *"answer the central question"*, *"답변 합성"*, *"결론 합성"*.

### `reharm:loop-setup` — set up and start the autonomous loop

**Reach for it when:** you want the seven skills above to run *unattended* (overnight batches, long-horizon accumulation) and don't want to hand-edit the loop template.

**What happens:** it detects the scope, interviews you for the real decisions (`MAX_ITERS`, `RUN_EXPERIMENTS`, sibling scope, dynamic vs interval pacing), derives the mechanical fields itself, validates the experiment gate *before* the first tick, writes `.claude/loop.md`, and starts the native `/loop` — all in one invocation.

**What it won't do:** it decides nothing about knowledge. The unattended auto-decisions live in the loop template it writes (see the [autonomous-loop guide](../templates/loop.guide.md)), and they activate only after you answer the interview and the loop starts.

**Then what:** keep the session open and the machine awake; to stop it early, tell the loop to stop and it ends itself explicitly; re-run the wizard after a plugin upgrade to pick up template fixes.

**Just say:** *"reharm loop setup"*, *"start the evolution loop"*, *"자율 루프 설정"*, *"루프 시작"*.

---

## A natural order (but it's not linear)

A scope usually flows like this:

```
root  ──▶  reharmonization  ──▶  critique  ──▶  experiment-design  ──▶  ensemble
(seed)     (harden)             (adjudicate)   (real-world proof)      (answer)
                    ╲
                     ╲──▶  modal-interchange   (whenever a second scope exists)
```

But you rarely walk it front to back. New material re-enters at `root` at any time; `critique` fires whenever residue builds up; `modal-interchange` only matters once you have two scopes; `ensemble` can be run early for a provisional answer and re-run as the core hardens. When you're unsure which step you're on, `reharm:pushing` reads the state and tells you — that's the whole point of it.

## Two guarantees worth remembering

- **Generations are earned, never granted.** Only `reharm:reharmonization` raises a generation, and only for nodes that survive refutation. `critique` and `pushing` never do.
- **Nothing is destroyed.** Collapsed claims are `deprecated`, not deleted; the donor in a mashup is cited, not copied; a deliverable never edits the nodes it quotes. You can always trace back.

## See also

- [`README.md`](../README.md) — what re:Harmoniz is and why.
- [`EVOLUTION.md`](../EVOLUTION.md) — the full protocol, one file.
- [`templates/loop.guide.md`](../templates/loop.guide.md) — the opt-in autonomous loop that drives these skills unattended.
