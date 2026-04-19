from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.utils.caching import dump_json, ensure_dir, utc_timestamp
from demo.utils.official_wrapper import DemoScenario, load_demo_config, resolve_backend, run_case


def build_scenario(config_path: Path, demo_mode: str, task_index: int | None, max_trials: int) -> DemoScenario:
    config = load_demo_config(config_path)
    backend = resolve_backend(demo_mode)
    merged = dict(config.get("defaults", {}))
    merged.update(config.get(backend, {}))
    target_index = merged.get("target_task_index", 0) if task_index is None else task_index
    merged.update(
        {
            "warmup_task_indices": [],
            "target_task_index": target_index,
            "compare_max_trials": max_trials,
            "warmup_max_trials": max_trials,
        }
    )
    return DemoScenario(**merged)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a very small G-Memory smoke test.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "demo/demo_config.yaml"))
    parser.add_argument("--task-index", type=int)
    parser.add_argument("--max-trials", type=int, default=4)
    parser.add_argument("--demo-mode", default="auto", choices=["auto", "mock", "live"])
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "demo/outputs"))
    args = parser.parse_args()

    scenario = build_scenario(Path(args.config), args.demo_mode, args.task_index, args.max_trials)
    backend = resolve_backend(args.demo_mode)
    smoke_dir = ensure_dir(args.output_dir) / f"smoke-{utc_timestamp()}"
    result = run_case(
        scenario=scenario,
        memory_type="g-memory",
        task_indices=[scenario.target_task_index],
        max_trials=scenario.compare_max_trials,
        working_dir=smoke_dir / "official_runs" / "gmemory-smoke",
        backend=backend,
        label="smoke-gmemory",
    )
    result["status"] = "completed_without_exception"
    result_path = dump_json(result, smoke_dir / "smoke_result.json")

    print("Smoke demo completed.")
    print(f"Backend: {backend}")
    print(f"Success flag: {result.get('success')}")
    print(f"Output: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
