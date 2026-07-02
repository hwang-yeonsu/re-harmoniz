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
    extra_fm: str = "",
) -> Path:
    p = scope / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    extra = f"{extra_fm}\n" if extra_fm else ""
    p.write_text(
        "---\n"
        f"type: {ntype}\n"
        f'title: "{title}"\n'
        f"created: {updated}\n"
        f"updated: {updated}\n"
        f"{extra}"
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

    def test_experiment_pages_are_not_scoreable(self):
        # Experiment pre-registrations (§2) are design records, not knowledge
        # nodes — they must be excluded from frontier scoring like type:meta.
        today = date.today().isoformat()
        write_node(self.scope, "wiki/claims/노드.md", title="노드", updated=today)
        write_node(
            self.scope,
            "wiki/experiments/실험.md",
            title="실험",
            updated=today,
            ntype="experiment",
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

    def test_json_exposes_evolution_fields(self):
        # 0.9.0 (§13 deep-research bridge): pushing needs status / generation /
        # challenges_survived / sources_count per row to spot claims stuck
        # short of the ≥2-independent-sources gate without re-reading files.
        today = date.today().isoformat()
        sources = ["[[출처A]]", "[[출처B]]"]
        extra = (
            "status: developing\n"
            "confidence: medium\n"
            "generation: 3\n"
            "challenges_survived: 2\n"
            "sources:\n" + "\n".join(f'  - "{s}"' for s in sources)
        )
        write_node(
            self.scope,
            "wiki/claims/노드.md",
            title="노드",
            updated=today,
            body="[[허브노드]]",
            extra_fm=extra,
        )
        write_node(self.scope, "wiki/claims/허브노드.md", title="허브", updated=today)
        proc = run_script(self.scope, "--json", "--include-score-zero")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        by_key = {r["title_key"]: r for r in json.loads(proc.stdout)["results"]}
        row = by_key["노드"]
        self.assertEqual(row["status"], "developing")
        self.assertEqual(row["generation"], 3)
        self.assertEqual(row["challenges_survived"], 2)
        self.assertEqual(row["sources_count"], len(sources))
        bare = by_key["허브노드"]
        self.assertIsNone(bare["status"])
        self.assertIsNone(bare["generation"])
        self.assertIsNone(bare["challenges_survived"])
        self.assertEqual(bare["sources_count"], 0)


if __name__ == "__main__":
    unittest.main()
