# Presenter Notes

## 60-Second Version

G-Memory extends a multi-agent system with a hierarchy of past task memories. Instead of only solving the current problem from scratch, it retrieves related historical tasks, climbs upward to reusable insights, then pushes back down to compact interaction trajectories and role-specific memory packets for the active agents. In this demo we reuse the official repository, run a small local PDDL task twice under the same setup, and only change the memory condition: `empty` versus `g-memory`.

## 90-Second Version

This poster demo is a reliability-first wrapper around the official G-Memory codebase. We kept the authors’ task runner, MAS workflow, and memory module, then added instrumentation so we can expose what gets retrieved and injected at runtime. The live example uses a small local `pddl/gripper` task that is easy to run on a laptop. First we show a no-memory baseline under a tight action budget. Then we prewarm G-Memory with one successful prior experience and rerun the same target task. The compare output shows the retrieved historical query node, the selected insights, the compact successful trajectory, the per-agent memory packet, and the final outcome change. If live execution is unstable, replay mode regenerates the same visualization from a cached compare record.

## What To Show First

- Open the repository root `README.md` for the project overview and the latest figures.
- Open `demo/assets/architecture_overview.png` and say this is a wrapper on top of the official repo, not a rewrite.
- Show `python demo/scripts/run_live_compare.py --demo-mode mock` or the latest `compare_result.json`.
- Point to the side-by-side baseline vs G-Memory outcome.
- Show the memory hierarchy figure and explain query retrieval -> insight selection -> trajectory reuse -> agent packet injection.
- End on the outcome difference and the replay fallback.

## Fallback Checklist

- If API mode is slow, switch to `--demo-mode mock`.
- If live compare is risky, run `python demo/scripts/run_replay_demo.py`.
- If someone asks whether the replay is real, say it is regenerated from a saved compare JSON produced by the same wrapper.
- If someone asks about benchmark claims, say this is a small local demo run and not a paper reproduction.

## Likely Questions

1. Is this the authors’ real implementation?
   Yes. The demo reuses the official task runner, MAS workflow, prompts, and G-Memory module under `official_gmemory/`, then adds wrappers and instrumentation.

2. Why use a PDDL task instead of a larger environment?
   Because the project rewards a sophisticated demo, and the local PDDL path is much more reliable on a laptop than heavier embodied environments.

3. What exactly changes between the two runs?
   The task, MAS type, backend, and budget stay the same. The only intended change is the memory condition: `empty` versus `g-memory`.

4. Is the mock backend a scientific evaluation?
   No. It is a deterministic presentation mode that keeps the official execution path visible and stable for a poster session. Any results from it should be labeled as demo behavior, not benchmark evidence.

5. What is replay mode for?
   Replay mode is the presentation-safe fallback. It loads a saved compare JSON and redraws the figures without rerunning the full task stack.
