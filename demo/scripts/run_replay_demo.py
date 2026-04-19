from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.utils.caching import ensure_dir, latest_json
from demo.utils.visualize_compare import save_compare_figure
from demo.utils.visualize_graphs import save_architecture_overview, save_memory_hierarchy_figure


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a cached G-Memory compare run without rerunning the official stack.")
    parser.add_argument("--compare-json")
    parser.add_argument("--cache-dir", default=str(PROJECT_ROOT / "demo/cached_runs"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "demo/outputs/replay"))
    args = parser.parse_args()

    compare_json = Path(args.compare_json) if args.compare_json else latest_json(args.cache_dir)
    if compare_json is None or not compare_json.exists():
        print("No cached compare JSON found. Run the live compare once first.")
        return 1

    import json

    compare_record = json.loads(compare_json.read_text(encoding="utf-8"))
    compare_payload = compare_record["compare_payload"]
    output_dir = ensure_dir(args.output_dir)

    compare_figure = save_compare_figure(compare_payload, output_dir / "replay_compare.png")
    hierarchy_figure = save_memory_hierarchy_figure(compare_payload, output_dir / "replay_memory_hierarchy.png")
    architecture_figure = save_architecture_overview(output_dir / "replay_architecture_overview.png")

    print(f"Replay source: {compare_json}")
    print(f"Compare figure: {compare_figure}")
    print(f"Memory hierarchy: {hierarchy_figure}")
    print(f"Architecture overview: {architecture_figure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
