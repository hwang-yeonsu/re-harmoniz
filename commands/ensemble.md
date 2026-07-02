---
description: "re:Harmoniz answer synthesis — assembles the scope's hardened claims into one citable deliverable answering the central question, confidence set by the weakest load-bearing link. Writes only wiki/deliverables/ + close-out files; node states never change."
---

# reharm:ensemble — Answer Synthesis (deliverable)

Namespaced slash entry point. Dispatches to the bundled `ensemble` skill so that `/reharm:ensemble` stays available alongside the auto-triggered skill, without loading the full skill description into every session.

## Dispatch

1. Read the full skill instructions from the active plugin install: `${CLAUDE_PLUGIN_ROOT}/skills/ensemble/SKILL.md`.
2. Follow that SKILL.md exactly. Wherever it references `${CLAUDE_SKILL_DIR}`, treat it as `${CLAUDE_PLUGIN_ROOT}/skills/ensemble` (so the protocol is at `${CLAUDE_PLUGIN_ROOT}/EVOLUTION.md`).
3. Treat the user's arguments (the scope path and/or the question, if given) as:

```text
$ARGUMENTS
```

If `${CLAUDE_PLUGIN_ROOT}` is unset or the file is not directly readable, locate the re:Harmoniz plugin root (the directory containing `EVOLUTION.md` and `skills/`) under the installed plugins directory, then continue.
