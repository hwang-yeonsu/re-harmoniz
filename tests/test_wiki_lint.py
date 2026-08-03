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
        for s in ("seed", "developing", "hardened", "evergreen", "deprecated", "pruned"):
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
            f"evergreen {expected['evergreen']} · deprecated {expected['deprecated']} · "
            f"pruned {expected['pruned']} (2026-06-12)"
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
                "pruned": 0,
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

    # ---- evidence_class (0.14.0 §2/§3 class-calibrated gates) ----

    def test_evidence_class_valid_values(self):
        for cls, stem in (
            ("literature", "문헌클레임"),
            ("field", "실측클레임"),
            ("design", "설계클레임"),
        ):
            write(
                self.scope,
                f"wiki/claims/{stem}.md",
                node_text(
                    title=stem,
                    body="[[문헌클레임]] [[실측클레임]] [[설계클레임]]",
                    extra_fm=f"evidence_class: {cls}",
                ),
            )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)

    def test_evidence_class_invalid_flagged(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/claims/무효클래스.md",
            node_text(
                title="bad-class",
                body="[[노드A]]",
                extra_fm="evidence_class: anecdotal",
            ),
        )
        write(
            self.scope,
            "wiki/claims/노드C.md",
            node_text(title="C", body="[[무효클래스]]"),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/claims/무효클래스.md")
        self.assertEqual(finding["invalid"], {"evidence_class": "anecdotal"})

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

    def test_allowlist_line_with_html_comment_and_none_sentinel(self):
        # The SCOPE_CLAUDE.md template writes the toggle with a trailing HTML
        # comment; the parser must strip it, and a "(none)" value with a
        # comment must still mean an empty allowlist.
        write(
            self.scope,
            "CLAUDE.md",
            "- Allowed external wikilinks: 외부볼트노트 <!-- 의도된 볼트 링크 -->\n",
        )
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[노드B]] [[외부볼트노트]]"),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertEqual(data["counts"]["allowed_external"], 1)
        self.assertEqual(data["counts"]["unresolved_external"], 0)
        # now the "(none)" default with a comment → empty allowlist
        write(
            self.scope,
            "CLAUDE.md",
            "- Allowed external wikilinks: (none) <!-- comma-separated stems -->\n",
        )
        data = self.lint()
        self.assertEqual(data["counts"]["allowed_external"], 0)
        self.assertEqual(data["counts"]["unresolved_external"], 1)

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

    # ---- deliverable node (0.10.0 §14: non-evolving answer synthesis) ----

    def deliverable_text(self, *, question="[[중심질문]]", omit=()) -> str:
        fm = {
            "type": "deliverable",
            "title": '"답변 논지"',
            "created": "2026-07-02",
            "updated": "2026-07-02",
            "question": f'"{question}"',
        }
        lines = [f"{k}: {v}" for k, v in fm.items() if k not in omit]
        return (
            "---\n" + "\n".join(lines) + "\n---\n\n"
            "**Confidence:** medium\n\n## Answer\n[[노드A]] 결론.\n"
        )

    def test_deliverable_node_is_valid_and_scanned(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/questions/중심질문.md",
            '---\ntype: question\ntitle: "q"\nstatus: open\n---\n',
        )
        write(
            self.scope,
            "wiki/deliverables/답변.md",
            self.deliverable_text(),
        )
        data = self.lint()
        self.assertTrue(data["clean"])
        self.assertEqual(data["counts"]["pages_checked"], 4)
        self.assertEqual(data["counts"]["missing_frontmatter"], 0)
        # deliverables never enter the maturity census (§14)
        self.assertEqual(data["status_census"]["total"], 2)

    def test_deliverable_missing_required_keys(self):
        self._clean_pair()
        write(
            self.scope,
            "wiki/deliverables/답변.md",
            self.deliverable_text(omit=("question", "updated")),
        )
        data = self.lint()
        self.assertFalse(data["clean"])
        self.assertEqual(data["counts"]["missing_frontmatter"], 1)
        finding = data["findings"]["missing_frontmatter"][0]
        self.assertEqual(finding["path"], "wiki/deliverables/답변.md")
        self.assertEqual(finding["missing"], ["question", "updated"])


class ForwardLookingInNodeBodyTest(unittest.TestCase):
    """§2 — claim/mashup bodies assert what is known, never what to do next."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _pair(self, a_body: str, b_body: str = "see [[노드A]]"):
        write(self.scope, "wiki/claims/노드A.md", node_text(title="A", body=a_body))
        write(self.scope, "wiki/claims/노드B.md", node_text(title="B", body=b_body))

    def test_plan_in_claim_body_is_reported(self):
        self._pair("컷오프는 조건화됐다. 다음 진전은 결합 데이터셋 확보다. [[노드B]]")
        data = self.lint()
        found = data["findings"]["forward_looking_in_node_body"]
        self.assertEqual([f["path"] for f in found], ["wiki/claims/노드A.md"])
        self.assertEqual(found[0]["match"], "다음 진전")

    def test_line_number_is_file_relative_not_body_relative(self):
        # frontmatter is 10 lines + closing ---, then a blank line: the
        # assertion sits on file line 13, not body line 2.
        self._pair("첫 줄은 사실이다.\n다음 단계는 벤치마크다. [[노드B]]")
        found = self.lint()["findings"]["forward_looking_in_node_body"]
        path = self.scope / "wiki/claims/노드A.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        expected = next(
            i for i, ln in enumerate(lines, 1) if "다음 단계는 벤치마크다" in ln
        )
        self.assertEqual([f["line"] for f in found], [expected])

    def test_quoted_plan_is_not_reported(self):
        # a merge record citing the stale line it just retired is not the node
        # asserting a plan — quoted spans are stripped before matching
        self._pair('종전 결론("다음 진전 = 데이터 확보")은 은퇴했다. [[노드B]]')
        self.assertEqual(self.lint()["findings"]["forward_looking_in_node_body"], [])

    def test_backticked_plan_is_not_reported(self):
        self._pair("규칙 이름은 `next step` 패턴이다. [[노드B]]")
        self.assertEqual(self.lint()["findings"]["forward_looking_in_node_body"], [])

    def test_deprecated_node_is_not_reported(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(
                title="A",
                status="deprecated",
                body="다음 진전은 결합 데이터셋 확보다. [[노드B]]",
            ),
        )
        write(self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]"))
        self.assertEqual(self.lint()["findings"]["forward_looking_in_node_body"], [])

    def test_source_page_is_not_reported(self):
        # only claims/ and mashups/ evolve; sources and questions may hold plans
        self._pair("사실 진술. [[노드B]]")
        write(
            self.scope,
            "wiki/questions/질문A.md",
            "---\ntype: question\ntitle: \"q\"\ncreated: 2026-06-12\nstatus: open\n---\n\n"
            "다음 단계는 사전등록이다. [[노드A]]\n",
        )
        self.assertEqual(self.lint()["findings"]["forward_looking_in_node_body"], [])

    def test_apostrophes_do_not_swallow_the_match(self):
        # "don't ... it's" must not be treated as one quoted span
        self._pair("We don't know the next step; it's unclear. [[노드B]]")
        found = self.lint()["findings"]["forward_looking_in_node_body"]
        self.assertEqual([f["match"] for f in found], ["next step"])

    def test_warning_does_not_break_clean(self):
        self._pair("다음 진전은 벤치마크다. [[노드B]]")
        data = self.lint()
        self.assertEqual(len(data["findings"]["forward_looking_in_node_body"]), 1)
        self.assertTrue(data["clean"])


class ExperimentRetiredStatusTest(unittest.TestCase):
    """§2 — `retired`: the decision died, not the run (distinct from `abandoned`)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_retired_is_a_valid_experiment_status(self):
        write(self.scope, "wiki/claims/클레임A.md", node_text(title="A", body="[[실험A]]"))
        write(
            self.scope,
            "wiki/experiments/실험A.md",
            experiment_text(title="e", status="retired", claim="[[클레임A]]", body="[[클레임A]]"),
        )
        data = self.lint()
        self.assertEqual(data["findings"]["missing_frontmatter"], [])
        self.assertTrue(data["clean"])

    def test_unknown_experiment_status_still_rejected(self):
        write(self.scope, "wiki/claims/클레임A.md", node_text(title="A", body="[[실험A]]"))
        write(
            self.scope,
            "wiki/experiments/실험A.md",
            experiment_text(title="e", status="superseded", claim="[[클레임A]]", body="[[클레임A]]"),
        )
        data = self.lint()
        self.assertEqual(len(data["findings"]["missing_frontmatter"]), 1)
        self.assertFalse(data["clean"])


class DecisionAtStakeTest(unittest.TestCase):
    """§12 decision gate — live pre-registrations must name a decision (warning)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _exp(self, status: str, body: str):
        write(self.scope, "wiki/claims/클레임A.md", node_text(title="A", body="[[실험A]]"))
        write(
            self.scope,
            "wiki/experiments/실험A.md",
            experiment_text(title="e", status=status, claim="[[클레임A]]", body=body),
        )

    def test_planned_without_section_is_reported(self):
        self._exp("planned", "## Hypothesis\nH. [[클레임A]]")
        found = self.lint()["findings"]["experiment_missing_decision_at_stake"]
        self.assertEqual([f["path"] for f in found], ["wiki/experiments/실험A.md"])

    def test_planned_with_section_is_clean(self):
        self._exp(
            "planned",
            "## Decision at stake\n- CONFIRM → ship it\n- REFUTE → redesign\n\n[[클레임A]]",
        )
        self.assertEqual(
            self.lint()["findings"]["experiment_missing_decision_at_stake"], []
        )

    def test_template_trailing_comment_is_tolerated(self):
        # the §2 experiment template annotates the heading with an HTML comment;
        # a node copied from it verbatim does name a decision
        self._exp(
            "planned",
            "## Decision at stake            <!-- §12 decision gate, pre-registered -->\n"
            "- CONFIRM → ship it\n- REFUTE → redesign\n\n[[클레임A]]",
        )
        self.assertEqual(
            self.lint()["findings"]["experiment_missing_decision_at_stake"], []
        )

    def test_legacy_imported_node_is_not_reported(self):
        # additive change: pre-registrations that already ran stay valid
        self._exp("imported", "## Hypothesis\nH. [[클레임A]]")
        self.assertEqual(
            self.lint()["findings"]["experiment_missing_decision_at_stake"], []
        )

    def test_missing_section_is_a_warning_not_clean_breaking(self):
        self._exp("planned", "## Hypothesis\nH. [[클레임A]]")
        data = self.lint()
        self.assertEqual(len(data["findings"]["experiment_missing_decision_at_stake"]), 1)
        self.assertTrue(data["clean"])


# ---- §10 declared decisions + §2 `serves:` — the pruning baseline (1.0.0) ----


def scope_claude_md(*rows: str, goal: str = "목표 한 줄", heading: bool = True) -> str:
    """A scope CLAUDE.md, optionally declaring the §10 goal/decision block.

    `rows` are table rows like `| D1 | … | open |`. `heading=False` writes a
    CLAUDE.md with no decision block at all (the pre-1.0.0 shape).
    """
    head = "# Research_X — Research Scope\n\n## 1. Purpose & Boundaries\n\n한 단락.\n\n"
    tail = "## 2. Metadata\n\n- Code workspace path(s): `/tmp/ws`\n"
    if not heading:
        return head + tail
    block = (
        "### Goal & Open Decisions\n\n"
        f"**Goal:** {goal}\n\n"
        "| ID | Decision to settle | Status |\n"
        "|---|---|---|\n" + "".join(f"{r}\n" for r in rows) + "\n"
    )
    return head + block + tail


class DeclaredDecisionsTest(unittest.TestCase):
    """§10: the scope declares the decisions it exists to settle; §2 `serves:`
    binds a node to them. Without that binding there is no relevance signal to
    prune against — every finding here is a warning, so `clean` is untouched."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _pair(self, *, a_fm="", b_fm=""):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[노드B]]", extra_fm=a_fm),
        )
        write(
            self.scope,
            "wiki/claims/노드B.md",
            node_text(title="B", body="[[노드A]]", extra_fm=b_fm),
        )

    def test_declared_decisions_are_parsed_and_split_by_status(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md(
                "| D1 | 8-bit로 32-bit를 대체할 수 있는가 | open |",
                "| D2 | 이미 정해진 것 | settled |",
            ),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D2"]')
        data = self.lint()
        self.assertEqual(
            data["decisions"],
            {"declared": 2, "open": ["D1"], "settled": ["D2"], "superseded": []},
        )

    def test_table_header_and_separator_rows_are_not_decisions(self):
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        self.assertEqual(self.lint()["decisions"]["declared"], 1)

    def test_rows_after_the_block_ends_are_not_decisions(self):
        # a D-shaped row in a LATER section must not leak into the decision set
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 하나 | open |")
            + "\n## 5. Seed Source Candidates\n\n| D9 | 시드 표의 오해 | open |\n",
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["decisions"]["open"], ["D1"])

    def test_unrecognized_decision_status_counts_as_open(self):
        # conservative on purpose: an unrecognized status must never silently
        # retire a decision, because that would let a node be pruned against a
        # decision nobody actually closed
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 오타 상태 | opne |", "| D2 | 닫힘 | settled |"),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D2"]')
        data = self.lint()
        self.assertEqual(data["decisions"]["open"], ["D1"])
        self.assertEqual(data["decisions"]["settled"], ["D2"])

    def test_missing_decision_block_is_reported_when_nodes_exist(self):
        write(self.scope, "CLAUDE.md", scope_claude_md(heading=False))
        self._pair()
        data = self.lint()
        self.assertEqual(data["counts"]["no_decisions_declared"], 1)
        self.assertEqual(data["decisions"]["declared"], 0)
        self.assertTrue(data["clean"])

    def test_missing_decision_block_is_quiet_on_an_empty_scope(self):
        (self.scope / "wiki" / "claims").mkdir(parents=True)
        data = self.lint()
        self.assertEqual(data["counts"]["no_decisions_declared"], 0)

    def test_serves_resolving_to_a_declared_decision_is_quiet(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 하나 | open |", "| D2 | 둘 | open |"),
        )
        self._pair(a_fm='serves: ["D1", "D2"]', b_fm='serves: ["D2"]')
        data = self.lint()
        self.assertEqual(data["counts"]["unknown_serves_target"], 0)
        self.assertEqual(data["counts"]["unassigned_claims"], 0)

    def test_serves_naming_an_undeclared_decision_is_reported(self):
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        self._pair(a_fm='serves: ["D1", "D9"]', b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["counts"]["unknown_serves_target"], 1)
        finding = data["findings"]["unknown_serves_target"][0]
        self.assertEqual(finding["path"], "wiki/claims/노드A.md")
        self.assertEqual(finding["target"], "D9")
        self.assertTrue(data["clean"])

    def test_serves_block_list_form_parses(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 하나 | open |", "| D2 | 둘 | open |"),
        )
        self._pair(a_fm="serves:\n  - D1\n  - D2", b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["counts"]["unknown_serves_target"], 0)
        self.assertEqual(data["counts"]["unassigned_claims"], 0)

    def test_unassigned_claim_is_counted_when_decisions_are_declared(self):
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        self._pair(a_fm='serves: ["D1"]')  # 노드B carries no serves:
        data = self.lint()
        self.assertEqual(data["counts"]["unassigned_claims"], 1)
        self.assertEqual(
            data["findings"]["unassigned_claims"], ["wiki/claims/노드B.md"]
        )
        self.assertTrue(data["clean"])

    def test_empty_serves_list_counts_as_unassigned(self):
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        self._pair(a_fm='serves: ["D1"]', b_fm="serves: []")
        self.assertEqual(self.lint()["counts"]["unassigned_claims"], 1)

    def test_unassigned_is_not_counted_without_declared_decisions(self):
        write(self.scope, "CLAUDE.md", scope_claude_md(heading=False))
        self._pair()
        data = self.lint()
        self.assertEqual(data["counts"]["unassigned_claims"], 0)
        self.assertEqual(data["counts"]["unknown_serves_target"], 0)

    def test_terminal_nodes_are_exempt_from_unassigned(self):
        # deprecated (collapsed) and pruned (goal-irrelevant) have left the graph
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        write(
            self.scope,
            "wiki/claims/살아있는노드.md",
            node_text(title="live", body="[[버려진노드]] [[잘린노드]]", extra_fm='serves: ["D1"]'),
        )
        write(
            self.scope,
            "wiki/claims/버려진노드.md",
            node_text(title="dep", status="deprecated", body="[[살아있는노드]]"),
        )
        write(
            self.scope,
            "wiki/claims/잘린노드.md",
            node_text(title="pruned", status="pruned", body="[[살아있는노드]]"),
        )
        data = self.lint()
        self.assertEqual(data["counts"]["unassigned_claims"], 0)

    def test_sources_and_questions_are_never_unassigned(self):
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 하나 | open |"))
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        write(
            self.scope, "wiki/sources/출처.md", '---\ntype: source\ntitle: "s"\n---\n'
        )
        write(
            self.scope,
            "wiki/questions/질문.md",
            '---\ntype: question\ntitle: "q"\nstatus: open\n---\n',
        )
        self.assertEqual(self.lint()["counts"]["unassigned_claims"], 0)

    def test_no_claude_md_at_all_is_quiet_about_serves(self):
        self._pair()
        data = self.lint()
        self.assertEqual(data["decisions"]["declared"], 0)
        self.assertEqual(data["counts"]["unassigned_claims"], 0)
        self.assertTrue(data["clean"])


class PrunedStatusTest(unittest.TestCase):
    """§3: `pruned` is a terminal status distinct from `deprecated` — the node
    was cut for serving no open decision, NOT for collapsing under refutation.
    Conflating the two would erase the signal the loop steers on."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_pruned_is_a_valid_claim_status(self):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", status="pruned", body="[[노드B]]"),
        )
        write(
            self.scope, "wiki/claims/노드B.md", node_text(title="B", body="[[노드A]]")
        )
        data = self.lint()
        self.assertEqual(data["findings"]["missing_frontmatter"], [])
        self.assertTrue(data["clean"])

    def test_pruned_node_is_orphan_exempt(self):
        # nothing links to it, exactly as with deprecated (§3: it left the graph)
        write(
            self.scope,
            "wiki/claims/잘린노드.md",
            node_text(title="p", status="pruned", body="본문."),
        )
        data = self.lint()
        self.assertEqual(data["findings"]["orphans"], [])
        self.assertTrue(data["clean"])

    def test_pruned_node_is_forward_looking_exempt(self):
        write(
            self.scope,
            "wiki/claims/잘린노드.md",
            node_text(
                title="p", status="pruned", body="다음 단계는 이걸 다시 보는 것."
            ),
        )
        self.assertEqual(
            self.lint()["findings"]["forward_looking_in_node_body"], []
        )

    def test_census_counts_pruned_separately_from_deprecated(self):
        for stem, status in (
            ("살아있는노드", "seed"),
            ("버려진노드", "deprecated"),
            ("잘린노드", "pruned"),
        ):
            write(
                self.scope,
                f"wiki/claims/{stem}.md",
                node_text(title=stem, status=status, body="[[살아있는노드]]"),
            )
        census = self.lint()["status_census"]
        self.assertEqual(census["total"], 3)
        self.assertEqual(census["deprecated"], 1)
        self.assertEqual(census["pruned"], 1)
        self.assertEqual(census["seed"], 1)

    def test_pruned_is_rejected_on_an_experiment_node(self):
        # experiments keep their own lifecycle (§2) — `pruned` is a maturity value
        write(
            self.scope,
            "wiki/experiments/실험.md",
            experiment_text(status="pruned", claim="[[노드A]]"),
        )
        data = self.lint()
        self.assertEqual(len(data["findings"]["missing_frontmatter"]), 1)
        self.assertEqual(
            data["findings"]["missing_frontmatter"][0]["invalid"]["status"], "pruned"
        )


class PruneRestorePointTest(unittest.TestCase):
    """§3 calls pruning **reversible** — "flip the node back to the status it
    held". Nothing recorded that status, so the promise was only executable by
    reading git. The prune line therefore carries the pre-prune status:
    `Pruned from <status>: <reason> (YYYY-MM-DD)`.

    A warning, not an error: it never breaks `clean`, and legacy `deprecated`
    nodes are untouched — deprecation is a verdict on the claim and is not
    meant to be undone."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _pruned(self, body: str):
        write(
            self.scope,
            "wiki/claims/잘린노드.md",
            node_text(title="p", status="pruned", body=body),
        )

    def test_pruned_without_a_restore_point_is_reported(self):
        self._pruned("Pruned: all served decisions settled (2026-08-03)")
        data = self.lint()
        self.assertEqual(data["counts"]["prune_without_restore_point"], 1)
        self.assertEqual(
            data["findings"]["prune_without_restore_point"][0]["path"],
            "wiki/claims/잘린노드.md",
        )
        self.assertTrue(data["clean"])

    def test_pruned_with_a_restore_point_is_quiet(self):
        self._pruned("Pruned from hardened: all served decisions settled (2026-08-03)")
        self.assertEqual(self.lint()["counts"]["prune_without_restore_point"], 0)

    def test_restore_point_must_name_a_real_maturity_status(self):
        # "Pruned from wherever" restores nothing — the point is a status to
        # flip back to, so an unrecognized word is the same gap as no word
        self._pruned("Pruned from 어딘가: 이유 (2026-08-03)")
        self.assertEqual(self.lint()["counts"]["prune_without_restore_point"], 1)

    def test_restore_point_is_found_anywhere_in_the_body(self):
        self._pruned(
            "# 제목\n\n본문은 그대로 남는다.\n\n"
            "Pruned from developing: 미배정 (2026-08-03)\n"
        )
        self.assertEqual(self.lint()["counts"]["prune_without_restore_point"], 0)

    def test_deprecated_needs_no_restore_point(self):
        write(
            self.scope,
            "wiki/claims/버려진노드.md",
            node_text(title="d", status="deprecated", body="총체적 붕괴."),
        )
        self.assertEqual(self.lint()["counts"]["prune_without_restore_point"], 0)

    def test_a_terminal_restore_point_is_not_a_restore_point(self):
        # flipping back to `pruned`/`deprecated` restores nothing
        self._pruned("Pruned from pruned: 이유 (2026-08-03)")
        self.assertEqual(self.lint()["counts"]["prune_without_restore_point"], 1)


class DecisionLifecycleTest(unittest.TestCase):
    """§1: a declared decision can stop being the right question — the branch
    was reframed, split, or made moot — which is neither `open` nor `settled`.

    `superseded` is that third terminal state. Its row **stays in the table**,
    which is what makes ID reuse impossible: a reused `D1` shows up as a
    duplicate row, and the linter says so."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _pair(self, *, a_fm="", b_fm=""):
        write(
            self.scope,
            "wiki/claims/노드A.md",
            node_text(title="A", body="[[노드B]]", extra_fm=a_fm),
        )
        write(
            self.scope,
            "wiki/claims/노드B.md",
            node_text(title="B", body="[[노드A]]", extra_fm=b_fm),
        )

    def test_superseded_is_neither_open_nor_settled(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md(
                "| D1 | 질문 자체가 바뀜 → D4 | superseded |",
                "| D4 | 다시 쓴 결정 | open |",
            ),
        )
        self._pair(a_fm='serves: ["D4"]', b_fm='serves: ["D4"]')
        data = self.lint()
        self.assertEqual(data["decisions"]["open"], ["D4"])
        self.assertEqual(data["decisions"]["settled"], [])
        self.assertEqual(data["decisions"]["superseded"], ["D1"])
        self.assertEqual(data["decisions"]["declared"], 2)

    def test_serves_pointing_at_a_superseded_decision_still_resolves(self):
        # the ID is still declared, so this is a re-binding job (critique), not
        # the "names no decision at all" fault `unknown_serves_target` reports
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md(
                "| D1 | 대체됨 → D4 | superseded |", "| D4 | 후속 | open |"
            ),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D4"]')
        data = self.lint()
        self.assertEqual(data["counts"]["unknown_serves_target"], 0)
        self.assertEqual(data["counts"]["stale_serves_target"], 1)
        finding = data["findings"]["stale_serves_target"][0]
        self.assertEqual(finding["path"], "wiki/claims/노드A.md")
        self.assertEqual(finding["target"], "D1")
        self.assertTrue(data["clean"])

    def test_a_typo_still_reads_as_open_not_as_superseded(self):
        # the §1 guarantee that an unrecognized status can never retire a
        # decision survives the enum gaining a third member
        write(self.scope, "CLAUDE.md", scope_claude_md("| D1 | 오타 | supersded |"))
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["decisions"]["open"], ["D1"])
        self.assertEqual(data["decisions"]["superseded"], [])

    def test_duplicate_decision_id_is_reported(self):
        # the ID-reuse signal: D1 was retired, its row deleted, and a new
        # decision took the name — every legacy `serves: D1` now points at
        # something it was never about
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 원래 결정 | superseded |", "| D1 | 재사용 | open |"),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["counts"]["duplicate_decision_id"], 1)
        self.assertEqual(data["findings"]["duplicate_decision_id"][0]["id"], "D1")
        self.assertTrue(data["clean"])

    def test_duplicate_id_keeps_only_its_first_row_and_is_counted_once(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 첫 행 | open |", "| D1 | 둘째 행 | settled |"),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D1"]')
        data = self.lint()
        self.assertEqual(data["decisions"]["declared"], 1)
        self.assertEqual(data["decisions"]["open"], ["D1"])
        self.assertEqual(data["decisions"]["settled"], [])

    def test_distinct_ids_are_not_duplicates(self):
        write(
            self.scope,
            "CLAUDE.md",
            scope_claude_md("| D1 | 하나 | open |", "| D2 | 둘 | settled |"),
        )
        self._pair(a_fm='serves: ["D1"]', b_fm='serves: ["D2"]')
        self.assertEqual(self.lint()["counts"]["duplicate_decision_id"], 0)


class ConditionalRecommendationTest(unittest.TestCase):
    """§2 node-body hygiene bans *expiring plans*, not engineering conclusions.
    A recommendation bound to a condition is an assertion — gradeable by the
    §5 refuters — and must survive the linter."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def _claim(self, body: str):
        write(self.scope, "wiki/claims/노드A.md", node_text(title="A", body=body))

    def test_conditional_recommendation_is_not_flagged(self):
        self._claim(
            "65B 이하 규모에서는 8-bit Adam을 선택한다. 그 위에서는 32-bit를 유지한다."
        )
        self.assertEqual(
            self.lint()["findings"]["forward_looking_in_node_body"], []
        )

    def test_english_conditional_recommendation_is_not_flagged(self):
        self._claim("Prefer 8-bit Adam when the model is at or below 65B.")
        self.assertEqual(
            self.lint()["findings"]["forward_looking_in_node_body"], []
        )

    def test_bare_plan_is_still_flagged(self):
        # the falsifiable counterpart: remove the rule and THIS test fails
        self._claim("다음 단계는 65B 초과 구간을 측정하는 것.")
        findings = self.lint()["findings"]["forward_looking_in_node_body"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["match"], "다음 단계")


class LegacyScopeCompatibilityTest(unittest.TestCase):
    """1.0.0's load-bearing promise: a scope written against 0.15.0 — no decision
    block, no `serves:`, no `pruned` — stays valid with no migration.

    This is the regression test for the whole additive design. If any 1.0.0 rule
    ever breaks `clean` on a pre-1.0.0 scope, existing users' wikis start failing
    Phase E lint on a version bump they did not ask for."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scope = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self._build_legacy_scope()

    def _build_legacy_scope(self):
        # a 0.15.0 scope CLAUDE.md: no `Goal & Open Decisions` block at all
        write(
            self.scope,
            "CLAUDE.md",
            "# Research_legacy\n\n## 1. Purpose & Boundaries\n\n한 단락.\n\n"
            "## 6. Toggles & Status\n\n- Allowed external wikilinks: 볼트노트\n",
        )
        for stem, other in (("구주장A", "구주장B"), ("구주장B", "구주장A")):
            write(
                self.scope,
                f"wiki/claims/{stem}.md",
                node_text(
                    title=stem,
                    status="developing",
                    confidence="medium",
                    generation="3",
                    body=f"본문. [[{other}]] [[볼트노트]]",
                    extra_fm='sources: ["[[구출처]]"]\nevidence_class: literature',
                ),
            )
        write(
            self.scope,
            "wiki/sources/구출처.md",
            '---\ntype: source\ntitle: "s"\norigin: primary\n---\n요약.\n',
        )
        # pre-0.9.0 convention: a question carrying a maturity value
        write(
            self.scope,
            "wiki/questions/구질문.md",
            '---\ntype: question\ntitle: "q"\nstatus: seed\n---\n예전 status.\n',
        )
        write(
            self.scope,
            "wiki/experiments/구실험.md",
            experiment_text(status="imported", claim="[[구주장A]]", body="## Hypothesis\nH.\n"),
        )
        write(
            self.scope,
            "wiki/index.md",
            "# Index\n\n**Census:** 2 nodes · seed 0 · developing 2 · hardened 0 · "
            "evergreen 0 · deprecated 0 (2026-06-12)\n",
        )
        write(
            self.scope,
            "wiki/meta/evolution/E0001.md",
            '---\ntype: meta\ntitle: "E0001"\ncreated: 2026-06-12\nsession: E0001\n---\n# E0001\n',
        )
        # §7 schema v2: no decision counters, no `trailing` rows
        write(
            self.scope,
            "wiki/meta/evolution/E0001.eval.json",
            json.dumps(
                {
                    "pass": True,
                    "score": 0.8,
                    "checks": {"lint_clean": True, "generation_progress": 2},
                    "stagnation": {"trailing": [], "verdict": "continue"},
                }
            ),
        )

    def lint(self) -> dict:
        proc = run_lint(self.scope)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_legacy_scope_still_lints_clean(self):
        data = self.lint()
        self.assertTrue(data["clean"], data["findings"])
        breaking = (
            "missing_frontmatter",
            "dead_wikilinks",
            "orphans",
            "contradictions",
            "duplicate_stems",
        )
        self.assertEqual(
            {k: data["counts"][k] for k in breaking}, {k: 0 for k in breaking}
        )

    def test_the_only_new_signal_is_the_undeclared_goal(self):
        counts = self.lint()["counts"]
        self.assertEqual(counts["no_decisions_declared"], 1)
        # with no decisions declared there is nothing to be unassigned against:
        # firing here would flood every legacy scope with meaningless warnings
        self.assertEqual(counts["unassigned_claims"], 0)
        self.assertEqual(counts["unknown_serves_target"], 0)

    def test_pre_existing_tolerances_still_hold(self):
        counts = self.lint()["counts"]
        self.assertEqual(counts["legacy_question_status"], 1)  # §2 question legacy
        self.assertEqual(counts["allowed_external"], 2)  # CLAUDE.md allowlist
        self.assertEqual(counts["census_drift"], 0)  # census line still matches
        self.assertEqual(counts["eval_findings"], 0)  # v2 eval still readable

    def test_census_gains_a_pruned_bucket_without_disturbing_legacy_counts(self):
        census = self.lint()["status_census"]
        self.assertEqual(census["developing"], 2)
        self.assertEqual(census["total"], 2)
        self.assertEqual(census["pruned"], 0)


if __name__ == "__main__":
    unittest.main()
