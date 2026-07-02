---
name: experiment-design
description: "re:Harmoniz field-experiment designer — for a claim stuck at the hardened→evergreen gate, design (pre-register) the experiment that would confirm or refute it: hypothesis, confirm/refute criterion, conditions, and a runner goal — then hand off to an external runner. Designs and records only; never runs code. Triggers: reharm experiment, design an experiment, 실험 설계, 실험 사전등록, pre-register experiment, what experiment proves this"
---

# reharm:experiment-design — Field-Experiment Designer (pre-registration)

The bridge from a *claim* to a *field experiment*. For a claim stuck at the `hardened → evergreen` gate — the one promotion the wiki cannot grant itself (it needs real-world evidence) — this skill **designs** the experiment and **pre-registers** its confirm/refute criterion, then hands the goal to an external runner. It is invoked **by the user after they decide an experiment is warranted** (`reharm:pushing` only recommends it).

**Read `${CLAUDE_SKILL_DIR}/../../EVOLUTION.md` (the protocol, at the plugin root) and follow it.** Key sections: §2 (the `experiment` node schema), §3 (the evergreen gate this serves), §4 Phase C (how the result is imported and judged), §5 (the reproducibility lens, applied prospectively here), §12 (the three-layer bridge — DESIGN / OPERATIONALIZE / EXECUTE).

You are the **DESIGN layer only** (§12). You write a pre-registration record and stop at a handoff command. You never run the experiment, never call the runner, and never author code-level metric/verify commands — that is the runner's planner (OPERATIONALIZE), which dry-runs in the code workspace you cannot see from here.

## Procedure

1. **Resolve the scope** (`.raw/` + `wiki/` present); read the scope `CLAUDE.md` (the §10 code-workspace path and any `runner:`/experiment-bridge toggle).
2. **Resolve the target claim.** Take it from the arguments, else ask once. If none is given and a `hardened` claim with empty `## Field Evidence` exists, offer those as candidates (the §3 evergreen-gate backlog) — but the user picks; never auto-select (§4 Phase B spirit).
3. **Testability gate (§12).** Read the claim body + `## Objections & Limits`. Decide with the user whether the claim is **empirically testable** (a runnable result could confirm/refute it). If it is *definitional / analytical / historical* — no runnable result — **stop and redirect**: its evidence path is independent-source corroboration (§3 developing→hardened) and the §5 refuters, i.e. `reharm:reharmonization`, not an experiment. Do not force a metric onto a non-empirical claim.
4. **Design the pre-registration.** With the user, fix — *before any run*:
   - **Hypothesis** — the claim restated as the proposition under test.
   - **Confirm / Refute** — the §5 reproducibility lens, written ahead of the evidence: the observable/numeric criterion that would confirm, and the failure/counterexample that would refute. These are frozen now so the result cannot be rationalized post-hoc (§4 Phase C).
   - **Conditions to record** — dataset / scale / hardware / hyperparameters the result must hold under and report (§2 Field Evidence requirement). Pull the claim's existing bounds (e.g. a `≤65B` scope qualifier, an absorbed objection) and confirm the rest with the user; you cannot read the code workspace, so flag any condition only the runner can fix.
   - **For the runner** — a plain-language `goal`, the experiment `shape` (confirmatory | exploratory | debug → lets the runner's planner pick its mode), and `result_sink: .raw/experiments-results/`. Author **no** metric or verify command here (§12).
5. **Write the node** `wiki/experiments/<slug>.md` per the §2 experiment schema (`type: experiment`, `status: planned`, `claim: "[[target]]"` — a **list** when one run genuinely serves several claims/questions (§2), `created`, optional `runner:`). Body = the four sections above plus a `## Handoff` block holding the exact next command the user runs **in the code workspace**.
6. **Connect.** Wikilink the experiment to its claim; if the claim already has a `planned`/`running` experiment node, **update it, don't duplicate** (one live experiment per claim).
7. **Close out**: update `index.md` (census; experiment nodes are listed but not part of the maturity census counts), overwrite `hot.md`, prepend a `log.md` entry (`## [date] experiment | <claim> pre-registered`).
8. **Lint**: from the scope root run `python3 "${CLAUDE_SKILL_DIR}/../../scripts/wiki-lint.py" --json`; expect `clean: true` (the new node must carry the §2 experiment keys and a resolvable `claim:` link).
9. **Hand off and stop.** Print the `## Handoff` command and the return path (`.raw/experiments-results/` → `reharm:root` → `reharm:reharmonization` Phase C). Then stop — the user crosses into the code workspace and runs the runner (§12). This skill runs nothing.

## Constraints

- **DESIGN only (§12).** Write the pre-registration node and stop at the handoff. Never execute the experiment, never invoke the runner, never `cd` into or modify the code workspace, never touch git.
- **No code-level spec.** Metric and verify commands are the runner planner's job (OPERATIONALIZE) — it must dry-run them in the code workspace, which this skill cannot see. Authoring them here would be unvalidated guessing.
- **Pre-registration is binding.** The confirm/refute criterion is fixed before the run; Phase C judges the result against it, not a criterion chosen afterward (§4 Phase C, §5.5).
- **Never raises `generation` or maturity.** This skill only creates/maintains a `type: experiment` record. Generations are earned by surviving Phase D; the evergreen promotion happens in `reharm:reharmonization` when the result imports.
- **One scope, one live experiment per claim.** Update an existing `planned`/`running` node rather than spawning a duplicate.
- **Empirical claims only.** Non-empirical claims are redirected to `reharm:reharmonization` (§12 testability gate).
