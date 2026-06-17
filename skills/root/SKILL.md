---
name: root
description: "re:Harmoniz entry point — scaffold a research scope and/or seed it: throw in a repo URL, article, pseudocode, existing note, or rough idea and it lands in .raw/ and becomes atomic claim nodes. Triggers: reharm root, root this, 시드 투입, 스코프 만들어, seed the scope, plant, ingest into research scope"
---

# reharm:root — Scaffold & Atomic Seeding

Turns any input (a source or a rough topic) into atomic knowledge nodes inside a research scope. **Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) first and follow it.** Key sections: §1 (anatomy, sources-vs-claims), §2 (node schema), §6 (web search policy), §11.2 (index template).

## Procedure

1. **Resolve the scope.** If the current directory is not a research scope (`.raw/` + `wiki/` present), either take the target path from the arguments or ask once.
   - **If the scope does not exist yet, scaffold it**: create the §1 tree, copy `${CLAUDE_SKILL_DIR}/../../templates/SCOPE_CLAUDE.md` → `CLAUDE.md` and fill what is known (purpose, seed candidates), create initial `index.md` (§11.2) / `hot.md` / `log.md` / `overview.md`. Then continue seeding if input was given.
2. **Read scope `CLAUDE.md`** (verification rules, toggles, seed queue).
3. **Land the source.**
   - External material (URL, pasted text, file): store under `.raw/` — immutable from then on. Fetched web pages get date + URL recorded.
   - Material already sitting in `.raw/`: process in place.
   - Existing notes elsewhere in the repo: do **not** copy — reference by wikilink only (single source of truth).
4. **Source summary**: one page per source in `wiki/sources/` with a `key_claims` list.
5. **Atomize** into `wiki/claims/`:
   - One node = one verifiable assertion. Title in the user's language; english kebab-case `aliases:`.
   - Frontmatter per EVOLUTION.md §2 with **mandatory new-node defaults** (`status: seed`, `generation: 1`, `confidence: low`).
   - Body: declarative current-form conclusion + empty `## Objections & Limits` and `## Field Evidence` skeletons.
   - If an equivalent node exists, update it instead of duplicating.
6. **Connect**: supports/contradicts wikilinks; conflicts get `> [!contradiction]` callouts on both nodes.
7. **Close out**: update `index.md` (§11.2 maturity census), overwrite `hot.md`, prepend `log.md` entry (`## [date] root | title`).

## Constraints

- No verification, no promotion here — that is `reharm:reharmonization` Phase D. Every seed is born `seed`.
- Web enrichment is allowed within EVOLUTION.md §6 bounds; skip entirely if the scope sets `Web search: disabled`.
- Max 15 new nodes per source — overflow goes to `wiki/questions/` as candidates. Process sources one at a time.
