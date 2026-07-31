from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_benchmark_is_deterministic_and_balanced(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            subprocess.run([sys.executable, str(ROOT / "benchmark/generate_benchmark.py"), "--output", first], check=True)
            subprocess.run([sys.executable, str(ROOT / "benchmark/generate_benchmark.py"), "--output", second], check=True)
            one = json.loads((Path(first) / "summary.json").read_text())
            two = json.loads((Path(second) / "summary.json").read_text())
            self.assertEqual(one, two)
            self.assertEqual(one["total"], 450)
            self.assertEqual(one["splits"]["confirmatory"], 240)
            self.assertEqual(one["splits"]["out-of-distribution"], 90)
            self.assertEqual(one["labels"], {"SAFE": 225, "UNSAFE": 225})

    def test_baselines_emit_one_row_per_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "benchmark"
            normalized = root / "normalized"
            subprocess.run([sys.executable, str(ROOT / "benchmark/generate_benchmark.py"), "--output", str(benchmark)], check=True)
            subprocess.run([
                sys.executable, str(ROOT / "baselines/run_baselines.py"),
                "--benchmark-root", str(benchmark), "--output-dir", str(normalized)
            ], check=True)
            for path in normalized.glob("*.jsonl"):
                self.assertEqual(len(path.read_text().splitlines()), 450)

    def test_gitleaks_adapter_maps_file_to_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({
                "case_id": "c1", "split": "pilot", "relative_path": "cases/pilot/c1.txt"
            }) + "\n")
            raw = root / "raw.json"
            raw.write_text(json.dumps([{"File": "generated/benchmark/cases/pilot/c1.txt"}]))
            output = root / "output.jsonl"
            subprocess.run([
                sys.executable, str(ROOT / "adapters/normalize_results.py"),
                "--tool", "gitleaks", "--raw", str(raw),
                "--manifest", str(manifest), "--output", str(output)
            ], check=True)
            row = json.loads(output.read_text())
            self.assertEqual(row["normalized_action"], "BLOCK")
            self.assertEqual(row["finding_count"], 1)

    def test_metrics_pipeline_with_synthetic_normalized_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "benchmark"
            normalized = root / "normalized"
            metrics = root / "metrics.json"
            subprocess.run([sys.executable, str(ROOT / "benchmark/generate_benchmark.py"), "--output", str(benchmark)], check=True)
            subprocess.run([sys.executable, str(ROOT / "baselines/run_baselines.py"), "--benchmark-root", str(benchmark), "--output-dir", str(normalized)], check=True)
            baseline_rows = [json.loads(line) for line in (normalized / "keyword-regex-baseline.jsonl").read_text().splitlines()]
            for tool in ("gitleaks", "trufflehog", "detect-secrets"):
                rows = [{**row, "tool": tool} for row in baseline_rows]
                (normalized / f"{tool}.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
            subprocess.run([sys.executable, str(ROOT / "analysis/compute_metrics.py"), "--manifest", str(benchmark / "manifest.jsonl"), "--results-dir", str(normalized), "--output", str(metrics)], check=True)
            result = json.loads(metrics.read_text())
            self.assertIn("threshold_evaluation", result)
            self.assertEqual(result["primary_analysis"]["gitleaks"]["bootstrap"]["attack_pass_through_rate_reduction"], 0.0)


if __name__ == "__main__":
    unittest.main()
