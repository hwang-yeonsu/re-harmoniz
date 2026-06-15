# re:Harmoniz

**English** · [한국어](README.ko.md)

> **An evolution loop for research wikis** — a Claude Code plugin (`reharm`).

**re:Harmoniz = re·search + re·harmoniz·ation.** Like a musician reharmonizes a melody — keeping the tune, re-deriving the chords beneath it — re:Harmoniz keeps your research *question* fixed and re-derives the **claims and evidence underneath it**, generation after generation.

Knowledge lives as atomic **claim** nodes that harden under two pressures: **mutation** (revision) and **natural selection** (adversarial verification). A 1st-generation claim is a bare assertion; a 10th-generation claim has absorbed its refutations, cites independent sources, and carries real-world field evidence. Only nodes that *survive* refutation gain a generation — so the wiki's average reliability rises monotonically.

It's all plain Markdown you own. The entire protocol is one file: [`EVOLUTION.md`](EVOLUTION.md).

## The loop

```
  seed a claim
      │
      ▼
  mutate            ── revise, decompose new sources, hunt counter-evidence
      │
      ▼
  natural selection ── 3 refuters, one lens each (coherence · evidence · reproducibility)
      │
      ├─ survives ≥2/3 ─▶ generation +1, promote: seed → developing → hardened → evergreen
      └─ collapses     ─▶ deprecated (kept on record — never deleted)
```

Run it whenever new material or new doubt piles up. Nothing is auto-decided: you pick the targets, you adjudicate the ambiguous ones.

## Skills

| Skill | What it does |
|---|---|
| `reharm:root` | Entry point. Scaffolds a scope, then seeds it: throw in a repo URL, article, pseudocode, an existing note, or a rough idea → it lands in `.raw/` and becomes atomic `claims/` (all born generation 1). |
| `reharm:reharmonization` | One evolution session — the namesake skill: Retrospect → Target (you approve) → Mutate → Natural Selection (3 refuters, ≥2/3 must survive) → Record. |
| `reharm:modal-interchange` | Cross-scope mashup — borrow knowledge from a parallel scope (like borrowing chords from a parallel mode) and mint cross-domain insights, citation-only. |
| `reharm:critique` | Adjudication — gathers the ambiguous backlog (open questions, stalled nodes, contradictions, lint warnings) and resolves it through a short interview. |

## Usage scenarios

**Tracking a fast-moving technique.** You're evaluating whether a new ML optimization actually holds up at scale. `reharm:root` a couple of papers and the reference repo; each finding becomes a claim. Weeks later a new result contradicts one — run `reharm:reharmonization`: the refuters test both, the loser is deprecated *with its reasons on record*, the survivor gains a generation and now cites two independent sources.

**A literature review that defends itself.** Atomize every paper into claims with citations. Contradictions across papers stay explicit on *both* nodes until you settle them in `reharm:critique`. The `index.md` maturity census shows at a glance what's solid (hardened/evergreen) versus still speculative (seed).

**Competitive / market analysis.** Seed vendor docs, benchmarks, and field reports. Adversarial verification strips marketing claims that have no independent backing; only assertions that survive the evidence lens harden. Real usage that later confirms or breaks a claim gets appended under `## Field Evidence`.

**Connecting two research tracks.** Once you have two scopes — say one on *training* and one on *serving* — `reharm:modal-interchange` finds where one side's open problem is answered by the other side's mechanism, and mints a cross-domain insight, cited back to both originals (single source of truth).

<details>
<summary><b>A full walkthrough — one topic across all four skills</b></summary>

The scope is `Research_optimizers` (training-time optimization for your ML pipeline); a parallel scope, `Research_serving`, already exists for inference. **The question:** *can 8-bit Adam (bitsandbytes) replace 32-bit Adam without hurting final model quality?*

**① Seed it — `reharm:root`**

```bash
cd 01_Projects/Project_A/Research_optimizers
/reharm:root https://github.com/bitsandbytes-foundation/bitsandbytes
/reharm:root "paper: 8-bit Optimizers via Block-wise Quantization (Dettmers et al., 2022)"
```

The repo dump and paper land in `.raw/`, each gets a `sources/` summary, and the assertion becomes a claim — `claims/8bit-adam-matches-32bit-quality.md`, born `seed · generation 1 · confidence low`.

**② First evolution — `reharm:reharmonization` (writes `E0001.md`)**

Phase B surfaces the fresh node (high boundary score); you approve it. Phase C hunts counter-evidence on the web. Phase D runs three refuters — *coherence · evidence · reproducibility*; the reproducibility lens lands a counterexample (*training diverges without a stable-embedding layer*), but **2/3 survive**.

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

You finally run 8-bit Adam in your actual pipeline; at your scale (≤65B) it matches 32-bit within noise. The experiment report enters via `reharm:root`, and its conclusion is appended under the claim's `## Field Evidence` with a wikilink back. Next session that single field-evidence entry is the only gate left: `hardened → evergreen`.

**What you read between sessions:** `hot.md` (what just changed), `index.md` (the maturity census — how many nodes sit at each status), and `meta/evolution/E####.md` (why each change happened).

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
├── .raw/            # immutable sources (papers, clips, dumps, experiment reports)
├── wiki/
│   ├── claims/      # ★ atomic assertions — the unit of evolution
│   ├── mashups/     # ★ synthesized cross-insights
│   ├── sources/     # one summary page per source
│   ├── questions/   # open questions
│   ├── meta/evolution/  # session reports E0001.md…
│   └── index.md · hot.md · log.md · overview.md
└── CLAUDE.md        # scope config (templates/SCOPE_CLAUDE.md)
```

`sources/` = what a document says (testimony on record). `claims/` = what you currently believe is true (the contested issue). Only claims and mashups evolve.

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

## Language

Your notes, claims, and reports are written in **your language** (Korean fully supported — see `EVOLUTION.md` §9 for the search conventions that make it work). System docs (this README, `EVOLUTION.md`, the skills) are English.
