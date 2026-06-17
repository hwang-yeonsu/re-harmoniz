---
description: "re:Harmoniz — scaffold a research scope and/or seed it (repo URL, article, pseudocode, note, or rough idea → .raw/ → atomic claim nodes)."
---

# reharm:root — Scaffold & Atomic Seeding

Namespaced slash entry point. Dispatches to the bundled `root` skill so that `/reharm:root` stays available alongside the auto-triggered skill, without loading the full skill description into every session.

## Dispatch

1. Read the full skill instructions from the active plugin install: `${CLAUDE_PLUGIN_ROOT}/skills/root/SKILL.md`.
2. Follow that SKILL.md exactly. Wherever it references `${CLAUDE_SKILL_DIR}`, treat it as `${CLAUDE_PLUGIN_ROOT}/skills/root` (so the protocol is at `${CLAUDE_PLUGIN_ROOT}/EVOLUTION.md`).
3. Treat the user's arguments as:

```text
$ARGUMENTS
```

If `${CLAUDE_PLUGIN_ROOT}` is unset or the file is not directly readable, locate the re:Harmoniz plugin root (the directory containing `EVOLUTION.md` and `skills/`) under the installed plugins directory, then continue.
