from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.utils.caching import dump_json, latest_json, slugify
from demo.utils.official_wrapper import safe_run_compare_demo


def parse_indices(raw: str | None) -> list[int] | None:
    if raw is None or raw == "":
        return None
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the main no-memory vs G-Memory poster demo.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "demo/demo_config.yaml"))
    parser.add_argument("--task")
    parser.add_argument("--mas-type")
    parser.add_argument("--model")
    parser.add_argument("--max-trials", type=int)
    parser.add_argument("--warmup-max-trials", type=int)
    parser.add_argument("--target-task-index", type=int)
    parser.add_argument("--warmup-task-indices")
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "demo/outputs"))
    parser.add_argument("--cache-dir", default=str(PROJECT_ROOT / "demo/cached_runs"))
    parser.add_argument("--demo-mode", default="auto", choices=["auto", "mock", "live"])
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir)
    if args.use_cache:
        cached = latest_json(cache_dir)
        if cached is not None:
            print(f"Using cached compare record: {cached}")
            return 0

    overrides = {
        "task": args.task,
        "mas_type": args.mas_type,
        "model": args.model,
        "compare_max_trials": args.max_trials,
        "warmup_max_trials": args.warmup_max_trials,
        "target_task_index": args.target_task_index,
        "warmup_task_indices": parse_indices(args.warmup_task_indices),
    }
    compare_record = safe_run_compare_demo(
        config_path=args.config,
        output_dir=args.output_dir,
        demo_mode=args.demo_mode,
        overrides=overrides,
    )

    cache_name = slugify(compare_record["run_id"]) + ".json"
    cache_path = dump_json(compare_record, cache_dir / cache_name)

    artifacts = compare_record.get("artifacts", {})
    print("Live compare completed.")
    print(f"Run id: {compare_record['run_id']}")
    print(f"Backend: {compare_record['backend']}")
    print(f"Compare JSON: {artifacts.get('compare_json')}")
    print(f"Compare figure: {artifacts.get('compare_figure')}")
    print(f"Memory hierarchy: {artifacts.get('memory_hierarchy')}")
    print(f"Cache copy: {cache_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
