from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.utils.caching import ensure_dir, latest_json
from demo.utils.memory_introspection import NOT_EXPOSED
from demo.utils.visualize_compare import save_compare_figure
from demo.utils.visualize_graphs import save_architecture_overview, save_memory_hierarchy_figure


def _meaningful_count(items: list[object]) -> int:
    return len([item for item in items if item not in (None, "", [], NOT_EXPOSED)])


def _copy_or_render(source: str | None, fallback_writer, output_path: Path) -> Path:
    if source:
        source_path = Path(source)
        if source_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, output_path)
            return output_path
    return fallback_writer(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish the latest demo snapshot to stable, GitHub-visible paths.")
    parser.add_argument("--compare-json", default=None)
    parser.add_argument("--cache-dir", default=str(PROJECT_ROOT / "demo/cached_runs"))
    parser.add_argument("--publish-dir", default=str(PROJECT_ROOT / "demo/published"))
    parser.add_argument("--results-markdown", default=str(PROJECT_ROOT / "demo/LATEST_RESULTS.md"))
    args = parser.parse_args()

    compare_json = Path(args.compare_json) if args.compare_json else latest_json(args.cache_dir)
    if compare_json is None or not compare_json.exists():
        raise SystemExit("No compare JSON found. Run the live demo first or pass --compare-json.")

    compare_record = json.loads(compare_json.read_text(encoding="utf-8"))
    compare_payload = compare_record["compare_payload"]
    artifacts = compare_record.get("artifacts", {})

    publish_dir = ensure_dir(args.publish_dir)
    results_markdown = Path(args.results_markdown)

    compare_image = _copy_or_render(
        artifacts.get("compare_figure"),
        lambda output_path: save_compare_figure(compare_payload, output_path),
        publish_dir / "latest_compare.png",
    )
    memory_image = _copy_or_render(
        artifacts.get("memory_hierarchy"),
        lambda output_path: save_memory_hierarchy_figure(compare_payload, output_path),
        publish_dir / "latest_memory_flow.png",
    )
    architecture_image = _copy_or_render(
        artifacts.get("architecture_overview"),
        lambda output_path: save_architecture_overview(output_path),
        publish_dir / "latest_architecture.png",
    )

    published_json = publish_dir / "latest_compare.json"
    published_json.write_text(json.dumps(compare_record, indent=2), encoding="utf-8")

    no_memory = compare_payload["no_memory"]
    gmemory = compare_payload["gmemory"]
    rel_compare = compare_image.relative_to(PROJECT_ROOT / "demo")
    rel_memory = memory_image.relative_to(PROJECT_ROOT / "demo")
    rel_architecture = architecture_image.relative_to(PROJECT_ROOT / "demo")
    rel_json = published_json.relative_to(PROJECT_ROOT / "demo")

    markdown = "\n".join(
        [
            "# Latest Verified Results",
            "",
            "This page is the stable snapshot used by the repository landing page.",
            "It is regenerated from the latest successful compare record with `publish_demo_snapshot.py`.",
            "",
            f"- Run id: `{compare_record['run_id']}`",
            f"- Backend: `{compare_record['backend']}`",
            f"- Task: `{compare_record['scenario']['task']}`",
            f"- MAS type: `{compare_record['scenario']['mas_type']}`",
            f"- Delta summary: {compare_payload['delta_summary']}",
            "",
            "## Outcome Table",
            "",
            "| Mode | Reward | Done | Runtime (s) |",
            "| --- | --- | --- | --- |",
            f"| No memory | `{no_memory['final_reward']}` | `{no_memory['final_done']}` | `{no_memory['runtime_seconds']}` |",
            f"| G-Memory | `{gmemory['final_reward']}` | `{gmemory['final_done']}` | `{gmemory['runtime_seconds']}` |",
            "",
            "## Retrieved Memory Evidence",
            "",
            f"- Historical query candidates exposed: `{_meaningful_count(gmemory['retrieved_historical_queries'])}`",
            f"- Successful trajectories exposed: `{_meaningful_count(gmemory['selected_successful_trajectories'])}`",
            f"- Insight nodes exposed: `{_meaningful_count(gmemory['selected_insights'])}`",
            f"- Agent memory packets exposed: `{len(gmemory['agent_memory_packets'])}`",
            "",
            "## Compare Figure",
            "",
            f"![Latest compare figure](./{rel_compare.as_posix()})",
            "",
            "## Memory Flow Figure",
            "",
            f"![Latest memory flow](./{rel_memory.as_posix()})",
            "",
            "## Architecture Figure",
            "",
            f"![Latest architecture overview](./{rel_architecture.as_posix()})",
            "",
            "## Raw Artifact",
            "",
            f"- [Stable compare JSON](./{rel_json.as_posix()})",
        ]
    )

    results_markdown.write_text(markdown + "\n", encoding="utf-8")
    print(f"Published snapshot from {compare_json}")
    print(f"Results markdown: {results_markdown}")
    print(f"Compare image: {compare_image}")
    print(f"Memory image: {memory_image}")
    print(f"Architecture image: {architecture_image}")
    print(f"Stable compare JSON: {published_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
