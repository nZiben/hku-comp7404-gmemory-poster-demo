# pddl-autogen-mock-20260419T014847Z

- Backend: `mock`
- Task: `pddl`
- MAS type: `autogen`
- Delta summary: G-Memory succeeds where the empty-memory baseline fails. It retrieves 1 related historical query nodes and 2 insight nodes, then injects role-specific memory packets before action selection.

## No Memory
- reward=0.75, done=False
- feedback: not exposed by current code path

## G-Memory
- reward=1.0, done=True
- feedback: not exposed by current code path
- retrieved queries: 1
- selected insights: 2