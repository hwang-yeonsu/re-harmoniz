"""Tests for scripts/boundary-score.py.

Contract under test (EVOLUTION.md §4 Phase B): the script is executed from a
research-scope root and scores `./wiki/**/*.md` relative to the current
working directory — NOT relative to the script file, which lives in the
installed plugin directory.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "boundary-score.py"


def write_node(
    scope: Path,
    rel: str,
    *,
    title: str,
    updated: str,
    body: str = "",
    ntype: str = "claim",
) -> Path:
    p = scope / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "---\n"
        f"type: {ntype}\n"
        f'title: "{title}"\n'
        f"created: {updated}\n"
        f"updated: {updated}\n"
        "---\n"
        f"{body}\n",
        encoding="utf-8",
    )
    return p


def run_script(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class BoundaryScoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_scores_wiki_under_cwd(self):
        today = date.today().isoformat()
        write_node(
            self.scope,
            "wiki/claims/프론티어노드.md",
            title="프론티어",
            updated=today,
            body="[[허브노드]] and [[허브노드|별칭]]",
        )
        write_node(self.scope, "wiki/claims/허브노드.md", title="허브", updated=today)
        proc = run_script(self.scope, "--json", "--include-score-zero")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["page_count_scoreable"], 2)
        by_key = {r["title_key"]: r for r in data["results"]}
        # alias link to the same target is deduplicated → out_degree 1
        self.assertEqual(by_key["프론티어노드"]["out_degree"], 1)
        self.assertEqual(by_key["프론티어노드"]["in_degree"], 0)
        self.assertEqual(by_key["허브노드"]["out_degree"], 0)
        self.assertEqual(by_key["허브노드"]["in_degree"], 1)
        self.assertGreater(by_key["프론티어노드"]["score"], 0.0)
        self.assertLess(by_key["허브노드"]["score"], 0.0)

    def test_meta_pages_are_not_scoreable(self):
        today = date.today().isoformat()
        write_node(self.scope, "wiki/claims/노드.md", title="노드", updated=today)
        write_node(
            self.scope,
            "wiki/meta/evolution/E0001.md",
            title="E0001",
            updated=today,
            ntype="meta",
        )
        proc = run_script(self.scope, "--json", "--include-score-zero")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["page_count_scoreable"], 1)
        self.assertEqual(data["results"][0]["title_key"], "노드")

    def test_protocol_aux_files_excluded(self):
        # index/hot/log/overview are excluded by filename even when not
        # type:meta — guards the §1-aligned EXCLUDE_FILENAMES trim.
        today = date.today().isoformat()
        write_node(self.scope, "wiki/claims/노드.md", title="n", updated=today)
        for aux in ("index.md", "hot.md", "log.md", "overview.md"):
            write_node(self.scope, f"wiki/{aux}", title=aux, updated=today)
        proc = run_script(self.scope, "--json", "--include-score-zero")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["page_count_scoreable"], 1)
        self.assertEqual(data["results"][0]["title_key"], "노드")

    def test_fails_fast_when_cwd_is_not_a_scope(self):
        proc = run_script(self.scope, "--json")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("wiki", proc.stderr)


if __name__ == "__main__":
    unittest.main()
