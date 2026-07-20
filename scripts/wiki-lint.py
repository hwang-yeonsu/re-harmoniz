#!/usr/bin/env python3
# re:Harmoniz Phase E health check (EVOLUTION.md §4 Phase E.3). 스코프 디렉토리에서
# 실행 — ./wiki(링크 해석에 ./.raw 포함)만 읽는 read-only, stdout 전용 (보고서 파일은
# 호출자가 wiki/meta/lint/에 저장).
"""wiki-lint.py — scope health check for the re:Harmoniz protocol.

Checks (EVOLUTION.md §4 Phase E.3):
  1. missing/invalid frontmatter — evolving nodes (claims/, mashups/) must
     carry the §2 scalar keys; sources/ and questions/ need type + title.
     Enum keys (type/status/confidence), date keys, and integer keys are
     validated when present.
  2. dead wikilinks — path-qualified targets that resolve nowhere inside the
     scope. Bare targets matching nothing are reported separately as
     `unresolved_external`: they may be legitimate cross-scope citations
     (e.g. modal-interchange SSoT links), so they do not break `clean` —
     review them manually. Stems declared in the scope CLAUDE.md
     `Allowed external wikilinks:` toggle move to `allowed_external`
     (acknowledged, zero-noise).
  3. orphans — claims/mashups (excluding deprecated) with zero inbound
     wikilinks from other node pages. Links from index/hot/log/overview or
     meta pages do not rescue a node; frontmatter wikilinks (supports: …) do.
  4. unresolved contradictions — `> [!contradiction]` callouts in bodies or
     non-empty `contradicts:` frontmatter.
  5. duplicate stems — two wiki/ files sharing a filename stem. Wikilinks
     resolve by stem (§9), so a collision makes one file unreachable.
  6. status census — `status_census` (top-level) aggregates claims/ +
     mashups/ frontmatter status; the index.md `**Census:**` line is display
     only, so a disagreement is reported as a `census_drift` warning.
  7. session eval — the LATEST `E####.eval.json` (§7 schema v2) must carry a
     boolean `pass` and a `stagnation.verdict` enum; a missing/broken/invalid
     file is reported as `eval_findings` warnings.
  8. schema extensions (§2) — question pages use the question lifecycle
     (open|answered|escalated|archived; maturity values tolerated as
     `legacy_question_status` warnings), experiment `claim:` may be a string
     or a list, sources may carry `origin: primary|secondary` +
     `derived_from:`, claims/mashups may carry
     `evidence_class: literature|field|design` (absent = literature, §3),
     and mashup `borrowed:` snapshots must carry
     node/scope/status_at_mint/gen_at_mint/date.

`clean` = the five checks all count zero (`unresolved_external`,
`allowed_external`, `legacy_question_status`, `census_drift`, and
`eval_findings` are warnings and excluded).

Usage:
  wiki-lint.py            # human-readable text
  wiki-lint.py --json     # machine-readable (feeds E####.eval.json checks)

Exit codes:
  0  lint ran (clean or with findings — see `clean`)
  2  usage error (no ./wiki under the current directory)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCOPE_ROOT = Path.cwd()
WIKI_DIR = SCOPE_ROOT / "wiki"
RAW_DIR = SCOPE_ROOT / ".raw"

NODE_DIRS = ("claims", "mashups", "sources", "questions", "experiments", "deliverables")
EVOLVING_DIRS = ("claims", "mashups")
REQUIRED_NODE_KEYS = (
    "type",
    "title",
    "created",
    "updated",
    "status",
    "confidence",
    "generation",
    "last_challenged",
    "challenges_survived",
)
REQUIRED_PAGE_KEYS = ("type", "title")
# Experiment pre-registrations (§2, §12) are design records: page-level keys plus
# the link to the claim they serve and their own lifecycle status — and explicitly
# NONE of the evolution mechanics (generation/confidence/last_challenged/
# challenges_survived), which is why they are not in EVOLVING_DIRS.
REQUIRED_EXPERIMENT_KEYS = ("type", "title", "created", "status", "claim")
# Deliverables (§14) are non-evolving answer syntheses: page keys plus the
# question that is their identity, `updated` because they are re-derived in
# place — and none of the evolution mechanics (they are never graded).
REQUIRED_DELIVERABLE_KEYS = ("type", "title", "created", "updated", "question")
VALID_ENUMS = {
    "type": {
        "claim",
        "mashup",
        "source",
        "question",
        "meta",
        "experiment",
        "deliverable",
    },
    "status": {"seed", "developing", "hardened", "evergreen", "deprecated"},
    "confidence": {"high", "medium", "low"},
    "origin": {"primary", "secondary"},
    # §2/§3 class-calibrated gates (0.14.0). Optional — absence = literature
    # (legacy nodes stay valid, no migration); validated only when present.
    "evidence_class": {"literature", "field", "design"},
}
# `status` is type-dependent: experiment nodes use their own lifecycle, never the
# maturity ladder (§3), and questions use their own lifecycle with the maturity
# values tolerated as legacy (§2 — reported via `legacy_question_status`).
# check_frontmatter swaps the right set in per type.
EXPERIMENT_STATUSES = {"planned", "running", "imported", "abandoned"}
QUESTION_STATUSES = {"open", "answered", "escalated", "archived"}
# `borrowed:` snapshot subkeys minted by modal-interchange (§2) — the drift
# baseline reharmonization Phase A compares against.
BORROWED_KEYS = ("node", "scope", "status_at_mint", "gen_at_mint", "date")
DATE_KEYS = ("created", "updated", "last_challenged")
INT_KEYS = ("generation", "challenges_survived")
# §3 maturity ladder, in census display order (claims + mashups only).
MATURITY_STATUSES = ("seed", "developing", "hardened", "evergreen", "deprecated")
# §7 stagnation verdict enum (eval schema v2).
STAGNATION_VERDICTS = {"continue", "reseed", "change-strategy"}

MAX_BODY_BYTES = 256 * 1024
EXIT_OK = 0
EXIT_USAGE = 2

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
FM_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
CONTRADICTION_CALLOUT_RE = re.compile(
    r"^\s*>\s*\[!contradiction\]", re.MULTILINE | re.IGNORECASE
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
CENSUS_LINE_RE = re.compile(r"^\s*\*\*Census:\*\*(.*)$", re.MULTILINE)
CENSUS_TOTAL_RE = re.compile(r"(\d+)\s*nodes?")
CENSUS_PAIR_RE = re.compile(
    r"\b(seed|developing|hardened|evergreen|deprecated)\s+(\d+)"
)
SESSION_REPORT_RE = re.compile(r"^(E\d+)\.md$")
SESSION_EVAL_RE = re.compile(r"^(E\d+)\.eval\.json$")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _unquote(s: str) -> str:
    return s.strip().strip('"').strip("'")


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, body). frontmatter is None when no block exists.

    Values are strings; block-style lists (`key:` followed by `- item` lines)
    become Python lists. A list item of the form `- key: val` opens a one-level
    mapping whose following deeper-indented `key: val` lines join it (the
    `borrowed:` snapshot shape). No YAML library — stdlib only, same spirit as
    boundary-score.py.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm_raw, body = m.group(1), text[m.end() :]
    fm: dict = {}
    lines = fm_raw.splitlines()
    for i, line in enumerate(lines):
        km = FM_KEY_RE.match(line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val == "":
            items: list = []
            item_indent = -1
            for nxt in lines[i + 1 :]:
                if nxt.strip() == "":
                    continue
                dm = re.match(r"^(\s*)-\s+(.*)$", nxt)
                if dm:
                    item_indent = len(dm.group(1))
                    content = dm.group(2).strip()
                    cm = FM_KEY_RE.match(content)
                    if cm and cm.group(2).strip():
                        items.append({cm.group(1): _unquote(cm.group(2))})
                    else:
                        items.append(_unquote(content))
                    continue
                nm = re.match(r"^(\s+)([A-Za-z_][\w-]*):\s*(.*)$", nxt)
                if (
                    nm
                    and items
                    and isinstance(items[-1], dict)
                    and len(nm.group(1)) > item_indent
                ):
                    items[-1][nm.group(2)] = _unquote(nm.group(3))
                    continue
                break
            fm[key] = items
        else:
            fm[key] = _unquote(val)
    return fm, body


def list_is_nonempty(val) -> bool:
    """True when a list-typed frontmatter value carries content."""
    if val is None:
        return False
    if isinstance(val, list):
        return len(val) > 0
    s = str(val).strip()
    if s in ("", "[]"):
        return False
    if s.startswith("[") and s.endswith("]"):
        return s[1:-1].strip() != ""
    return True


def extract_wikilinks(text: str) -> set[str]:
    """Unique raw link targets, skipping fenced code blocks (frontmatter
    wikilinks like `supports: ["[[x]]"]` are intentionally included)."""
    cleaned: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        fm = FENCE_RE.match(line)
        if fm:
            char, length = fm.group(2)[0], len(fm.group(2))
            if fence_char is None:
                fence_char, fence_len = char, length
                continue
            if char == fence_char and length >= fence_len:
                fence_char, fence_len = None, 0
                continue
        if fence_char is not None:
            continue
        cleaned.append(line)
    return {
        m.group(1).strip()
        for m in WIKILINK_RE.finditer("\n".join(cleaned))
        if m.group(1).strip()
    }


def read_page(md: Path) -> dict | None:
    if md.is_symlink():
        return None
    try:
        text = md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if len(text.encode("utf-8")) > MAX_BODY_BYTES:
        return None
    fm, body = parse_frontmatter(text)
    return {
        "path": md.relative_to(SCOPE_ROOT).as_posix(),
        "stem": md.stem,
        "fm": fm,
        "body": body,
        "links": extract_wikilinks(text),
    }


def collect_node_pages() -> list[dict]:
    pages: list[dict] = []
    for kind in NODE_DIRS:
        d = WIKI_DIR / kind
        if not d.is_dir():
            continue
        for md in sorted(d.rglob("*.md")):
            page = read_page(md)
            if page:
                page["kind"] = kind
                pages.append(page)
    return pages


def collect_aux_pages() -> list[dict]:
    """index/hot/overview — their dead links matter; log.md and meta/ rot
    naturally (append-only history) and are skipped."""
    pages = []
    for name in ("index.md", "hot.md", "overview.md"):
        md = WIKI_DIR / name
        if md.is_file():
            page = read_page(md)
            if page:
                pages.append(page)
    return pages


def validate_borrowed(borrowed) -> list[str]:
    """Issues with a `borrowed:` snapshot (§2). Each entry must be a mapping
    carrying node/scope/status_at_mint/gen_at_mint/date with typed values."""
    if isinstance(borrowed, str):
        if borrowed.strip() in ("", "[]"):
            return []
        return ["not a list of `- node:` mapping entries"]
    if not isinstance(borrowed, list):
        return ["not a list of `- node:` mapping entries"]
    issues: list[str] = []
    for idx, entry in enumerate(borrowed):
        if not isinstance(entry, dict):
            issues.append(
                f"entry {idx}: not a mapping — expected subkeys "
                + "/".join(BORROWED_KEYS)
            )
            continue
        missing = sorted(k for k in BORROWED_KEYS if k not in entry)
        if missing:
            issues.append(f"entry {idx}: missing {'/'.join(missing)}")
        status = entry.get("status_at_mint")
        if isinstance(status, str) and status not in MATURITY_STATUSES:
            issues.append(
                f"entry {idx}: status_at_mint '{status}' not a maturity status"
            )
        gen = entry.get("gen_at_mint")
        if isinstance(gen, str) and not gen.isdigit():
            issues.append(f"entry {idx}: gen_at_mint '{gen}' not an integer")
        date_val = entry.get("date")
        if isinstance(date_val, str) and not DATE_RE.match(date_val):
            issues.append(f"entry {idx}: date '{date_val}' not YYYY-MM-DD")
    return issues


def check_frontmatter(pages: list[dict]) -> list[dict]:
    findings = []
    for page in pages:
        if page["kind"] in EVOLVING_DIRS:
            required = REQUIRED_NODE_KEYS
        elif page["kind"] == "experiments":
            required = REQUIRED_EXPERIMENT_KEYS
        elif page["kind"] == "deliverables":
            required = REQUIRED_DELIVERABLE_KEYS
        else:
            required = REQUIRED_PAGE_KEYS
        fm = page["fm"] or {}
        node_type = fm.get("type")
        missing = sorted(k for k in required if k not in fm)
        invalid: dict = {}
        for key, allowed in VALID_ENUMS.items():
            if key == "status" and node_type == "experiment":
                allowed = EXPERIMENT_STATUSES
            elif key == "status" and node_type == "question":
                # question lifecycle, with maturity values tolerated as legacy
                # (they are counted separately in legacy_question_status)
                allowed = QUESTION_STATUSES | set(MATURITY_STATUSES)
            val = fm.get(key)
            if isinstance(val, str) and val not in allowed:
                invalid[key] = val
        for key in INT_KEYS:
            val = fm.get(key)
            if isinstance(val, str) and not val.isdigit():
                invalid[key] = val
        for key in DATE_KEYS:
            val = fm.get(key)
            if isinstance(val, str) and not DATE_RE.match(val):
                invalid[key] = val
        if page["kind"] in EVOLVING_DIRS and "borrowed" in fm:
            issues = validate_borrowed(fm["borrowed"])
            if issues:
                invalid["borrowed"] = issues
        if missing or invalid:
            findings.append(
                {"path": page["path"], "missing": missing, "invalid": invalid}
            )
    return findings


def check_legacy_question_status(pages: list[dict]) -> list[dict]:
    """Question pages still carrying a maturity value in `status:` (§2 legacy —
    the pre-0.9.0 convention). Tolerated, reported, never breaks `clean`."""
    findings = []
    for page in pages:
        fm = page["fm"] or {}
        if fm.get("type") != "question":
            continue
        status = fm.get("status")
        if isinstance(status, str) and status in MATURITY_STATUSES:
            findings.append({"path": page["path"], "status": status})
    return findings


def classify_target(
    target: str, wiki_stems: set[str], raw_names: set[str], raw_stems: set[str]
) -> str:
    t = target[2:] if target.startswith("./") else target
    if "/" in t:
        candidates = (
            SCOPE_ROOT / t,
            SCOPE_ROOT / f"{t}.md",
            WIKI_DIR / t,
            WIKI_DIR / f"{t}.md",
        )
        return "ok" if any(c.exists() for c in candidates) else "dead"
    if t in wiki_stems or t in raw_names or t in raw_stems:
        return "ok"
    return "external"


def check_links(pages: list[dict]) -> tuple[list[dict], list[dict]]:
    wiki_stems = {md.stem for md in WIKI_DIR.rglob("*.md")}
    raw_names: set[str] = set()
    raw_stems: set[str] = set()
    if RAW_DIR.is_dir():
        for f in RAW_DIR.rglob("*"):
            if f.is_file():
                raw_names.add(f.name)
                raw_stems.add(f.stem)
    dead, external = [], []
    for page in pages:
        for target in sorted(page["links"]):
            verdict = classify_target(target, wiki_stems, raw_names, raw_stems)
            if verdict == "dead":
                dead.append({"path": page["path"], "target": target})
            elif verdict == "external":
                external.append({"path": page["path"], "target": target})
    return dead, external


def check_orphans(node_pages: list[dict]) -> list[str]:
    inbound: dict[str, int] = {p["stem"]: 0 for p in node_pages}
    for page in node_pages:
        for target in page["links"]:
            stem = target.rsplit("/", 1)[-1]
            stem = stem[:-3] if stem.endswith(".md") else stem
            if stem in inbound and stem != page["stem"]:
                inbound[stem] += 1
    orphans = []
    for page in node_pages:
        if page["kind"] not in EVOLVING_DIRS:
            continue
        if (page["fm"] or {}).get("status") == "deprecated":
            continue  # deprecated nodes leave the graph by design (§3)
        if inbound[page["stem"]] == 0:
            orphans.append(page["path"])
    return sorted(orphans)


def check_contradictions(node_pages: list[dict]) -> list[dict]:
    findings = []
    for page in node_pages:
        via = []
        if CONTRADICTION_CALLOUT_RE.search(page["body"]):
            via.append("callout")
        if list_is_nonempty((page["fm"] or {}).get("contradicts")):
            via.append("frontmatter")
        if via:
            findings.append({"path": page["path"], "via": sorted(via)})
    return findings


def check_duplicate_stems() -> list[dict]:
    """Stems owned by >1 file under wiki/. Wikilinks resolve by stem (§9) and
    boundary-score keys pages by stem, so a shared stem makes one file
    silently unreachable (an ambiguous link / a dropped frontier candidate)."""
    by_stem: dict[str, list[str]] = {}
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if md.is_symlink():
            continue
        by_stem.setdefault(md.stem, []).append(
            md.relative_to(SCOPE_ROOT).as_posix()
        )
    return [
        {"stem": stem, "paths": sorted(paths)}
        for stem, paths in sorted(by_stem.items())
        if len(paths) > 1
    ]


def compute_status_census(node_pages: list[dict]) -> dict:
    """Maturity census computed from claims/ + mashups/ frontmatter (§11.2).

    This is the canonical census (P0-C): the index.md `**Census:**` line is a
    display copy. A page whose status falls outside the §3 ladder lands in no
    bucket (the frontmatter check already flags it), so total may exceed the
    bucket sum — deliberately visible.
    """
    census = {"total": 0, **{s: 0 for s in MATURITY_STATUSES}}
    for page in node_pages:
        if page["kind"] not in EVOLVING_DIRS:
            continue
        census["total"] += 1
        status = (page["fm"] or {}).get("status")
        if isinstance(status, str) and status in MATURITY_STATUSES:
            census[status] += 1
    return census


def check_census_drift(census: dict) -> list[dict]:
    """Compare the index.md `**Census:**` display line against the computed
    census. Warnings only — drift never breaks `clean` (the fix is a routine
    index refresh, not a structural fault). An empty scope with no census
    line is tolerated (nothing to disagree about yet)."""
    index_md = WIKI_DIR / "index.md"
    text = ""
    if index_md.is_file():
        try:
            text = index_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            text = ""
    m = CENSUS_LINE_RE.search(text)
    if not m:
        if census["total"] == 0:
            return []
        return [
            {
                "path": "wiki/index.md",
                "issue": "no **Census:** line found while evolving nodes exist "
                "(§11.2 index template)",
                "computed": census,
            }
        ]
    rest = m.group(1)
    found: dict = {s: 0 for s in MATURITY_STATUSES}
    tm = CENSUS_TOTAL_RE.search(rest)
    found["total"] = int(tm.group(1)) if tm else None
    for sm in CENSUS_PAIR_RE.finditer(rest):
        found[sm.group(1)] = int(sm.group(2))
    drift = any(found[s] != census[s] for s in MATURITY_STATUSES) or (
        found["total"] is not None and found["total"] != census["total"]
    )
    if not drift:
        return []
    return [
        {
            "path": "wiki/index.md",
            "issue": "**Census:** line disagrees with the computed status_census",
            "found": found,
            "computed": census,
        }
    ]


ALLOWLIST_RE = re.compile(r"Allowed external wikilinks:\s*(.*)$", re.MULTILINE)


def load_external_allowlist() -> set[str]:
    """Deliberate cross-scope wikilink stems declared in the scope CLAUDE.md
    (`Allowed external wikilinks: a, [[b]]`). Matching link targets are
    reported under `allowed_external` instead of `unresolved_external`, so
    intended vault/cross-scope citations stop reading as noise."""
    claude_md = SCOPE_ROOT / "CLAUDE.md"
    if not claude_md.is_file():
        return set()
    try:
        text = claude_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    m = ALLOWLIST_RE.search(text)
    if not m:
        return set()
    # the SCOPE_CLAUDE.md template annotates the toggle with an HTML comment
    raw = re.sub(r"<!--.*?-->", "", m.group(1)).strip()
    if raw.lower() in ("", "none", "(none)", "-", "disabled"):
        return set()
    entries: set[str] = set()
    for part in raw.split(","):
        stem = part.strip().strip("[]").strip()
        if stem:
            entries.add(stem)
    return entries


def check_eval() -> list[dict]:
    """Validate the LATEST session's `E####.eval.json` against §7 schema v2:
    `pass` must be a boolean and `stagnation.verdict` one of the fixed enum.
    Warnings only — a broken eval means the steering signal is unreliable,
    not that the wiki content is unhealthy, so `clean` is unaffected."""
    evo_dir = WIKI_DIR / "meta" / "evolution"
    if not evo_dir.is_dir():
        return []
    sessions: dict[str, dict] = {}
    for f in sorted(evo_dir.iterdir()):
        if not f.is_file():
            continue
        rm = SESSION_REPORT_RE.match(f.name)
        if rm:
            sessions.setdefault(rm.group(1), {})["report"] = f
        em = SESSION_EVAL_RE.match(f.name)
        if em:
            sessions.setdefault(em.group(1), {})["eval"] = f
    if not sessions:
        return []
    latest = max(sessions, key=lambda s: int(s[1:]))
    rel = f"wiki/meta/evolution/{latest}.eval.json"
    eval_path = sessions[latest].get("eval")
    if eval_path is None:
        return [
            {
                "path": rel,
                "issue": "missing — §7 requires an eval JSON next to the "
                f"{latest}.md report",
            }
        ]
    try:
        data = json.loads(eval_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return [{"path": rel, "issue": "unparseable JSON"}]
    if not isinstance(data, dict):
        return [{"path": rel, "issue": "top level is not an object"}]
    findings = []
    if not isinstance(data.get("pass"), bool):
        findings.append(
            {"path": rel, "issue": "`pass` missing or not a boolean (§7 required)"}
        )
    stagnation = data.get("stagnation")
    verdict = stagnation.get("verdict") if isinstance(stagnation, dict) else None
    if verdict not in STAGNATION_VERDICTS:
        findings.append(
            {
                "path": rel,
                "issue": "`stagnation.verdict` missing or not one of "
                "continue|reseed|change-strategy (§7 required)",
            }
        )
    return findings


def run(want_json: bool) -> int:
    if not WIKI_DIR.is_dir():
        log(
            f"ERR: no wiki/ directory under {SCOPE_ROOT} — run from a research-scope root"
        )
        return EXIT_USAGE

    node_pages = collect_node_pages()
    fm_findings = check_frontmatter(node_pages)
    legacy_question = check_legacy_question_status(node_pages)
    dead, external = check_links(node_pages + collect_aux_pages())
    allowlist = load_external_allowlist()
    allowed_external = [e for e in external if e["target"] in allowlist]
    external = [e for e in external if e["target"] not in allowlist]
    orphans = check_orphans(node_pages)
    contradictions = check_contradictions(node_pages)
    duplicate_stems = check_duplicate_stems()
    status_census = compute_status_census(node_pages)
    census_drift = check_census_drift(status_census)
    eval_findings = check_eval()

    counts = {
        "pages_checked": len(node_pages),
        "missing_frontmatter": len(fm_findings),
        "dead_wikilinks": len(dead),
        "orphans": len(orphans),
        "contradictions": len(contradictions),
        "duplicate_stems": len(duplicate_stems),
        "unresolved_external": len(external),
        "allowed_external": len(allowed_external),
        "legacy_question_status": len(legacy_question),
        "census_drift": len(census_drift),
        "eval_findings": len(eval_findings),
    }
    clean = all(
        counts[k] == 0
        for k in (
            "missing_frontmatter",
            "dead_wikilinks",
            "orphans",
            "contradictions",
            "duplicate_stems",
        )
    )
    report = {
        "generated": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "scope": str(SCOPE_ROOT),
        "counts": counts,
        "clean": clean,
        "status_census": status_census,
        "findings": {
            "missing_frontmatter": fm_findings,
            "dead_wikilinks": dead,
            "orphans": orphans,
            "contradictions": contradictions,
            "duplicate_stems": duplicate_stems,
            "unresolved_external": external,
            "allowed_external": allowed_external,
            "legacy_question_status": legacy_question,
            "census_drift": census_drift,
            "eval_findings": eval_findings,
        },
    }

    if want_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return EXIT_OK

    print("# Wiki Lint Report")
    print(f"scope: {SCOPE_ROOT}")
    print(f"pages checked: {counts['pages_checked']} · clean: {clean}")
    census_parts = " · ".join(f"{s} {status_census[s]}" for s in MATURITY_STATUSES)
    print(f"status census: {status_census['total']} nodes · {census_parts}")
    for label, items in (
        ("missing/invalid frontmatter", fm_findings),
        ("dead wikilinks", dead),
        ("orphans", orphans),
        ("unresolved contradictions", contradictions),
        ("duplicate stems", duplicate_stems),
        ("unresolved external links (verify manually)", external),
        ("allowed external links (scope CLAUDE.md allowlist)", allowed_external),
        ("legacy question status (§2 pre-lifecycle values)", legacy_question),
        ("census drift (warning — refresh index.md)", census_drift),
        ("eval findings (warning — §7 schema v2)", eval_findings),
    ):
        print(f"\n## {label}: {len(items)}")
        for item in items:
            print(
                f"- {item}"
                if isinstance(item, str)
                else f"- {json.dumps(item, ensure_ascii=False)}"
            )
    return EXIT_OK


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    return run(args.json)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
