---
description: "re:Harmoniz field-experiment designer — pre-registers (designs) the experiment that would confirm or refute a claim stuck at the evergreen gate, then hands off to a runner (external, or the plugin's default runner-worker). Designs and records only; never runs code."
---

# reharm:experiment-design — Field-Experiment Designer (pre-registration)

Namespaced slash entry point. Dispatches to the bundled `experiment-design` skill so that `/reharm:experiment-design` stays available alongside the auto-triggered skill, without loading the full skill description into every session.

## Dispatch

1. Read the full skill instructions from the active plugin install: `${CLAUDE_PLUGIN_ROOT}/skills/experiment-design/SKILL.md`.
2. Follow that SKILL.md exactly. Wherever it references `${CLAUDE_SKILL_DIR}`, treat it as `${CLAUDE_PLUGIN_ROOT}/skills/experiment-design` (so the protocol is at `${CLAUDE_PLUGIN_ROOT}/EVOLUTION.md`).
3. Treat the user's arguments (the target claim, if given) as:

```text
$ARGUMENTS
```

If `${CLAUDE_PLUGIN_ROOT}` is unset or the file is not directly readable, locate the re:Harmoniz plugin root (the directory containing `EVOLUTION.md` and `skills/`) under the installed plugins directory, then continue.
