"""Tests for src/analyze/stats.py significance_label()."""
from src.analyze.stats import significance_label


class TestSignificanceLabelBonferroniNesting:
    """A star label must never be awarded to a p-value that fails the
    Bonferroni-corrected threshold (alpha/n) -- see stats.py docstring for
    the bug this fixes."""

    def test_small_n_unaffected(self):
        assert significance_label(0.0001, n=1) == "***"
        assert significance_label(0.005, n=1) == "**"
        assert significance_label(0.03, n=1) == "*"
        assert significance_label(0.5, n=1) == "ns"

    def test_p_failing_corrected_threshold_is_ns_even_if_below_fixed_thresholds(self):
        # n=28 -> corrected threshold = 0.05/28 ~= 0.00179. A p of 0.005 would
        # have been labeled "**" under the old fixed-threshold-only logic
        # despite failing the corrected bar.
        assert significance_label(0.005, n=28) == "ns"
        assert significance_label(0.003, n=28) == "ns"  # also fails 0.00179

    def test_p_clearing_corrected_threshold_still_gets_correct_tier(self):
        # n=28 -> threshold ~= 0.00179. p=0.0001 clears it and is < 0.001.
        assert significance_label(0.0001, n=28) == "***"
