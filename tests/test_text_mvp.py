import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from blitz_engine import BlitzEngine
from blitz_engine.cli import main


class TextMVPTests(unittest.TestCase):
    def setUp(self):
        self.engine = BlitzEngine(modalities=["linguistic"])
        self.session = self.engine.new_session(
            baseline_texts=[
                "I drove to work and grabbed coffee before the meeting.",
                "My usual breakfast is eggs, toast, and tea at home.",
                "Last weekend I cleaned the apartment and watched a movie.",
                "I usually walk to the store in the afternoon for groceries.",
                "My morning routine starts with stretching and checking messages.",
            ],
            baseline_latencies_ms=[120, 140, 100, 110, 130],
            baseline_duration_s=120,
            consent=True,
            use_case="research",
            jurisdiction="CA-US",
        )

    def test_session_returns_structured_output(self):
        result = self.session.analyze_text(
            response_text="Honestly, I really do not know, um, I was basically with someone at that place.",
            question="Where were you Tuesday night?",
            response_latency_ms=900,
        )

        self.assertGreaterEqual(result.risk_score, 0.0)
        self.assertLessEqual(result.risk_score, 1.0)
        self.assertTrue(result.top_cues)
        self.assertEqual(result.quality_flags["input_mode"], "text")
        self.assertTrue(result.compliance["not_for_sole_decision"])

    def test_missing_consent_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.new_session(
                baseline_texts=["Neutral baseline text"] * 5,
                consent=False,
                use_case="research",
                jurisdiction="CA-US",
            )

    def test_cli_writes_json_report(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            baseline = tmp / "baseline.txt"
            response = tmp / "response.txt"
            output = tmp / "report.json"

            baseline.write_text(
                "\n".join([
                    "I drove to work and grabbed coffee before the meeting.",
                    "My usual breakfast is eggs, toast, and tea at home.",
                    "Last weekend I cleaned the apartment and watched a movie.",
                    "I usually walk to the store in the afternoon for groceries.",
                    "My morning routine starts with stretching and checking messages.",
                ])
            )
            response.write_text("Honestly, I really do not know, um, I was basically with someone at that place.")

            exit_code = main([
                "analyze-text",
                "--baseline-file", str(baseline),
                "--response-file", str(response),
                "--question", "Where were you Tuesday night?",
                "--response-latency-ms", "900",
                "--output", str(output),
            ])

            self.assertEqual(exit_code, 0)
            payload = output.read_text()
            self.assertIn('"risk_score"', payload)
            self.assertIn('"session_id"', payload)


if __name__ == "__main__":
    unittest.main()
