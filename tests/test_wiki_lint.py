"""Tests for scripts/wiki-lint.py (EVOLUTION.md §4 Phase E.3 health check).

The linter runs from a research-scope root, reads ./wiki (and ./.raw for
link resolution), and reports four findings: missing/invalid frontmatter,
dead wikilinks, orphan nodes, unresolved contradictions. Links that cannot
be resolved inside the scope but look like bare cross-scope citations are
reported separately as `unresolved_external` and do not break `clean`.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "wiki-lint.py"


def node_text(
    *,
    ntype="claim",
    title="t",
    status="seed",
    confidence="low",
    generation="1",
    body="",
    omit=(),
    extra_fm="",
) -> str:
    fm = {
        "type": ntype,
        "title": f'"{title}"',
        "created": "2026-06-12",
        "updated": "2026-06-12",
        "status": status,
        "confidence": confidence,
        "generation": generation,
        "last_challenged": "2026-06-12",
        "challenges_survived": "0",
    }
    lines = [f"{k}: {v}" for k, v in fm.items() if k not in omit]
    if extra_fm:
        lines.append(extra_fm)
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body + "\n"


def experiment_text(
    *,
    title="exp",
    status="planned",
    claim="[[클레임A]]",
    created="2026-06-12",
    body="",
    omit=(),
) -> str:
    """A §2 `type: experiment` pre-registration node (no evolution-mechanic keys)."""
    fm = {
        "type": "experiment",
        "title": f'"{title}"',
        "created": created,
        "updated": created,
        "status": status,
        "claim": f'"{claim}"',
    }
    lines = [f"{k}: {v}" for k, v in fm.items() if k not in omit]
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body + "\n"


def write(scope: Path, rel: str, text: str) -> Path:
    p = scope / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def run_lint(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--json"], cwd=cwd, capture_output=True, text=True
    )


class WikiLintTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_clean_scope(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="supports [[노드B]]"),
        )
        write(
            self.scope,
            "wiki/claims/노드B.md",
            node_text(title="B", body="see [[노드A]]"),
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["pages_checked"], 2)
        zero_keys = (
            "missing_frontmatter",
            "dead_wikilinks",
            "orphans",
            "contradictions",
            "unresolved_external",
        )
        self.assertEqual(
            {k: data["counts"][k] for k in zero_keys}, {k: 0 for k in zero_keys}
        )

    def test_empty_wiki_is_clean(self):
        (self.scope / "wiki" / "claims").mkdir(parents=True)
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["pages_checked"], 0)

    def test_missing_and_invalid_frontmatter(self):
        write(
            self.scope,
            "wiki/claims/불량노드.md",
            node_text(
                title="bad",
                status="solid",
                omit=("confidence", "last_challenged"),
                body="[[좋은노드]]",
            ),
        )
        write(
            self.scope,
            "wiki/claims/좋은노드.md",
            node_text(title="ok", body="[[불량노드]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 1)
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/claims/불량노드.md")
        self.assertEqual(sorted(finding["missing"]), ["confidence", "last_challenged"])
        self.assertEqual(finding["invalid"], {"status": "solid"})

    def test_dead_vs_external_unresolved_links(self):
        (self.scope / ".raw").mkdir()
        (self.scope / ".raw" / "논문.pdf").write_bytes(b"%PDF")
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(
                title="A",
                body="[[wiki/claims/없는노드]] [[외부볼트노트]] "
                "[[.raw/논문.pdf]] [[노드B]]",
            ),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["dead_wikilinks"], 1)
        self.assertEqual(
            data["findings"]["dead_wikilinks"][0]["target"], "wiki/claims/없는노드"
        )
        self.assertEqual(data["counts"]["unresolved_external"], 1)
        self.assertEqual(
            data["findings"]["unresolved_external"][0]["target"], "외부볼트노트"
        )

    def test_wikilinks_inside_code_fences_are_ignored(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="```\n[[펜스속링크]]\n```\n[[노드B]]"),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["unresolved_external"], 0)

    def test_orphans_frontmatter_links_and_deprecated_exemption(self):
        write(self.scope, "wiki/claims/외톨이.md", node_text(title="o"))
        write(self.scope, "wiki/claims/지지받는노드.md", node_text(title="s"))
        write(
            self.scope,
            "wiki/claims/지지하는노드.md",
            node_text(title="b", extra_fm='supports: ["[[지지받는노드]]"]'),
        )
        write(
            self.scope,
            "wiki/claims/은퇴노드.md",
            node_text(title="d", status="deprecated"),
        )
        # index links never rescue a node from orphanhood
        write(
            self.scope,
            "wiki/index.md",
            "# Index\n[[외톨이]] [[지지받는노드]] [[지지하는노드]] [[은퇴노드]]\n",
        )
        data = self.lint()
        self.assertEqual(
            data["findings"]["orphans"],
            ["wiki/claims/외톨이.md", "wiki/claims/지지하는노드.md"],
        )

    def test_contradictions_via_callout_and_frontmatter(self):
        write(
            self.scope,
            "wiki/claims/모순A.md",
            node_text(
                title="a",
                extra_fm='contradicts: ["[[모순B]]"]',
                body="> [!contradiction] B와 충돌\n\n[[모순B]]",
            ),
        )
        write(
            self.scope, "wiki/claims/모순B.md", node_text(title="b", body="[[모순A]]")
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["contradictions"], 1)
        finding = data["findings"]["contradictions"][0]
        self.assertEqual(finding["path"], "wiki/claims/모순A.md")
        self.assertEqual(sorted(finding["via"]), ["callout", "frontmatter"])

    def test_empty_contradicts_list_is_resolved(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="a", extra_fm="contradicts: []", body="[[노드B]]"),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="b", body="[[노드A]]")
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["contradictions"], 0)

    def test_duplicate_stems_across_dirs(self):
        # wikilinks resolve by stem across the whole wiki (§9), so two files
        # sharing a stem are ambiguous — boundary-score silently drops one.
        write(
            self.scope,
            "wiki/claims/중복.md",
            node_text(title="c", body="[[다른노드]]"),
        )
        write(
            self.scope,
            "wiki/sources/중복.md",
            node_text(ntype="source", title="s"),
        )
        write(
            self.scope,
            "wiki/claims/다른노드.md",
            node_text(title="o", body="[[중복]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["duplicate_stems"], 1)
        self.assertEqual(data["counts"]["orphans"], 0)
        self.assertEqual(data["counts"]["dead_wikilinks"], 0)
        finding = data["findings"]["duplicate_stems"][0]
        self.assertEqual(finding["stem"], "중복")
        self.assertEqual(
            finding["paths"], ["wiki/claims/중복.md", "wiki/sources/중복.md"]
        )

    def test_usage_error_without_wiki(self):
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("wiki", proc.stderr)

    def test_experiment_node_is_valid(self):
        # A pre-registration node (§2) carries type/title/created/status/claim and
        # nothing else; it must lint clean and be counted as a page.
        write(self.scope, "wiki/claims/클레임A.md", node_text(title="A", body="[[클레임B]]"))
        write(self.scope, "wiki/claims/클레임B.md", node_text(title="B", body="[[클레임A]]"))
        write(
            self.scope,
            "wiki/experiments/실험.md",
            experiment_text(title="exp", claim="[[클레임A]]", body="## Hypothesis\nA holds."),
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["pages_checked"], 3)
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)

    def test_experiment_status_uses_experiment_enum_not_claim_enum(self):
        # `hardened` is a valid CLAIM status but not a valid EXPERIMENT status,
        # so status validation must branch on type (§2 experiment lifecycle).
        write(self.scope, "wiki/claims/클레임A.md", node_text(title="A"))
        write(
            self.scope,
            "wiki/experiments/실험.md",
            experiment_text(title="exp", status="hardened", claim="[[클레임A]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 1)
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/experiments/실험.md")
        self.assertEqual(finding["invalid"], {"status": "hardened"})
        self.assertEqual(finding["missing"], [])

    def test_experiment_missing_required_keys(self):
        # Experiments require type/title/created/status/claim — not the full
        # evolving-node key set, but more than a bare page.
        write(
            self.scope,
            "wiki/experiments/실험.md",
            experiment_text(title="exp", omit=("status", "claim")),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 1)
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/experiments/실험.md")
        self.assertEqual(finding["missing"], ["claim", "status"])


if __name__ == "__main__":
    unittest.main()
