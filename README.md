# re:Harmoniz

**English** · [한국어](README.ko.md)

[![latest version](https://img.shields.io/github/v/release/hwang-yeonsu/re-harmoniz?label=version&sort=semver&color=blue)](https://github.com/hwang-yeonsu/re-harmoniz/releases)

> **A research loop that settles decisions** — a Claude Code plugin (`reharm`).

**re:Harmoniz = re·search + re·harmoniz·ation.** Hold the *decisions you need to make* fixed and re-derive what sits beneath them — the **claims, and the evidence they rest on** — generation after generation. (The name borrows *reharmonization* from music: keep the melody, rework the chords under it.)

You declare, up front, the decisions a scope exists to settle. Claims are the **branches** under those decisions. Research grows the branches; verification **prunes** them. A branch nothing is waiting on gets cut, however true it is; a branch a decision rests on gets three adversarial refuters and has to survive. Progress is measured in decisions settled — not in how much the wiki knows.

It's all plain Markdown you own. The entire protocol is one file: [`EVOLUTION.md`](EVOLUTION.md).

## Why not just a wiki?

Most knowledge tools — Zettelkasten vaults, Notion, "LLM wiki" note stores — **accumulate**: every note you add counts equally, and the pile only grows. re:Harmoniz is built for **engineering research**, where the point is to act, so it does two things a note store cannot:

- **Every node has to earn its keep.** A source becomes claims only where it bears on a declared decision; the rest stays on the source page, recorded and citable but free. Nodes that stop mattering are `pruned` — a status distinct from `deprecated`, because "nothing depends on this" is not the same finding as "this was wrong."
- **Verification depth follows what rests on the node.** A claim a decision hinges on gets all three refuters and must survive ≥2/3. A supporting detail gets one lens. A claim no open decision rests on gets none — it gets pruned instead. Rigor is aimed, not sprayed.
- **Progress is decisions settled, not generations gained.** The session evaluator counts `decisions_settled` and `branches_pruned` first, and flags three sessions of rising generations with no decision movement as `change-strategy` — the failure mode that reads as healthy under every other metric.
- **Disagreement stays on the record.** Contradictions live on *both* nodes until you adjudicate; collapsed claims are deprecated, never deleted. The wiki defends its own conclusions.

That's the difference: a **decision-directed research engine**, not a note store — and not a truth engine either. Splitting a mixed assertion into ever-finer propositions raises a maturity number without moving a decision, and a proposition fine enough to be cleanly true is usually too fine to act on.

## The loop

```
  declare the decisions      D1: replace 32-bit Adam with 8-bit?   (open)
      │
      ▼
  seed a branch          ── a source becomes claims only where a decision rests on it
      │
      ▼
  mutate                 ── revise, decompose new sources, hunt counter-evidence
      │
      ▼
  prune                  ── cut branches no open decision depends on   ─▶ pruned
      │
      ▼
  natural selection      ── depth follows role: 3 refuters if load-bearing, 1 lens if not
      │
      ├─ survives ─▶ generation +1, promote: seed → developing → hardened → evergreen
      └─ collapses ─▶ deprecated (kept on record — never deleted)
      │
      ▼
  answer the decision    ── one citable page, as soon as it can be acted on
```

Run it whenever new material or new doubt piles up. Nothing is auto-decided: you pick the targets, you adjudicate the ambiguous ones, and you decide what gets pruned.

## Skills

| Skill | What it does |
|---|---|
| `reharm:root` | Entry point. Scaffolds a scope — asking what decisions it exists to settle — then seeds it: throw in a repo URL, article, pseudocode, an existing note, or a rough idea → it lands in `.raw/` and becomes `claims/` **only where it bears on one of those decisions** (all born generation 1); the rest stays on the source page. Several sources fan out to isolated sub-agents — one per source — so no source's framing leaks into another's claims. |
| `reharm:reharmonization` | One evolution session, serving one open decision — the namesake skill: Retrospect → Target (pick the decision, then the node; you approve) → Mutate + prune sweep → Natural Selection (3 refuters if the node is load-bearing, 1 lens if not, none if nothing rests on it) → Record. |
| `reharm:modal-interchange` | Cross-scope mashup — borrow knowledge from a parallel scope (like borrowing chords from a parallel mode) and mint cross-domain insights, citation-only. Each mashup carries a `borrowed:` snapshot of the donor's state, so later donor drift surfaces as an objection instead of silent rot. |
| `reharm:critique` | Adjudication **and pruning** — gathers the ambiguous backlog (open questions, stalled nodes, contradictions, lint warnings) *and* the prune queue (nodes bound to no open decision, or only to settled ones) and resolves both through a short interview: themed bundles get one multi-select triage, and prunes are proposed — never automatic — with *bind to a decision* offered alongside, since a missing binding is often a gap rather than a dead branch. |
| `reharm:pushing` | Orientation (read-only). Reads the scope's declared decisions plus its wiki state and recommends the next move — declare the goal, seed, evolve, adjudicate, prune, answer, or escalate stuck evidence to deep research — with the evidence behind it. Ordered so that realizing value already earned, or lowering the cost of every later session, outranks adding work. Changes nothing; you decide. |
| `reharm:experiment-design` | Field-experiment designer. For a claim stuck at the `hardened → evergreen` gate **whose result would change an action**, it **pre-registers** the experiment that would confirm or refute it — hypothesis, a `## Decision at stake` pair naming what differs *outside the wiki* under each outcome (the decision gate; if nothing does, it redirects instead), a CONFIRM/REFUTE criterion fixed before the run, the conditions to record — then hands a plain-language goal to a runner — an external one you configure (e.g. `autoresearch`), or by default the plugin's **runner-worker**, an isolated sub-agent recorded on the node and launched later by you or the autonomous loop. Designs and records only; never runs code. |
| `reharm:ensemble` | Answer synthesis — the loop's **exit**. Assembles what survived into one `deliverables/` page that answers a declared decision (or the scope's central question), opening with a three-line bottom line a practitioner can act on: every load-bearing sentence cites its node with a (status · confidence · generation) snapshot, the weakest load-bearing claim sets the confidence floor, and open caveats stay on the record. Run it **as soon as the decision can be taken**, not once the census looks impressive. Update-in-place; node states never change. |

> **Not sure which to run?** [`docs/SKILLS.md`](docs/SKILLS.md) is a friendly, situation-first guide — *"I want to X → run Y"* — that says what each skill does and won't touch. (Or just run `reharm:pushing` and it names the next move for you.)

## Usage scenarios

**Deciding whether to adopt a technique.** You need to answer *"do we switch to this optimizer?"* — declare it as `D1`, then `reharm:root` a couple of papers and the reference repo. Only the findings that would flip D1 become claims; the rest stays on the source pages. Weeks later a new result contradicts one — run `reharm:reharmonization`: the refuters test both, the loser is deprecated *with its reasons on record*, the survivor gains a generation and now cites two independent sources. When D1 can be answered, `reharm:ensemble` writes the page you act on.

**A literature review that defends itself.** Declare the decisions the review is meant to inform, then atomize papers against them. Contradictions across papers stay explicit on *both* nodes until you settle them in `reharm:critique`. The `index.md` Decisions table shows how far each decision has come; the maturity census shows what's solid (hardened/evergreen) versus still speculative (seed).

**Competitive / market analysis.** Seed vendor docs, benchmarks, and field reports. Adversarial verification strips marketing claims that have no independent backing; only assertions that survive the evidence lens harden. Real usage that later confirms or breaks a claim gets appended under `## Field Evidence`.

**Connecting two research tracks.** Once you have two scopes — say one on *training* and one on *serving* — `reharm:modal-interchange` finds where one side's open problem is answered by the other side's mechanism, and mints a cross-domain insight, cited back to both originals (single source of truth).

**Coming back to a scope cold.** Weeks later you reopen the scope and don't remember where it stands. `reharm:pushing` reads the decision block, the maturity census, the frontier scores per decision, the prune queue, the open contradictions, and the last session's stagnation verdict, then names the next move — *answer a decision that's now answerable* (`ensemble`), *prune dead branches* (`critique`), *evolve a frontier node* (`reharmonization`), *seed new material* (`root`) — with the evidence behind each. It's read-only: it points, you decide and run the skill.

**Catching a scope that's busy but not moving.** Six sessions in, generations are climbing, lint is clean, survival rate is high — and not one decision has moved. The session evaluator counts that pattern directly and returns `change-strategy`, and `pushing` says plainly that the wiki is hardening things nobody is waiting on. Every other metric in the scope reads healthy, which is exactly why this one is counted.

<details>
<summary><b>A full walkthrough — one topic across all seven skills</b></summary>

The scope is `Research_optimizers` (training-time optimization for your ML pipeline); a parallel scope, `Research_serving`, already exists for inference.

**⓪ Declare the decision** — before any research, the scope `CLAUDE.md` says what it is for:

```markdown
### Goal & Open Decisions

**Goal:** cut the training pipeline's memory budget without losing model quality

| ID | Decision to settle | Status |
|---|---|---|
| D1 | Do we switch the training config to 8-bit Adam? | open |
```

Note what D1 is not: it is not *"is 8-bit Adam as good as 32-bit?"* That is a question about the world. D1 is a thing you will do or not do, and every later step is measured against it.

**① Seed it — `reharm:root`**

```bash
cd 01_Projects/Project_A/Research_optimizers
/reharm:root https://github.com/bitsandbytes-foundation/bitsandbytes
/reharm:root "paper: 8-bit Optimizers via Block-wise Quantization (Dettmers et al., 2022)"
```

The repo dump and paper land in `.raw/` and each gets a `sources/` summary. The paper makes perhaps twenty assertions; **two of them bear on D1**, so two become claims — `claims/8bit-adam-matches-32bit-quality.md` and `claims/stable-embedding-required-for-8bit.md`, born `seed · generation 1 · confidence low · serves: ["D1"]`. The other eighteen — block-wise quantization internals, benchmark tables, related-work framing — stay on the source page, cited whenever they matter and costing nothing. Each run atomizes inside an **isolated sub-agent**, so seeding several sources never lets one's framing bleed into another's.

**② First evolution — `reharm:reharmonization` (writes `E0001.md`)**

Phase B picks D1 (the only open decision), then asks for the frontier *inside* it — `boundary-score.py --serves D1` — and surfaces the fresh node; you approve it. Phase C hunts counter-evidence on the web, decision angle first. Phase D judges at **full depth**, because flipping this claim flips D1: three refuters — *coherence · evidence · reproducibility*; the reproducibility lens lands a counterexample (*training diverges without a stable-embedding layer*), but **2/3 survive**.

→ `generation → 2`, `seed → developing`, `confidence medium`; the counterexample is absorbed into the claim's `## Objections & Limits`; `E0001.md` logs the three verdicts; `index.md` + `hot.md` refresh. *Not `hardened` yet — that gate needs a second **independent** source.*

**③ Second evolution — `reharm:reharmonization` (writes `E0002.md`), weeks later**

A new independent paper has arrived in `.raw/` (via `reharm:root`). Phase A re-verifies the E0001 node — still holds. Phase C decomposes the new paper, spinning off `claims/stable-embedding-required-for-8bit.md` (seed) and supplying the **second independent source** the main claim was missing. It survives refutation again → `generation 3`, and with *survived verification + 2 independent sources* it now promotes `developing → hardened`.

**④ Resolve the ambiguous — `reharm:critique`**

Two sources disagree: one says quality holds at every scale, another reports degradation above ~65B — so the node carries a `> [!contradiction]` callout. `reharm:critique` gathers this backlog and interviews you; you rule *"scope the claim to ≤65B; >65B is an open question."* The callout is removed and absorbed into `## Objections & Limits`, a sharpened question is filed in `questions/`, and `confidence` is reaffirmed. Note: critique adjusts `confidence`/`status` only — **it never raises `generation`** (generations are earned by surviving refutation, not by your verdict).

**⑤ Borrow from a parallel scope — `reharm:modal-interchange`**

```bash
/reharm:modal-interchange Research_optimizers Research_serving
```

Cheap recon (`hot.md` → `index.md`) of both scopes finds a crossover: serving's claim *"INT8 weight quantization needs per-channel calibration to stay accurate"* and optimizers' *"8-bit needs a stable-embedding layer"* are the **same failure mode** — quantization breaks at one sensitive layer until you anchor it structurally. It mints `mashups/quantization-stability-shared-failure-mode.md` in **this** scope (born seed), whose `sources:` wikilink **both** originating nodes. The serving node is cited, never copied or edited (single source of truth) — and it goes through natural selection in a later session like any other node.

**⑥ Real-world proof → `evergreen`**

Before the run you **pre-register** the experiment with `reharm:experiment-design` — it first makes you name the decision at stake (CONFIRM → keep 8-bit Adam in the training config; REFUTE → revert to 32-bit and re-budget the memory), then fixes the CONFIRM/REFUTE criterion in advance (CONFIRM if the eval-loss gap stays < tolerance at ≤65B), so the result can't be rationalized after the fact, and hands the goal to an external runner. You finally run 8-bit Adam in your actual pipeline; at your scale (≤65B) it matches 32-bit within noise. The experiment report lands in the scope's `.raw/experiments-results/` (the field-origin convention) and gets a `sources/` summary via `reharm:root`. The next `reharm:reharmonization`'s Phase C imports its conclusion — **with the conditions it held under (≤65B)** — into the claim's `## Field Evidence`. Because those conditions match the claim's scope (narrowed to ≤65B in ④) and no open counterexample remains, that single field-evidence entry opens the last gate: `hardened → evergreen`. (Had the result held only under narrower conditions, you'd have scoped the claim down further or held evergreen back.)

**⑦ Answer the decision — `reharm:ensemble`**

D1 is now answerable, so it gets one page: `deliverables/8bit-adam-answer.md`, its `question:` set to `D1`. Every load-bearing sentence cites its node with a snapshot (`[[8bit-adam-matches-32bit-quality]] evergreen · high · g5`), the **confidence floor** in the header is set by the weakest load-bearing claim, and the open >65B question from ④ stays on the record under `## Open caveats`. Re-running ensemble after later sessions re-derives the same file in place — the answer tracks the wiki, never the other way round, and no node's state changes.

**⑧ Settle it, then prune what carried it — `reharm:critique`**

You act on the answer and flip D1 to `settled`. The next session's prune sweep then lists the nodes that served only D1 — the benchmark bound, the memory-ratio detail — as prune candidates. You keep the two that also bear on a still-open decision and prune the rest: `status: pruned`, bodies verbatim, generations intact, inbound links still resolving. They stop drawing refuters and re-verification the day they stop mattering, and if D1 ever reopens they flip straight back.

**What you read between sessions:** `index.md` (the **Decisions** table first — how far each decision has come — then the maturity census), `hot.md` (what just changed), and `meta/evolution/E####.md` (why each change happened, with a `## Decision movement` line) — or run `reharm:pushing` to read them for you and name the next move (read-only).

</details>

## Install

```bash
# from GitHub
claude plugin marketplace add hwang-yeonsu/re-harmoniz
claude plugin install reharm@re-harmoniz

# or from a local clone
claude plugin marketplace add /path/to/re-harmoniz
claude plugin install reharm@re-harmoniz
```

**Enable per project (recommended).** Installing only makes the plugin *available*; **enablement decides where `/reharm:*` exists**, resolved per project root. Keep it off at user level and switch it on only in repos that actually hold research wikis — `<repo-root>/.claude/settings.json`:

```json
{ "enabledPlugins": { "reharm@re-harmoniz": true } }
```

Update later with `claude plugin update reharm@re-harmoniz`.

Requirements: Claude Code + Python 3 (stdlib only — frontier scorer and wiki linter). Web search uses native tools. *Optional:* `npm install -g defuddle` gives cleaner, token-leaner web-page extraction; `reharm` uses it when present and falls back to native WebFetch otherwise (`EVOLUTION.md` §6).

## A scope, inside

A **scope** is a self-contained folder — three things make it one:

```
Research_X/
├── .raw/            # immutable sources (papers, clips, dumps)
│   ├── experiments-results/ # field-origin — the scope's own experiment/real-world results
│   └── deep-research/       # reports returning from a deep-research escalation (§13)
├── wiki/
│   ├── claims/      # ★ the assertions your decisions rest on — the unit of evolution
│   ├── mashups/     # ★ synthesized cross-insights
│   ├── sources/     # one summary page per source (origin: primary|secondary + ancestry)
│   ├── questions/   # open questions — lifecycle: open → answered | escalated | archived
│   ├── experiments/ # ★ field-experiment pre-registrations (design records)
│   ├── deliverables/ # answer syntheses — non-evolving snapshots (reharm:ensemble)
│   ├── meta/evolution/  # session reports E0001.md…
│   └── index.md · hot.md · log.md · overview.md
└── CLAUDE.md        # scope config — incl. the Goal & Open Decisions block (templates/SCOPE_CLAUDE.md)
```

`sources/` = what a document says (testimony on record). `claims/` = the branches your decisions rest on. Only claims and mashups evolve — and only while a decision still needs them.

The `CLAUDE.md` decision block is the load-bearing part: it is what makes seeding selective, targeting decision-scoped, verification tiered, and pruning possible. A scope without it still works exactly as before — every relevance rule simply stays inert, and the linter tells you so.

## Fits the structure you already have

A scope is *just* `.raw/` + `wiki/` + `CLAUDE.md`, so it drops into any knowledge base — reharm doesn't care where the scope sits. One way to lay it out: research scopes nested inside a personal PARA / Obsidian vault, with project-bound research living under its project and general reference research under resources.

```
my-vault/                       # your knowledge-base root (e.g. an Obsidian vault)
├── 00_Inbox/
├── 01_Projects/                # time-bound work
│   └── Project_A/
│       └── Research_X/          # ← a reharm scope (research bound to this project)
│           ├── .raw/
│           ├── wiki/
│           └── CLAUDE.md
├── 02_Areas/
├── 03_Resources/               # durable reference
│   └── Research_Y/              # ← a reharm scope (general reference)
│       ├── .raw/
│       ├── wiki/
│       └── CLAUDE.md
└── 04_Archives/
```

That's only an example — use whatever structure you already have. (Since a scope is not a code workspace, point each one back to its real source-code path in the scope's `CLAUDE.md`.)

## Autonomous mode (opt-in)

Every skill above is **manual by design** — you pick the targets, you adjudicate (`EVOLUTION.md` "nothing is auto-decided"). When you want the loop to run *unattended*, the plugin ships a template that deliberately trades that away: [`templates/loop.md`](templates/loop.md). One thing it will **not** trade away: the loop never writes or settles a decision. With no open decision it stops cleanly (`no-decisions`) rather than picking its own target — a loop that invents its own goals optimizes whatever it happens to find. Copy it to your research project's `.claude/loop.md`, fill in the `CONFIG` block, and the native `/loop` command re-runs **one iteration per firing** — `reharm:pushing` picks the next move, then the recommended skill executes, with the main session standing in for your approvals.

The quickest path is the bundled wizard — **one command from zero to a running loop**:

```bash
/reharm:loop-setup       # detects the scope, checks it declares an open decision, interviews for CONFIG,
                         # validates the experiment gate, writes .claude/loop.md, then starts the
                         # native /loop — all in one invocation
```

No hand-copying needed — the wizard writes `.claude/loop.md` for you. Manual setup (copy the template, fill CONFIG yourself) remains a valid alternative. Either way the file is a point-in-time copy owned by your research project: plugin upgrades never touch it, so re-run the wizard afterwards to refresh it (your CONFIG is shown and kept, the ledger carries over, and your scope/wiki needs no migration). The loop then runs as:

```bash
# from the research project root — /loop with no prompt (bare or interval-only) reads .claude/loop.md
/loop                    # recommended — dynamic, self-paced: enforces MAX_ITERS, stops itself when idle or stagnant
/loop 2h                 # supported — fixed cadence; ends itself by deleting its own cron job (interval only, no prompt)
```

It is **opt-in and lives outside the plugin core** (a project-local file, not a skill) precisely because it overrides the no-auto-decide rule. Safeguards are built into the contract: a per-scope lock, a ledger kept *outside* the scope (`EVOLUTION.md` §8), a per-iteration target cap (`MAX_TARGETS`, default 2), reversible `deprecate` (never delete), and double logging (`E####.md` + a ledger line naming the `targets` touched) for audit. Real experiment execution stays gated — it runs only when `RUN_EXPERIMENTS=yes` **and** the scope's code-workspace path exists (§12), and the run itself is an isolated background runner sub-agent (the plugin's runner-worker by default, or your configured external runner) that reports into `.raw/experiments-results/`; otherwise the loop stops at design + handoff.

**Where it runs:** `/loop` is **local and session-scoped** — the Claude Code session must stay open and the machine awake for it to fire (a closed/sleeping laptop will not run it). The template runs in either mode: a bare `/loop` (**dynamic**, self-paced — recommended, because ending is fail-safe: the loop stops by simply not re-arming its own wakeup) or an interval-only `/loop 2h` (**fixed cadence** — the loop must actively delete its own cron job to end; a missed delete keeps firing no-op ticks until you CronDelete the job or the 7-day expiry). Never pass a prompt together with the interval — a prompt bypasses `.claude/loop.md`. Mid-run compaction is safe (state lives in the ledger; the next firing re-reads the file in full), while `/clear` kills the schedule. For a fixed wall-clock schedule (e.g. nightly) or a laptop-closed, unattended run, use cloud [Routines](https://code.claude.com/docs/en/routines.md) (`/schedule`), which execute on Anthropic-managed infrastructure — not `/loop`. The template header is the terse contract; the **[autonomous-loop guide](templates/loop.guide.md)** is the full long-form explanation (what it is, why, how it's verified, the execution model, and the exact commands).

## Language

Your notes, claims, and reports are written in **your language** (Korean fully supported — see `EVOLUTION.md` §9 for the search conventions that make it work). System docs (this README, `EVOLUTION.md`, the skills) are English.
