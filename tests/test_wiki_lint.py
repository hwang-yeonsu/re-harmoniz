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

    # ---- status_census (P0-C: census is computed, index line is display) ----

    def _seed_statused_nodes(self) -> dict:
        """Write claims/mashups with a known status mix; return expected census."""
        statuses = ["seed", "seed", "developing", "hardened", "deprecated"]
        for i, status in enumerate(statuses):
            body = f"[[노드{(i + 1) % len(statuses)}]]"
            if i == 0:
                body += " [[매쉬업]]"  # keeps the mashup from linting as an orphan
            write(
                self.scope,
                f"wiki/claims/노드{i}.md",
                node_text(title=f"c{i}", status=status, body=body),
            )
        write(
            self.scope,
            "wiki/mashups/매쉬업.md",
            node_text(ntype="mashup", title="m", status="developing", body="[[노드0]]"),
        )
        statuses.append("developing")  # the mashup counts too
        expected = {"total": len(statuses)}
        for s in ("seed", "developing", "hardened", "evergreen", "deprecated"):
            expected[s] = statuses.count(s)
        return expected

    def test_status_census_counts_claims_and_mashups_only(self):
        expected = self._seed_statused_nodes()
        # sources/questions/experiments never enter the maturity census
        write(
            self.scope,
            "wiki/sources/출처.md",
            "---\ntype: source\ntitle: \"s\"\n---\n",
        )
        write(
            self.scope,
            "wiki/experiments/실험.md",
            experiment_text(title="exp", claim="[[노드0]]"),
        )
        data = self.lint()
        self.assertEqual(data["status_census"], expected)

    def test_census_drift_on_mismatching_index_line(self):
        expected = self._seed_statused_nodes()
        write(
            self.scope,
            "wiki/index.md",
            "# Index\n\n**Census:** 99 nodes · seed 9 · developing 0 · "
            "hardened 0 · evergreen 0 · deprecated 0 (2026-06-12)\n",
        )
        data = self.lint()
        self.assertEqual(data["counts"]["census_drift"], 1)
        finding = data["findings"]["census_drift"][0]
        self.assertEqual(finding["path"], "wiki/index.md")
        self.assertEqual(finding["computed"], expected)
        self.assertEqual(finding["found"]["total"], 99)
        # drift is a warning: it must never break `clean`
        self.assertTrue(data["clean"])

    def test_census_matching_index_line_is_quiet(self):
        expected = self._seed_statused_nodes()
        line = (
            f"**Census:** {expected['total']} nodes · seed {expected['seed']} · "
            f"developing {expected['developing']} · hardened {expected['hardened']} · "
            f"evergreen {expected['evergreen']} · deprecated {expected['deprecated']} "
            "(2026-06-12)"
        )
        write(self.scope, "wiki/index.md", f"# Index\n\n{line}\n")
        data = self.lint()
        self.assertEqual(data["counts"]["census_drift"], 0)
        self.assertEqual(data["findings"]["census_drift"], [])

    def test_census_line_missing_warns_but_stays_clean(self):
        self._seed_statused_nodes()
        write(self.scope, "wiki/index.md", "# Index\n\nno census here\n")
        data = self.lint()
        self.assertEqual(data["counts"]["census_drift"], 1)
        self.assertIn("Census", data["findings"]["census_drift"][0]["issue"])
        self.assertTrue(data["clean"])

    def test_empty_scope_has_zero_census_and_no_drift(self):
        (self.scope / "wiki" / "claims").mkdir(parents=True)
        data = self.lint()
        self.assertEqual(
            data["status_census"],
            {
                "total": 0,
                "seed": 0,
                "developing": 0,
                "hardened": 0,
                "evergreen": 0,
                "deprecated": 0,
            },
        )
        self.assertEqual(data["counts"]["census_drift"], 0)

    # ---- eval_findings (P0-B: §7 eval schema v2 validation, non-breaking) ----

    def _clean_pair(self):
        write(
            self.scope, "wiki/claims/노드A.md", node_text(title="A", body="[[노드B]]")
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )

    def test_valid_eval_v2_yields_no_findings(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/meta/evolution/E0001.md",
            "---\ntype: meta\ntitle: \"E0001\"\n---\n# E0001\n",
        )
        write(
            self.scope,
            "wiki/meta/evolution/E0001.eval.json",
            json.dumps(
                {
                    "pass": True,
                    "score": 0.8,
                    "checks": {
                        "lint_clean": True,
                        "generation_progress": 2,
                        "mutations_rejected": 1,
                        "new_independent_sources": 1,
                    },
                    "stagnation": {"verdict": "continue"},
                }
            ),
        )
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 0)
        self.assertTrue(data["clean"])

    def test_missing_eval_for_latest_report_warns_but_stays_clean(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/meta/evolution/E0001.md",
            "---\ntype: meta\ntitle: \"E0001\"\n---\n# E0001\n",
        )
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 1)
        finding = data["findings"]["eval_findings"][0]
        self.assertEqual(finding["path"], "wiki/meta/evolution/E0001.eval.json")
        self.assertIn("missing", finding["issue"])
        self.assertTrue(data["clean"])

    def test_unparseable_eval_is_reported(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/meta/evolution/E0001.eval.json",
            "{ this is not json",
        )
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 1)
        self.assertIn("unparseable", data["findings"]["eval_findings"][0]["issue"])
        self.assertTrue(data["clean"])

    def test_eval_missing_pass_and_bad_verdict_are_both_reported(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/meta/evolution/E0001.eval.json",
            json.dumps({"pass": "yes", "stagnation": {"verdict": "flat"}}),
        )
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 2)
        issues = sorted(f["issue"] for f in data["findings"]["eval_findings"])
        self.assertIn("pass", issues[0])
        self.assertIn("stagnation.verdict", issues[1])
        self.assertTrue(data["clean"])

    def test_only_latest_session_eval_is_validated(self):
        # E0001 has a broken eval, E0002 has a valid one — only the latest
        # session (E0002) is checked, so no findings.
        self._clean_pair()
        write(self.scope, "wiki/meta/evolution/E0001.eval.json", "broken{")
        write(
            self.scope,
            "wiki/meta/evolution/E0002.md",
            "---\ntype: meta\ntitle: \"E0002\"\n---\n# E0002\n",
        )
        write(
            self.scope,
            "wiki/meta/evolution/E0002.eval.json",
            json.dumps({"pass": False, "stagnation": {"verdict": "reseed"}}),
        )
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 0)

    def test_no_sessions_no_eval_findings(self):
        self._clean_pair()
        data = self.lint()
        self.assertEqual(data["counts"]["eval_findings"], 0)

    # ---- borrowed: snapshot validation (0.9.0 modal-interchange drift) ----

    BORROWED_OK = (
        "borrowed:\n"
        '  - node: "[[도너노드]]"\n'
        "    scope: /abs/Research_B\n"
        "    status_at_mint: hardened\n"
        "    gen_at_mint: 4\n"
        "    date: 2026-06-30"
    )

    def test_borrowed_snapshot_valid(self):
        write(
            self.scope,
            "wiki/mashups/교차매쉬업.md",
            node_text(
                ntype="mashup",
                title="m",
                extra_fm=self.BORROWED_OK,
                body="[[노드A]]",
            ),
        )
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[교차매쉬업]]"),
        )
        data = self.lint()
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)
        # the donor wikilink is cross-scope: reported external, not dead
        self.assertEqual(data["counts"]["dead_wikilinks"], 0)
        self.assertEqual(
            data["findings"]["unresolved_external"][0]["target"], "도너노드"
        )
        self.assertTrue(data["clean"])

    def test_borrowed_missing_subkeys_and_bad_status_flagged(self):
        bad = (
            "borrowed:\n"
            '  - node: "[[도너노드]]"\n'
            "    status_at_mint: solid\n"
            "    gen_at_mint: four"
        )
        write(
            self.scope,
            "wiki/mashups/교차매쉬업.md",
            node_text(ntype="mashup", title="m", extra_fm=bad, body="[[노드A]]"),
        )
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[교차매쉬업]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 1)
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/mashups/교차매쉬업.md")
        issues = "\n".join(finding["invalid"]["borrowed"])
        self.assertIn("scope", issues)
        self.assertIn("date", issues)
        self.assertIn("status_at_mint", issues)
        self.assertIn("gen_at_mint", issues)

    def test_borrowed_plain_string_entries_flagged(self):
        write(
            self.scope,
            "wiki/mashups/교차매쉬업.md",
            node_text(
                ntype="mashup",
                title="m",
                extra_fm='borrowed: ["[[도너노드]]"]',
                body="[[노드A]]",
            ),
        )
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[교차매쉬업]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertIn("borrowed", finding["invalid"])

    # ---- question lifecycle (0.9.0 §2: open|answered|escalated|archived) ----

    def test_question_lifecycle_status_valid(self):
        self._clean_pair()
        for status in ("open", "answered", "escalated", "archived"):
            write(
                self.scope,
                f"wiki/questions/질문-{status}.md",
                f'---\ntype: question\ntitle: "q"\nstatus: {status}\n---\n',
            )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["legacy_question_status"], 0)

    def test_question_legacy_maturity_status_tolerated_but_reported(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/questions/구질문.md",
            '---\ntype: question\ntitle: "q"\nstatus: seed\n---\n',
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)
        self.assertEqual(data["counts"]["legacy_question_status"], 1)
        finding = data["findings"]["legacy_question_status"][0]
        self.assertEqual(finding["path"], "wiki/questions/구질문.md")
        self.assertEqual(finding["status"], "seed")

    def test_question_unknown_status_flagged(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/questions/이상질문.md",
            '---\ntype: question\ntitle: "q"\nstatus: solved\n---\n',
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["invalid"], {"status": "solved"})
        self.assertEqual(data["counts"]["legacy_question_status"], 0)

    # ---- experiment claim: string OR list (0.9.0 §2, field evidence #3) ----

    def test_experiment_claim_as_list_is_valid(self):
        self._clean_pair()
        claim_list = 'claim:\n  - "[[노드A]]"\n  - "[[노드B]]"'
        write(
            self.scope,
            "wiki/experiments/다중실험.md",
            "---\ntype: experiment\ntitle: \"exp\"\ncreated: 2026-06-12\n"
            f"updated: 2026-06-12\nstatus: planned\n{claim_list}\n---\n",
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)

    # ---- sources origin/derived_from (0.9.0 §2 independence metadata) ----

    def test_source_origin_and_derived_from_valid(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/sources/원출처.md",
            '---\ntype: source\ntitle: "p"\norigin: primary\n---\n',
        )
        write(
            self.scope,
            "wiki/sources/이차출처.md",
            '---\ntype: source\ntitle: "s"\norigin: secondary\n'
            'derived_from:\n  - "[[원출처]]"\n---\n',
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)

    def test_source_invalid_origin_flagged(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/sources/출처.md",
            '---\ntype: source\ntitle: "s"\norigin: tertiary\n---\n',
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["invalid"], {"origin": "tertiary"})

    # ---- allowed external wikilinks (0.9.0 scope CLAUDE.md allowlist) ----

    def test_allowed_external_wikilinks_split_from_unresolved(self):
        write(
            self.scope,
            "CLAUDE.md",
            "# Scope\n\n## 6. Toggles & Status\n\n"
            "- Allowed external wikilinks: 외부볼트노트, [[둘째허용]]\n",
        )
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(
                title="A", body="[[노드B]] [[외부볼트노트]] [[둘째허용]] [[미허용외부]]"
            ),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["allowed_external"], 2)
        self.assertEqual(
            sorted(f["target"] for f in data["findings"]["allowed_external"]),
            ["둘째허용", "외부볼트노트"],
        )
        self.assertEqual(data["counts"]["unresolved_external"], 1)
        self.assertEqual(
            data["findings"]["unresolved_external"][0]["target"], "미허용외부"
        )

    def test_no_allowlist_keeps_all_external_unresolved(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[노드B]] [[외부볼트노트]]"),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertEqual(data["counts"]["allowed_external"], 0)
        self.assertEqual(data["counts"]["unresolved_external"], 1)


if __name__ == "__main__":
    unittest.main()
