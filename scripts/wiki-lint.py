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
     review them manually.
  3. orphans — claims/mashups (excluding deprecated) with zero inbound
     wikilinks from other node pages. Links from index/hot/log/overview or
     meta pages do not rescue a node; frontmatter wikilinks (supports: …) do.
  4. unresolved contradictions — `> [!contradiction]` callouts in bodies or
     non-empty `contradicts:` frontmatter.
  5. duplicate stems — two wiki/ files sharing a filename stem. Wikilinks
     resolve by stem (§9), so a collision makes one file unreachable.

`clean` = the five checks all count zero (`unresolved_external` excluded).

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

NODE_DIRS = ("claims", "mashups", "sources", "questions", "experiments")
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
VALID_ENUMS = {
    "type": {"claim", "mashup", "source", "question", "meta", "experiment"},
    "status": {"seed", "developing", "hardened", "evergreen", "deprecated"},
    "confidence": {"high", "medium", "low"},
}
# `status` is type-dependent: experiment nodes use their own lifecycle, never the
# maturity ladder (§3). check_frontmatter swaps this set in when type == experiment.
EXPERIMENT_STATUSES = {"planned", "running", "imported", "abandoned"}
DATE_KEYS = ("created", "updated", "last_challenged")
INT_KEYS = ("generation", "challenges_survived")

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


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, body). frontmatter is None when no block exists.

    Values are strings; block-style lists (`key:` followed by `- item` lines)
    become Python lists. No YAML library — stdlib only, same spirit as
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
            items: list[str] = []
            for nxt in lines[i + 1 :]:
                if re.match(r"^\s*-\s+", nxt):
                    items.append(nxt.strip()[1:].strip())
                elif nxt.strip() == "":
                    continue
                else:
                    break
            fm[key] = items
        else:
            fm[key] = val.strip().strip('"').strip("'")
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


def check_frontmatter(pages: list[dict]) -> list[dict]:
    findings = []
    for page in pages:
        if page["kind"] in EVOLVING_DIRS:
            required = REQUIRED_NODE_KEYS
        elif page["kind"] == "experiments":
            required = REQUIRED_EXPERIMENT_KEYS
        else:
            required = REQUIRED_PAGE_KEYS
        fm = page["fm"] or {}
        node_type = fm.get("type")
        missing = sorted(k for k in required if k not in fm)
        invalid: dict = {}
        for key, allowed in VALID_ENUMS.items():
            if key == "status" and node_type == "experiment":
                allowed = EXPERIMENT_STATUSES
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
        if missing or invalid:
            findings.append(
                {"path": page["path"], "missing": missing, "invalid": invalid}
            )
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


def run(want_json: bool) -> int:
    if not WIKI_DIR.is_dir():
        log(
            f"ERR: no wiki/ directory under {SCOPE_ROOT} — run from a research-scope root"
        )
        return EXIT_USAGE

    node_pages = collect_node_pages()
    fm_findings = check_frontmatter(node_pages)
    dead, external = check_links(node_pages + collect_aux_pages())
    orphans = check_orphans(node_pages)
    contradictions = check_contradictions(node_pages)
    duplicate_stems = check_duplicate_stems()

    counts = {
        "pages_checked": len(node_pages),
        "missing_frontmatter": len(fm_findings),
        "dead_wikilinks": len(dead),
        "orphans": len(orphans),
        "contradictions": len(contradictions),
        "duplicate_stems": len(duplicate_stems),
        "unresolved_external": len(external),
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
        "findings": {
            "missing_frontmatter": fm_findings,
            "dead_wikilinks": dead,
            "orphans": orphans,
            "contradictions": contradictions,
            "duplicate_stems": duplicate_stems,
            "unresolved_external": external,
        },
    }

    if want_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return EXIT_OK

    print("# Wiki Lint Report")
    print(f"scope: {SCOPE_ROOT}")
    print(f"pages checked: {counts['pages_checked']} · clean: {clean}")
    for label, items in (
        ("missing/invalid frontmatter", fm_findings),
        ("dead wikilinks", dead),
        ("orphans", orphans),
        ("unresolved contradictions", contradictions),
        ("duplicate stems", duplicate_stems),
        ("unresolved external links (verify manually)", external),
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
