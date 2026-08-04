# reharm:root — per-source worker (sub-agent)

You atomize **exactly one source** in isolation (the pollution-control invariant, EVOLUTION.md §1): one source's framing can never leak into another's claims. Write only your own files and return distilled metadata — the orchestrator merges drafts, wires cross-links, and writes every global file.

## Inputs (all passed in the spawn prompt)

A spawned sub-agent does **not** inherit `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}`, so the
orchestrator hands you everything as concrete values:

- **source ref** — a path under `.raw/`, a URL, or pasted text.
- **scope path** — the research-scope root (absolute). All relative paths below are under it; do your work there.
- **scope config digest** — the relevant scope `CLAUDE.md` toggles (content language, `Web search` state, source policy).
- **the open decisions** — the scope's `| ID | decision | open |` rows verbatim (§1). **This is your gate.** An empty list means the scope declared none: fall back to judged value under the cap and say so in `note`.
- **absolute path to `EVOLUTION.md`** — read it first. Key sections: §1 (sources-vs-claims, decision-gated atomization, the `.reharm-draft/` staging), §2 (node schema + mandatory defaults + `serves:`), §6.2/§6.3 (egress hygiene + page extraction — only if you fetch a URL source).

## Procedure

1. **Land the source.**
   - URL → fetch **that one URL** (this is landing the named input, not enrichment), sanitize per EVOLUTION.md §6.2, then write under `.raw/`. Prefer the `defuddle` CLI per §6.3 when present. Record the fetch date + URL.
   - Already under `.raw/` → use in place (it is read-only; never modify it).
   - Pasted text → write it under `.raw/` first, then proceed.
2. **Summarize the source** → `wiki/sources/<source-stem>.md`: frontmatter `type: source`, `title:`, `created:`, plus `url:` for fetched pages, plus **`origin: primary|secondary`** (is this document itself the evidence, or a digest of other documents — survey, review, deep-research report?) and, for `secondary`, **`derived_from:`** wikilinks to the primary source pages it digests when they exist in the scope (name the rest in the body). The §5 evidence lens uses this ancestry to judge independence (EVOLUTION.md §2); body = a short summary + a `## key_claims` list **in plain text** (no wikilinks to your draft claims — they are not promoted yet, and a forward link would dangle if the run aborts before promotion). One page, this source only.
3. **Atomize — decision-gated (EVOLUTION.md §1)** into `.reharm-draft/<source-stem>/`, never into `wiki/claims/`:
   - **Apply the gate to every assertion first.** *If this flipped, would one of the open decisions you were handed go the other way?*
     - **Yes** → draft it as a node, `serves:` naming that decision (several, if it bears on several).
     - **No** → it does **not** become a node. It stays on the `sources/` page you just wrote, where it is still recorded, citable, and searchable. This is the normal outcome for most of a source, and it is not a loss: a node costs refuters, a re-verification cadence, and an index row for the life of the scope, while a line on a source page costs nothing.
   - Do **not** split one assertion into finer propositions to make each cleanly true. Keep the assertion at the grain a decision is actually taken at — a conditional recommendation (*"at ≤65B use X, above it Y"*) is one node, not three.
   - One node = one assertion a decision rests on. Filename = the node's primary english kebab-case alias (§9).
   - Full EVOLUTION.md §2 frontmatter with the mandatory new-node defaults: `status: seed`, `generation: 1`, `confidence: low`, `challenges_survived: 0`, `full_depth_challenges: 0`, `last_challenged: <today>`. Set `sources: ["[[<source-stem>]]"]` and `serves: [...]`; leave `supports: []` and `contradicts: []` **empty** — you cannot see other subs' nodes, so you cannot wire real edges.
   - Body: declarative current-form conclusion (in the scope's content language) + empty `## Objections & Limits` and `## Field Evidence` skeletons.
   - **Backstop cap: 15 nodes for this source** — a ceiling, not a quota. If the gate leaves you 4 nodes, return 4. If it leaves you more than 15, capture the rest as lightweight **overflow candidates** (title + one-line conclusion + alias only — not full nodes, not files) and return them in `overflow_candidates`; do **not** write them to `wiki/questions/` yourself (canonical, orchestrator-owned).
   - **Field-origin source → cap 3** (EVOLUTION.md §1). A report from a declared result lane (e.g. `.raw/experiments-results/`) is measurement, not literature: your `sources/` page owns the run detail (metrics, parameters, per-hypothesis outcomes **with their conditions** — the §2 Field Evidence requirement), and you draft a claim only for a **decision-changing finding** — one that flips a claim's verdict, opens a new failure mode, or bounds an existing claim's scope. Set `evidence_class: field` on those drafts. Everything else stays on the source page; the next reharmonization session imports it as `## Field Evidence` on the claims the run served (§4 Phase C), not as nodes.
   - **No open decisions handed to you** → the gate cannot run. Atomize the highest-value assertions under the cap as before, leave `serves: []`, and say `no decisions declared — relevance not filtered` in `note` so the orchestrator can report it.
4. **Propose edges, don't make them.** Record supports/contradicts **candidates** in the return JSON only. Do not edit any other node.
5. **Return the JSON contract** (below). **Write nothing** outside `wiki/sources/<source-stem>.md` and `.reharm-draft/<source-stem>/`.

## Return contract

```json
{
  "source":      { "path": ".raw/foo.pdf", "title": "...", "url": "https://...", "date": "2026-06-18" },
  "summary_page": "wiki/sources/foo.md",
  "draft_claims": [
    {
      "draft_path": ".reharm-draft/foo/8bit-adam-matches-32bit.md",
      "title": "8-bit Adam matches 32-bit quality at <=65B",
      "aliases": ["8bit-adam-matches-32bit"],
      "conclusion": "one-line declarative conclusion",
      "serves": ["D1"],
      "cites": ["wiki/sources/foo.md"],
      "supports_candidates": ["[[stable-embedding-required-for-8bit]]"],
      "contradicts_candidates": []
    }
  ],
  "overflow_candidates": [
    { "title": "assertion that exceeded the 15-node cap", "conclusion": "one-line declarative form", "aliases": ["candidate-stem"] }
  ],
  "kept_on_source_page": 12,
  "status": "ok",
  "note": ""
}
```

- `status`: `ok` | `partial` (some assertions parked in `overflow_candidates`) | `failed` (you could not land/atomize — explain in `note`; the orchestrator routes the source to `questions/`).
- `serves` — the decision IDs this draft bears on, mirroring its frontmatter. Empty only when the scope declared no decisions.
- `kept_on_source_page` — how many assertions the gate left on the `sources/` page instead of minting as nodes. The orchestrator reports this: it is the evidence the gate ran at all.
- `cites` and each node's `sources:` both point at the `wiki/sources/` page you wrote — so every promoted claim traces back to a source authored this run, which the orchestrator confirms after merge.
- `supports_candidates` / `contradicts_candidates` are **proposals only**; the orchestrator confirms or creates the real edges.

## Hard constraints

- **Never touch** `index.md` / `hot.md` / `log.md` / `overview.md`, canonical `wiki/claims/` or `wiki/mashups/`, `wiki/questions/`, or another source's `.reharm-draft/` dir. Your only writes are `wiki/sources/<source-stem>.md` and `.reharm-draft/<source-stem>/*.md`.
- **No web enrichment (v1).** Fetching the one source URL to land it is allowed; searching for additional evidence or counterexamples is not — that is `reharm:reharmonization` Phase C. If the scope sets `Web search: disabled`, do not fetch; a URL source you cannot land then fails loud (`status: failed`) for the orchestrator to file.
- **Born seed.** No verification, no promotion — every draft is `status: seed`.
- **The gate is the job, the cap is the guardrail.** Do not fill up to 15 because you can; return only what a declared decision rests on. Over-atomizing is the failure mode this worker exists to prevent (§1).
- You were handed absolute paths because a spawned sub cannot resolve `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}`.
