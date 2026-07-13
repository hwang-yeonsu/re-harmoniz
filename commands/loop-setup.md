---
description: "re:Harmoniz autonomous-loop wizard — detects the scope, interviews for CONFIG, validates the experiment gate, writes .claude/loop.md, then starts the native /loop in the same invocation."
---

# reharm:loop-setup — Autonomous-Loop Wizard (setup → start, one command)

Namespaced slash entry point. Dispatches to the bundled `loop-setup` skill so that
`/reharm:loop-setup` stays available alongside the auto-triggered skill, without loading the full
skill description into every session.

## Dispatch

1. Read the full skill instructions from the active plugin install: `${CLAUDE_PLUGIN_ROOT}/skills/loop-setup/SKILL.md`.
2. Follow that SKILL.md exactly. Wherever it references `${CLAUDE_SKILL_DIR}`, treat it as `${CLAUDE_PLUGIN_ROOT}/skills/loop-setup` (so the template is at `${CLAUDE_PLUGIN_ROOT}/templates/loop.md`).
3. Treat the user's arguments (optional: a scope path, or "dynamic"/"interval <cadence>") as:

```text
$ARGUMENTS
```

If `${CLAUDE_PLUGIN_ROOT}` is unset or the file is not directly readable, locate the re:Harmoniz plugin root (the directory containing `EVOLUTION.md` and `skills/`) under the installed plugins directory, then continue.
