from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = PROJECT_ROOT / "demo/GMemory_Poster_Demo.ipynb"


def markdown_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def build_notebook() -> dict:
    cells = [
        markdown_cell(
            "# G-Memory Poster Demo\n\n"
            "This notebook is the presentation-friendly front end for the course-project demo layer. "
            "It wraps the official G-Memory repository, keeps the task small enough for a laptop, "
            "and exposes the retrieval pipeline in a way that is easy to explain live."
        ),
        markdown_cell(
            "## 1. Project Overview\n\n"
            "- The official repository is reused from `official_gmemory/`.\n"
            "- The demo layer adds small-task selection, structured tracing, visualization, and replay.\n"
            "- The recommended live path is a local `pddl` gripper example with `autogen` agents."
        ),
        markdown_cell(
            "## 2. What G-Memory Adds Over Standard MAS\n\n"
            "G-Memory is not just a larger context window. It builds a hierarchy of past tasks, distilled insights, "
            "and interaction trajectories, then injects targeted memory back into the multi-agent workflow."
        ),
        code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import sys\n\n"
            "PROJECT_ROOT = Path.cwd().resolve().parents[0] if Path.cwd().name == 'demo' else Path.cwd().resolve()\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n\n"
            "from demo.utils.official_wrapper import discover_available_tasks, recommended_task_name\n"
            "from demo.utils.memory_introspection import extract_case_view, build_compare_payload\n"
            "from demo.utils.visualize_graphs import save_memory_hierarchy_figure, save_architecture_overview\n"
            "from demo.utils.visualize_compare import save_compare_figure\n"
            "from demo.utils.caching import latest_json\n"
        ),
        markdown_cell("## 3. Environment / Repo Sanity Checks"),
        code_cell(
            "available = discover_available_tasks()\n"
            "available"
        ),
        markdown_cell("## 4. Detect Available Tasks and Configs"),
        code_cell(
            "recommended_task_name()"
        ),
        markdown_cell(
            "## 5. Select the Recommended Demo Task Automatically\n\n"
            "The wrapper prefers `pddl` when it is present, because it is fully local and does not require external search."
        ),
        markdown_cell("## 6. Run or Load the No-Memory Baseline"),
        code_cell(
            "compare_json = latest_json(PROJECT_ROOT / 'demo/cached_runs')\n"
            "assert compare_json is not None, 'Run the live compare once or add a cached compare JSON first.'\n"
            "compare_record = json.loads(compare_json.read_text(encoding='utf-8'))\n"
            "no_memory_view = extract_case_view(compare_record['baseline_case'])\n"
            "no_memory_view"
        ),
        markdown_cell("## 7. Run or Load the G-Memory Version"),
        code_cell(
            "gmemory_view = extract_case_view(compare_record['gmemory_case'])\n"
            "gmemory_view"
        ),
        markdown_cell("## 8. Inspect Retrieved Memory"),
        code_cell(
            "compare_payload = compare_record['compare_payload']\n"
            "{\n"
            "    'retrieved_historical_queries': gmemory_view['retrieved_historical_queries'],\n"
            "    'selected_successful_trajectories': gmemory_view['selected_successful_trajectories'],\n"
            "    'selected_insights': gmemory_view['selected_insights'],\n"
            "}"
        ),
        markdown_cell("## 9. Visualize Query / Insight / Interaction Structures"),
        code_cell(
            "memory_fig_path = PROJECT_ROOT / 'demo/outputs/notebook_memory_flow.png'\n"
            "save_memory_hierarchy_figure(compare_payload, memory_fig_path)\n"
            "memory_fig_path"
        ),
        markdown_cell("## 10. Show Per-Agent Memory Assignment"),
        code_cell(
            "gmemory_view['agent_memory_packets']"
        ),
        markdown_cell("## 11. Compare Final Outputs"),
        code_cell(
            "compare_fig_path = PROJECT_ROOT / 'demo/outputs/notebook_compare.png'\n"
            "save_compare_figure(compare_payload, compare_fig_path)\n"
            "compare_fig_path"
        ),
        markdown_cell("## 12. Summarize Why the Behavior Changed"),
        code_cell(
            "compare_payload['delta_summary']"
        ),
        markdown_cell("## 13. Replay Cached Example"),
        code_cell(
            "arch_fig_path = PROJECT_ROOT / 'demo/outputs/notebook_architecture.png'\n"
            "save_architecture_overview(arch_fig_path)\n"
            "arch_fig_path"
        ),
        markdown_cell(
            "## 14. Final Presenter Takeaway\n\n"
            "The important point is not the absolute score of this tiny local run. "
            "It is that the official pipeline is being reused, the retrieval path is visible, "
            "and the presenter has both a live mode and a replay-safe fallback."
        ),
    ]

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    NOTEBOOK_PATH.write_text(json.dumps(build_notebook(), indent=2), encoding="utf-8")
    print(f"Wrote {NOTEBOOK_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
