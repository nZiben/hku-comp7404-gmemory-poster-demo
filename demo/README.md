# G-Memory Poster Demo

This `demo/` package is a presentation-focused engineering layer built on top of the official G-Memory repository. It is meant for a course-project poster/demo setting where reliability, explainability, and visible reuse of the research code matter more than full benchmark reproduction.

## Start Here

- [Latest verified results](./LATEST_RESULTS.md)
- [Quickstart](./QUICKSTART.md)
- [Main notebook](./GMemory_Poster_Demo.ipynb)
- Published figures: [compare](./published/latest_compare.png), [memory flow](./published/latest_memory_flow.png), [architecture](./published/latest_architecture.png)

## What Was Reused

- The official task runner structure from `official_gmemory/tasks/run.py`
- The original MAS workflows, especially `autogen`
- The official `GMemory` memory module and its task/insight hierarchy
- The shipped dataset files under `official_gmemory/data/`
- The authors’ prompt and task formatting logic

## What Was Added

- A demo wrapper that picks a small laptop-safe task and runs side-by-side compare mode
- Opt-in tracing for retrieved tasks, selected insights, interaction trajectories, and per-agent memory packets
- A deterministic local mock backend for smoke tests and replay-safe demo generation
- Replay mode, cached compare records, summary export, and poster-ready figures
- A notebook, quickstart, presenter notes, and environment checks

## Demo Modes

- `Smoke Test`: verifies imports and runs a tiny `g-memory` case with a very small step budget
- `Live Compare`: runs the same task twice, once with `empty` memory and once with `g-memory`
- `Replay Demo`: loads a saved compare JSON and regenerates figures without rerunning the official stack

## Recommended Task Choice

The primary demo path uses the local `pddl` benchmark with the `gripper` subtask. In the official task index ordering this starts at `30`, so the default compare target is `pddl` task index `30`.

Why this choice:

- It is fully local
- It avoids external wiki lookup and large embodied environments
- It makes the memory effect easy to explain: transport planning under a small action budget

## Setup

1. Bootstrap the official upstream repo into `official_gmemory/` if it is not already present:

```bash
python demo/scripts/bootstrap_official_repo.py
```

2. Create or activate a Python environment.
3. Install the demo dependencies:

```bash
pip install -r demo/requirements-demo.txt
```

3. Optional: configure an OpenAI-compatible backend for API-backed live mode.

```bash
export OPENAI_API_BASE="..."
export OPENAI_API_KEY="..."
```

Notes:

- The demo layer has a local fallback path and does not require `langchain_chroma` or `sentence_transformers` for mock mode.
- This course-project repo keeps the demo layer separate from the authors' upstream repo. The expected local checkout path is `official_gmemory/`.

## Commands

Environment check:

```bash
python demo/scripts/check_environment.py
```

Smoke test:

```bash
python demo/scripts/run_smoke_demo.py --demo-mode mock
```

Main poster demo:

```bash
python demo/scripts/run_live_compare.py --demo-mode mock
```

API-backed compare when credentials are configured:

```bash
python demo/scripts/run_live_compare.py --demo-mode auto
```

Replay fallback:

```bash
python demo/scripts/run_replay_demo.py
```

Export a markdown case summary:

```bash
python demo/scripts/export_case_summary.py --compare-json demo/cached_runs/<compare-file>.json
```

Publish the latest compare run to stable GitHub-visible paths:

```bash
python demo/scripts/publish_demo_snapshot.py
```

## How To Read The Outputs

Successful live compare runs write a folder under `demo/outputs/` containing:

- `compare_result.json`
- `compare_figure.png`
- `memory_hierarchy.png`
- `official_runs/` with the underlying recorder logs and persisted memory

The JSON contains:

- task/query metadata
- baseline vs G-Memory outcomes
- retrieved historical query candidates
- selected successful trajectories
- selected insight nodes
- per-agent memory packets
- runtime metadata

For GitHub-friendly browsing, the latest published snapshot is copied to:

- `demo/LATEST_RESULTS.md`
- `demo/published/latest_compare.png`
- `demo/published/latest_memory_flow.png`
- `demo/published/latest_architecture.png`
- `demo/published/latest_compare.json`

## Common Failure Cases

- Missing Python packages: run `python demo/scripts/check_environment.py`
- Missing OpenAI credentials: use `--demo-mode mock` or `run_replay_demo.py`
- Optional benchmark packages like `alfworld` missing: the demo still works because it only depends on the local `pddl` path
- Live output differs from paper claims: label it as a small local demo run, not a benchmark reproduction

## Notebook

Open:

- [GMemory_Poster_Demo.ipynb](./GMemory_Poster_Demo.ipynb)

The notebook is designed to work as a guided walkthrough for the presenter and as grading evidence for how the official code was reused and instrumented.

## Attribution

The original G-Memory implementation, benchmark structure, and research method are from the authors of:

Zhang, Guibin and Fu, Muxin and Wan, Guancheng and Yu, Miao and Wang, Kun and Yan, Shuicheng.  
“G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems.”

This demo package is an add-on presentation layer and not a reimplementation of the research system from scratch.
