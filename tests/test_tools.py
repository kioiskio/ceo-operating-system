"""Tests for CEO Operating System tools (stdlib only)."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


class TestEquityCalc(unittest.TestCase):
    def test_example_exits_zero(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS / "equity-calculator" / "equity_calc.py"), "-e"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("CAP TABLE", r.stdout)


class TestSaasHealth(unittest.TestCase):
    def test_example_exits_zero(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS / "saas-metrics" / "saas_health.py"), "-e"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("SaaS METRICS HEALTH REPORT", r.stdout)


class TestPitchScorer(unittest.TestCase):
    def test_example_exits_zero(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS / "pitch-deck-scorer" / "scorer.py"), "-e"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("PITCH DECK SCORECARD", r.stdout)


if __name__ == "__main__":
    unittest.main()
