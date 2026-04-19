# Quickstart

## Install

```bash
python demo/scripts/bootstrap_official_repo.py
python -m venv .venv
source .venv/bin/activate
pip install -r demo/requirements-demo.txt
```

## Verify

```bash
python demo/scripts/check_environment.py
python demo/scripts/run_smoke_demo.py --demo-mode mock
```

## Run The Main Demo

Guaranteed local mode:

```bash
python demo/scripts/run_live_compare.py --demo-mode mock
```

Auto-switch to API mode if credentials are set:

```bash
python demo/scripts/run_live_compare.py --demo-mode auto
```

## Run The Fallback Replay

```bash
python demo/scripts/run_replay_demo.py
```

## Open The Notebook

- [GMemory_Poster_Demo.ipynb](./GMemory_Poster_Demo.ipynb)
- [Latest verified results](./LATEST_RESULTS.md)

## Where Files Go

- Cached compare JSON: `demo/cached_runs/`
- Fresh live outputs: `demo/outputs/`
- Poster-ready example figures: `demo/assets/`
- Stable GitHub-visible snapshot: `demo/published/`
