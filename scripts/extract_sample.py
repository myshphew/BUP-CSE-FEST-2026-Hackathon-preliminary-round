"""Export an existing official input and reference response without rewriting the pack."""

import argparse
import json
from pathlib import Path

from scripts.evaluate_samples import SAMPLE_PATH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=int, choices=range(1, 11), default=1)
    parser.add_argument("--directory", type=Path, default=Path("output"))
    args = parser.parse_args()
    case = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))["cases"][args.index - 1]
    args.directory.mkdir(parents=True, exist_ok=True)
    for key, name in [("input", "request.json"), ("expected_output", "reference-response.json")]:
        target = args.directory / name
        target.write_text(json.dumps(case[key], indent=2) + "\n", encoding="utf-8")
        print(target)


if __name__ == "__main__":
    main()
