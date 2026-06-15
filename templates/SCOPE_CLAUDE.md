# Research_<TOPIC> — Research Scope

## 1. Purpose & Boundaries

<One paragraph: what this scope researches, and what is explicitly out of scope.>

## 2. Metadata (the scope is not a code workspace)

- **Code workspace path(s): `<absolute path — fill in>`**
- Experiment lane: experiment reports produced in the workspace land in this scope's `.raw/` and re-enter through `reharm:root` (their conclusions feed `## Field Evidence`).

## 3. Protocol

- This scope follows the **re:Harmoniz protocol** (`reharm` plugin, `EVOLUTION.md`): node schema, maturity state machine, 5-phase evolution sessions, report templates.
- `.raw/` is immutable. Frequent revision of wiki nodes is encouraged.

## 4. Adversarial Verification (applies to any research loop running in this scope)

- Every claim carries explicit confidence: high (multiple independent sources agree) / medium (single good source) / low (speculation, unverified).
- Mutations and new assertions pass only if **≥2 of 3 refuters** (coherence / evidence / reproducibility lenses) fail to refute them. When uncertain, refute.
- Valid objections are never discarded — absorb them into the node's `## Objections & Limits`.

## 5. Seed Source Candidates (input queue for reharm:root)

| Priority | Source | Notes |
|---|---|---|
| 1 | <note / URL / file> | |

## 6. Toggles & Status

- Web search: enabled <!-- or: disabled -->
- Source policy: prefer peer-reviewed / official docs / primary sources; do not cite social media, forums, or undated pages as high-confidence <!-- edit per domain; scopes the §6 evidence lens -->
- <YYYY-MM-DD>: scope created. Nodes: 0.
