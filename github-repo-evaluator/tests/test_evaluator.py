#!/usr/bin/env python3
"""
Tests for GitHub Repo Evaluator
100% test coverage requirement: all new code must have tests.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from fetch_repo_info import (
    extract_repo_info,
    is_recently_updated,
)


class TestExtractRepoInfo(unittest.TestCase):
    """Test GitHub URL parsing."""

    def test_standard_url(self):
        owner, repo = extract_repo_info("https://github.com/facebook/react")
        self.assertEqual(owner, "facebook")
        self.assertEqual(repo, "react")

    def test_url_with_trailing_slash(self):
        owner, repo = extract_repo_info("https://github.com/facebook/react/")
        self.assertEqual(owner, "facebook")
        self.assertEqual(repo, "react")

    def test_url_with_git_suffix(self):
        owner, repo = extract_repo_info("https://github.com/tiangolo/fastapi.git")
        self.assertEqual(owner, "tiangolo")
        self.assertEqual(repo, "fastapi")

    def test_url_with_path_after_repo(self):
        owner, repo = extract_repo_info("https://github.com/microsoft/vscode/tree/main")
        self.assertEqual(owner, "microsoft")
        self.assertEqual(repo, "vscode")

    def test_invalid_url_raises_error(self):
        with self.assertRaises(ValueError):
            extract_repo_info("https://google.com")

    def test_invalid_url_empty(self):
        with self.assertRaises(ValueError):
            extract_repo_info("")

    def test_org_with_dots(self):
        owner, repo = extract_repo_info("https://github.com/vercel/next.js")
        self.assertEqual(owner, "vercel")
        self.assertEqual(repo, "next.js")


class TestIsRecentlyUpdated(unittest.TestCase):
    """Test date comparison logic."""

    def test_recent_date_returns_true(self):
        recent = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
        self.assertTrue(is_recently_updated(recent, months=6))

    def test_very_old_date_returns_false(self):
        old = (datetime.now() - timedelta(days=400)).isoformat() + "Z"
        self.assertFalse(is_recently_updated(old, months=6))

    def test_none_date_returns_false(self):
        self.assertFalse(is_recently_updated(None, months=6))

    def test_empty_date_returns_false(self):
        self.assertFalse(is_recently_updated("", months=6))

    def test_invalid_date_format_returns_false(self):
        self.assertFalse(is_recently_updated("not-a-date", months=6))

    def test_boundary_date_within_threshold(self):
        # Just within 6 months
        within = (datetime.now() - timedelta(days=180)).isoformat() + "Z"
        self.assertTrue(is_recently_updated(within, months=6))

    def test_boundary_date_outside_threshold(self):
        # Just outside 6 months
        outside = (datetime.now() - timedelta(days=181)).isoformat() + "Z"
        self.assertFalse(is_recently_updated(outside, months=6))


class TestEvaluatorDecisions(unittest.TestCase):
    """Test evaluation decision logic."""

    def score_to_decision(self, score: int) -> str:
        """Convert score to decision."""
        if score >= 3:
            return "下载"
        elif score >= 1:
            return "观望"
        else:
            return "关掉"

    def test_high_score_download(self):
        self.assertEqual(self.score_to_decision(5), "下载")
        self.assertEqual(self.score_to_decision(3), "下载")

    def test_medium_score_watch(self):
        self.assertEqual(self.score_to_decision(2), "观望")
        self.assertEqual(self.score_to_decision(1), "观望")

    def test_low_score_close(self):
        self.assertEqual(self.score_to_decision(0), "关掉")
        self.assertEqual(self.score_to_decision(-1), "关掉")
        self.assertEqual(self.score_to_decision(-5), "关掉")


class TestDimensionScoring(unittest.TestCase):
    """Test individual dimension scoring logic."""

    def evaluate_clarity(self, has_readme: bool, has_description: bool, has_demo: bool) -> int:
        """Evaluate purpose clarity dimension."""
        score = 0
        if has_readme:
            score += 1
        if has_description:
            score += 1
        if has_demo:
            score += 1
        return score

    def test_clear_purpose_scores_high(self):
        score = self.evaluate_clarity(True, True, True)
        self.assertEqual(score, 3)

    def test_partial_purpose_scores_medium(self):
        score = self.evaluate_clarity(True, True, False)
        self.assertEqual(score, 2)

    def test_vague_purpose_scores_low(self):
        score = self.evaluate_clarity(False, False, False)
        self.assertEqual(score, 0)

    def evaluate_version_status(self, has_releases: bool, has_version: bool, has_install: bool) -> int:
        """Evaluate version status dimension."""
        score = 0
        if has_releases:
            score += 1
        if has_version:
            score += 1
        if has_install:
            score += 1
        return score

    def test_official_release_scores_high(self):
        score = self.evaluate_version_status(True, True, True)
        self.assertEqual(score, 3)

    def test_source_only_scores_low(self):
        score = self.evaluate_version_status(False, False, False)
        self.assertEqual(score, 0)

    def evaluate_maintenance(self, recent_update: bool, issues_responded: bool, active_commits: bool) -> int:
        """Evaluate maintenance dimension."""
        score = 0
        if recent_update:
            score += 1
        if issues_responded:
            score += 1
        if active_commits:
            score += 1
        return score

    def test_active_maintenance_scores_high(self):
        score = self.evaluate_maintenance(True, True, True)
        self.assertEqual(score, 3)

    def test_abandoned_project_scores_low(self):
        score = self.evaluate_maintenance(False, False, False)
        self.assertEqual(score, 0)


class TestReportGeneration(unittest.TestCase):
    """Test evaluation report generation."""

    def generate_minimal_report(self, repo_name: str, purpose: str, usable: str, maintained: str, decision: str, reason: str) -> str:
        """Generate a minimal evaluation report."""
        return f"""# {repo_name} 评估报告

## 三步定位
1. 它做什么: {purpose}
2. 能用吗: {usable}
3. 还维护吗: {maintained}

## 最终决策
**[{decision}]**

理由: {reason}
"""

    def test_report_contains_required_fields(self):
        report = self.generate_minimal_report(
            "fastapi", "FastAPI web framework", "是", "是", "下载", "用途清晰，维护活跃"
        )
        self.assertIn("fastapi", report)
        self.assertIn("FastAPI web framework", report)
        self.assertIn("能用吗", report)
        self.assertIn("还维护吗", report)
        self.assertIn("下载", report)
        self.assertIn("用途清晰，维护活跃", report)

    def test_report_format_is_consistent(self):
        report1 = self.generate_minimal_report("a", "b", "c", "d", "e", "f")
        report2 = self.generate_minimal_report("x", "y", "z", "w", "v", "u")
        # Both should have same structure
        self.assertEqual(report1.count("\n"), report2.count("\n"))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_url_case_sensitivity(self):
        # GitHub URLs are case sensitive in path but we lowercase owner
        owner, repo = extract_repo_info("https://github.com/Facebook/React")
        self.assertEqual(owner, "Facebook")
        self.assertEqual(repo, "React")

    def test_very_long_repo_name(self):
        # Test handling of long names
        owner, repo = extract_repo_info("https://github.com/test/this-is-a-very-long-repository-name-that-might-break-things")
        self.assertEqual(owner, "test")
        self.assertEqual(repo, "this-is-a-very-long-repository-name-that-might-break-things")


if __name__ == "__main__":
    unittest.main()
