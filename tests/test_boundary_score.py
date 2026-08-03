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

    def test_deliverable_pages_are_not_scoreable(self):
        # Deliverables (§14) are non-evolving answer snapshots — like meta and
        # experiment they must never skew the frontier graph.
        today = date.today().isoformat()
        write_node(self.scope, "wiki/claims/노드.md", title="노드", updated=today)
        write_node(
            self.scope,
            "wiki/deliverables/답변.md",
            title="답변",
            updated=today,
            ntype="deliverable",
            body="[[노드]]",
        )
        proc = run_script(self.scope, "--json", "--include-score-zero")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["page_count_scoreable"], 1)
        self.assertEqual(data["results"][0]["title_key"], "노드")
        # and the deliverable's outbound link must not count as inbound degree
        self.assertEqual(data["results"][0]["in_degree"], 0)

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


class ServesFilterTest(unittest.TestCase):
    """§4 Phase B (1.0.0): the frontier is asked *within a decision*. The score
    formula is unchanged — relevance enters as a filter, not as a weight, so a
    node that tops the frontier while serving nothing cannot steal the session."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.today = date.today().isoformat()

    def _scope_with_three_nodes(self):
        # each points outward at the same two sinks → positive score for all three
        for stem, serves in (
            ("결정1노드", 'serves: ["D1"]'),
            ("결정2노드", 'serves: ["D2"]'),
            ("양쪽노드", "serves:\n  - D1\n  - D2"),
        ):
            write_node(
                self.scope,
                f"wiki/claims/{stem}.md",
                title=stem,
                updated=self.today,
                body="[[싱크A]] [[싱크B]]",
                extra_fm=serves,
            )
        write_node(
            self.scope, "wiki/claims/미배정노드.md", title="unassigned",
            updated=self.today, body="[[싱크A]] [[싱크B]]",
        )
        for sink in ("싱크A", "싱크B"):
            write_node(
                self.scope, f"wiki/claims/{sink}.md", title=sink, updated=self.today
            )

    def _rows(self, *args: str) -> list[dict]:
        proc = run_script(self.scope, "--json", "--top", "20", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)["results"]

    def test_json_row_exposes_serves(self):
        self._scope_with_three_nodes()
        by_key = {r["title_key"]: r for r in self._rows()}
        self.assertEqual(by_key["결정1노드"]["serves"], ["D1"])
        self.assertEqual(by_key["양쪽노드"]["serves"], ["D1", "D2"])
        self.assertEqual(by_key["미배정노드"]["serves"], [])

    def test_serves_filter_keeps_only_nodes_serving_that_decision(self):
        self._scope_with_three_nodes()
        keys = sorted(r["title_key"] for r in self._rows("--serves", "D1"))
        self.assertEqual(keys, ["결정1노드", "양쪽노드"])

    def test_serves_filter_excludes_unassigned_nodes(self):
        self._scope_with_three_nodes()
        keys = [r["title_key"] for r in self._rows("--serves", "D2")]
        self.assertNotIn("미배정노드", keys)
        self.assertEqual(sorted(keys), ["결정2노드", "양쪽노드"])

    def test_unknown_decision_yields_an_empty_frontier_not_an_error(self):
        # unlike --page (which names one page), a filter matching nothing is a
        # legitimate answer: "no frontier inside this decision"
        self._scope_with_three_nodes()
        proc = run_script(self.scope, "--json", "--serves", "D9")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["results"], [])

    def test_filter_does_not_change_the_score_of_the_nodes_it_keeps(self):
        self._scope_with_three_nodes()
        unfiltered = {r["title_key"]: r["score"] for r in self._rows()}
        filtered = {r["title_key"]: r["score"] for r in self._rows("--serves", "D1")}
        for key, score in filtered.items():
            self.assertEqual(score, unfiltered[key])

    def test_text_output_reports_the_active_decision_filter(self):
        self._scope_with_three_nodes()
        proc = run_script(self.scope, "--serves", "D1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("D1", proc.stdout)
        self.assertNotIn("결정2노드", proc.stdout)

    def test_page_missing_from_the_filtered_set_says_which_decision(self):
        # the page exists; it just does not serve D2. "no page matches" alone
        # reads as "no such page", which sends the reader looking for a typo.
        self._scope_with_three_nodes()
        proc = run_script(self.scope, "--page", "결정1노드", "--serves", "D2")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("D2", proc.stderr)


class TerminalStatusFrontierTest(unittest.TestCase):
    """§3: `deprecated` and `pruned` nodes have left the graph, so they must not
    compete for the next session's attention.

    Pruning bumps `updated` (the flip appends a one-line reason), which puts a
    just-cut branch at `recency_weight` 1.0 — the top of the very frontier the
    cut was supposed to remove it from. The autonomous loop auto-picks
    frontier-top, so this is a live re-targeting path, not a display nit."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.today = date.today().isoformat()

    def _scope(self, terminal_status: str, *, serves: str = ""):
        """One terminal node outscoring one live node, both freshly updated."""
        write_node(
            self.scope, "wiki/claims/잘린노드.md", title="terminal",
            updated=self.today, body="[[싱크A]] [[싱크B]] [[싱크C]]",
            extra_fm=f"status: {terminal_status}" + (f"\n{serves}" if serves else ""),
        )
        write_node(
            self.scope, "wiki/claims/살아있는노드.md", title="live",
            updated=self.today, body="[[싱크A]]",
            extra_fm='status: developing\nserves: ["D1"]',
        )
        for sink in ("싱크A", "싱크B", "싱크C"):
            write_node(
                self.scope, f"wiki/claims/{sink}.md", title=sink,
                updated=self.today, extra_fm="status: seed",
            )

    def _keys(self, *args: str) -> list[str]:
        proc = run_script(self.scope, "--json", "--top", "20", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return [r["title_key"] for r in json.loads(proc.stdout)["results"]]

    def test_pruned_node_is_excluded_from_the_frontier(self):
        self._scope("pruned")
        self.assertEqual(self._keys(), ["살아있는노드"])

    def test_deprecated_node_is_excluded_from_the_frontier(self):
        self._scope("deprecated")
        self.assertEqual(self._keys(), ["살아있는노드"])

    def test_serves_filter_does_not_resurrect_a_pruned_node(self):
        # the §3 "superseded" prune reason cuts a node while the decision it
        # names stays open, so `serves:` still matches — status has to be what
        # excludes it, not the filter
        self._scope("pruned", serves='serves: ["D1"]')
        self.assertEqual(self._keys("--serves", "D1"), ["살아있는노드"])

    def test_include_terminal_brings_them_back_at_an_unchanged_score(self):
        self._scope("pruned")
        proc = run_script(self.scope, "--json", "--top", "20", "--include-terminal")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = {r["title_key"]: r for r in json.loads(proc.stdout)["results"]}
        self.assertEqual(sorted(rows), ["살아있는노드", "잘린노드"])
        # exclusion is a filter, like --serves: it never re-weights what it keeps
        self.assertEqual(rows["잘린노드"]["score"], 3.0)
        self.assertEqual(rows["살아있는노드"]["score"], 1.0)

    def test_a_node_without_status_is_still_scored(self):
        # pre-1.0.0 pages and any page whose frontmatter omits `status`
        write_node(
            self.scope, "wiki/claims/무상태.md", title="bare",
            updated=self.today, body="[[싱크A]]",
        )
        write_node(
            self.scope, "wiki/claims/싱크A.md", title="싱크A", updated=self.today
        )
        self.assertEqual(self._keys(), ["무상태"])

    def test_terminal_pages_still_count_as_scoreable_and_as_link_targets(self):
        # excluded from the *ranking*, not from the graph: a live node pointing
        # at a pruned one keeps that out-edge, or its score would silently drop
        self._scope("pruned")
        proc = run_script(self.scope, "--json", "--top", "20")
        data = json.loads(proc.stdout)
        self.assertEqual(data["page_count_scoreable"], 5)


if __name__ == "__main__":
    unittest.main()
