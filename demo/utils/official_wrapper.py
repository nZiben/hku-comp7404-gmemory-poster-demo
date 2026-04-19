from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .caching import dump_json, ensure_dir, slugify, utc_timestamp
from .demo_backend import DemoHeuristicLLM
from .memory_introspection import build_compare_payload
from .parse_runs import parse_total_task_log
from .visualize_compare import save_compare_figure
from .visualize_graphs import save_architecture_overview, save_memory_hierarchy_figure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_ROOT = PROJECT_ROOT / "official_gmemory"


@dataclass
class DemoScenario:
    task: str = "pddl"
    mas_type: str = "autogen"
    reasoning: str = "io"
    model: str = "demo-mock-gripper"
    warmup_task_indices: list[int] = field(default_factory=lambda: [0])
    target_task_index: int = 0
    warmup_max_trials: int = 20
    compare_max_trials: int = 11
    successful_topk: int = 1
    failed_topk: int = 0
    insights_topk: int = 2
    threshold: float = 0.0
    hop: int = 1
    use_projector: bool = True
    start_insights_threshold: int = 1
    rounds_per_insights: int = 1
    insights_point_num: int = 1


def load_demo_config(config_path: str | Path) -> dict[str, Any]:
    import yaml

    with Path(config_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def discover_available_tasks() -> dict[str, Any]:
    datasets = {
        "alfworld": OFFICIAL_ROOT / "data/alfworld/alfworld_tasks_suffix.json",
        "fever": OFFICIAL_ROOT / "data/fever/fever_dev.jsonl",
        "pddl": OFFICIAL_ROOT / "data/pddl/test.jsonl",
        "sciworld": OFFICIAL_ROOT / "data/sciworld/test.jsonl",
    }
    summary = {}
    for name, path in datasets.items():
        if not path.exists():
            summary[name] = {"available": False, "count": 0, "path": str(path)}
            continue
        if path.suffix == ".json":
            count = len(json.loads(path.read_text(encoding="utf-8")))
        else:
            count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        summary[name] = {"available": True, "count": count, "path": str(path)}
    return summary


def recommended_task_name() -> str | None:
    availability = discover_available_tasks()
    for candidate in ("pddl", "fever", "sciworld", "alfworld"):
        if availability.get(candidate, {}).get("available"):
            return candidate
    return None


def resolve_backend(demo_mode: str) -> str:
    if demo_mode in {"mock", "local"}:
        return "mock"
    if demo_mode in {"live", "openai"}:
        return "openai"
    has_openai = importlib.util.find_spec("openai") is not None
    has_credentials = bool(os.getenv("OPENAI_API_BASE") and os.getenv("OPENAI_API_KEY"))
    return "openai" if has_openai and has_credentials else "mock"


def configure_demo_environment(backend: str) -> None:
    os.environ["GMEMORY_DEMO"] = "1"
    cache_root = ensure_dir(PROJECT_ROOT / ".demo_cache")
    matplotlib_cache = ensure_dir(cache_root / "matplotlib")
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_root))
    if backend == "mock":
        os.environ["GMEMORY_SIMPLE_EMBEDDING"] = "1"
        os.environ["GMEMORY_SIMPLE_STORE"] = "1"


@contextmanager
def official_repo_context():
    previous_cwd = Path.cwd()
    original_sys_path = list(sys.path)
    os.chdir(OFFICIAL_ROOT)
    sys.path.insert(0, str(OFFICIAL_ROOT))
    sys.path.insert(0, str(OFFICIAL_ROOT / "tasks"))
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        yield
    finally:
        os.chdir(previous_cwd)
        sys.path[:] = original_sys_path


def _load_run_module():
    importlib.invalidate_caches()
    return importlib.import_module("tasks.run")


def _pick_llm(backend: str, model: str):
    if backend == "mock":
        return DemoHeuristicLLM(model_name=model)
    return None


def _scenario_from_config(config: dict[str, Any], backend: str, overrides: dict[str, Any]) -> DemoScenario:
    base = dict(config.get("defaults", {}))
    base.update(config.get(backend, {}))
    base.update({key: value for key, value in overrides.items() if value is not None})
    return DemoScenario(**base)


def _prepare_task_manager(
    run_module,
    scenario: DemoScenario,
    memory_type: str,
    max_trials: int,
    task_indices: list[int],
    working_dir: Path,
    backend: str,
):
    task_manager = run_module.build_task(scenario.task, scenario.mas_type, memory_type, max_trials)
    selected_tasks = [dict(task_manager.tasks[index]) for index in task_indices]
    task_manager.tasks = selected_tasks
    task_manager.mas_config["successful_topk"] = scenario.successful_topk
    task_manager.mas_config["failed_topk"] = scenario.failed_topk
    task_manager.mas_config["insights_topk"] = scenario.insights_topk
    task_manager.mas_config["threshold"] = scenario.threshold
    task_manager.mas_config["use_projector"] = scenario.use_projector
    task_manager.mem_config.update(
        working_dir=str(working_dir),
        hop=scenario.hop,
        start_insights_threshold=scenario.start_insights_threshold,
        rounds_per_insights=scenario.rounds_per_insights,
        insights_point_num=scenario.insights_point_num,
    )

    llm_model = _pick_llm(backend, scenario.model)
    run_module.build_mas(
        task_manager,
        reasoning=scenario.reasoning,
        mas_memory=memory_type,
        llm_type=scenario.model,
        llm_model=llm_model,
    )
    return task_manager, selected_tasks


def run_case(
    scenario: DemoScenario,
    memory_type: str,
    task_indices: list[int],
    max_trials: int,
    working_dir: Path,
    backend: str,
    label: str,
) -> dict[str, Any]:
    configure_demo_environment(backend)
    working_dir = ensure_dir(working_dir)

    with official_repo_context():
        run_module = _load_run_module()
        run_module.WORKING_DIR = str(working_dir)
        task_manager, selected_tasks = _prepare_task_manager(
            run_module,
            scenario=scenario,
            memory_type=memory_type,
            max_trials=max_trials,
            task_indices=task_indices,
            working_dir=working_dir,
            backend=backend,
        )

        start_time = time.time()
        run_module.run_task(task_manager)
        runtime_seconds = time.time() - start_time

    trace = getattr(task_manager.mas, "last_demo_trace", {})
    log_summary = parse_total_task_log(task_manager.recorder.file_path)
    return {
        "label": label,
        "task": scenario.task,
        "mas_type": scenario.mas_type,
        "reasoning": scenario.reasoning,
        "memory_type": memory_type,
        "backend": backend,
        "model": scenario.model,
        "max_trials": max_trials,
        "task_indices": task_indices,
        "selected_task_config": selected_tasks[-1],
        "warmup_task_configs": selected_tasks[:-1],
        "working_dir": str(working_dir.resolve()),
        "log_path": str(Path(task_manager.recorder.file_path).resolve()),
        "runtime_seconds": runtime_seconds,
        "trace": trace,
        "success": trace.get("final_done"),
        "reward": trace.get("final_reward"),
        "log_summary": log_summary,
    }


def run_compare_demo(
    config_path: str | Path,
    output_dir: str | Path,
    demo_mode: str = "auto",
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    overrides = overrides or {}
    backend = resolve_backend(demo_mode)
    config = load_demo_config(config_path)
    scenario = _scenario_from_config(config, backend, overrides)

    run_stamp = f"{slugify(scenario.task)}-{scenario.mas_type}-{backend}-{utc_timestamp()}"
    output_root = ensure_dir(output_dir) / run_stamp
    ensure_dir(output_root)

    baseline_case = run_case(
        scenario=scenario,
        memory_type="empty",
        task_indices=[scenario.target_task_index],
        max_trials=scenario.compare_max_trials,
        working_dir=output_root / "official_runs" / "baseline",
        backend=backend,
        label="no-memory",
    )
    gmemory_working_dir = output_root / "official_runs" / "gmemory"
    warmup_records = []
    for warmup_position, warmup_index in enumerate(scenario.warmup_task_indices, start=1):
        warmup_records.append(
            run_case(
                scenario=scenario,
                memory_type="g-memory",
                task_indices=[warmup_index],
                max_trials=scenario.warmup_max_trials,
                working_dir=gmemory_working_dir,
                backend=backend,
                label=f"warmup-{warmup_position}",
            )
        )

    gmemory_case = run_case(
        scenario=scenario,
        memory_type="g-memory",
        task_indices=[scenario.target_task_index],
        max_trials=scenario.compare_max_trials,
        working_dir=gmemory_working_dir,
        backend=backend,
        label="g-memory",
    )

    compare_payload = build_compare_payload(baseline_case, gmemory_case)
    compare_record = {
        "run_id": run_stamp,
        "backend": backend,
        "scenario": scenario.__dict__,
        "baseline_case": baseline_case,
        "warmup_cases": warmup_records,
        "gmemory_case": gmemory_case,
        "compare_payload": compare_payload,
    }

    compare_json_path = dump_json(compare_record, output_root / "compare_result.json")
    compare_figure = save_compare_figure(compare_payload, output_root / "compare_figure.png")
    hierarchy_figure = save_memory_hierarchy_figure(compare_payload, output_root / "memory_hierarchy.png")
    architecture_figure = save_architecture_overview(output_root / "architecture_overview.png")

    compare_record["artifacts"] = {
        "compare_json": str(compare_json_path.resolve()),
        "compare_figure": str(compare_figure.resolve()),
        "memory_hierarchy": str(hierarchy_figure.resolve()),
        "architecture_overview": str(architecture_figure.resolve()),
    }
    dump_json(compare_record, output_root / "compare_result.json")
    return compare_record


def safe_run_compare_demo(
    config_path: str | Path,
    output_dir: str | Path,
    demo_mode: str = "auto",
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return run_compare_demo(config_path=config_path, output_dir=output_dir, demo_mode=demo_mode, overrides=overrides)
    except Exception as exc:  # pragma: no cover - exercised in actual demo environments
        failure = {
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        dump_json(failure, ensure_dir(output_dir) / f"failed-{utc_timestamp()}.json")
        raise
