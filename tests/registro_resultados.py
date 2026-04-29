"""
Results logger for audit and statistics.
Writes test results to JSON files for later analysis.
"""
import json
import os
from datetime import datetime
from typing import Any


class ResultsLogger:
    def __init__(self, output_dir: str = "logs/test-results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def log_result(self, test_name: str, params: dict, result: dict):
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "test_name": test_name,
            "params": params,
            "result": result
        }
        filename = f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return filepath

    def log_batch(self, test_name: str, params: dict, results: list[dict]):
        for result in results:
            self.log_result(test_name, params, result)

    def load_results(self, test_name: str = None) -> list[dict]:
        results = []
        for filename in os.listdir(self.output_dir):
            if test_name and not filename.startswith(test_name):
                continue
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    results.append(json.loads(line))
        return results
