from __future__ import annotations

from typing import Any


NOT_EXPOSED = "not exposed by current code path"


def _get(mapping: dict[str, Any], key: str, default: Any = NOT_EXPOSED) -> Any:
    value = mapping.get(key, default)
    return default if value in (None, "", []) else value


def extract_case_view(case_record: dict[str, Any]) -> dict[str, Any]:
    trace = case_record.get("trace", {})
    retrieval = trace.get("retrieval", {})
    selected_task = case_record.get("selected_task_config", {})

    return {
        "query": _get(trace, "task_main", selected_task.get("task", NOT_EXPOSED)),
        "task_description": _get(trace, "task_description", selected_task.get("task", NOT_EXPOSED)),
        "retrieved_historical_queries": retrieval.get("related_task_candidates", [NOT_EXPOSED]),
        "selected_successful_trajectories": retrieval.get("selected_successful_trajectories", [NOT_EXPOSED]),
        "selected_failed_trajectories": retrieval.get("selected_failed_trajectories", []),
        "selected_insights": retrieval.get("selected_insights", [NOT_EXPOSED]),
        "agent_memory_packets": trace.get("agent_memory_packets", {NOT_EXPOSED: NOT_EXPOSED}),
        "steps": trace.get("steps", []),
        "final_reward": _get(trace, "final_reward", case_record.get("reward")),
        "final_done": _get(trace, "final_done", case_record.get("success")),
        "final_feedback": _get(trace, "final_feedback"),
        "final_summary": _get(trace, "final_summary"),
        "saved_memory": trace.get("saved_memory", {}),
        "runtime_seconds": case_record.get("runtime_seconds"),
    }


def summarize_delta(no_memory_case: dict[str, Any], gmemory_case: dict[str, Any]) -> str:
    base = extract_case_view(no_memory_case)
    mem = extract_case_view(gmemory_case)

    evidence_count = len([item for item in mem["selected_insights"] if item != NOT_EXPOSED])
    retrieved_count = len([item for item in mem["retrieved_historical_queries"] if item != NOT_EXPOSED])

    if base["final_done"] is False and mem["final_done"] is True:
        return (
            f"G-Memory succeeds where the empty-memory baseline fails. "
            f"It retrieves {retrieved_count} related historical query nodes and {evidence_count} insight nodes, "
            "then injects role-specific memory packets before action selection."
        )

    if base["final_done"] == mem["final_done"]:
        return (
            f"Both runs end with done={mem['final_done']}, but the G-Memory condition adds "
            f"{retrieved_count} retrieved query candidates and {evidence_count} explicit insights."
        )

    return (
        f"The two runs diverge at the outcome level: baseline done={base['final_done']} vs "
        f"G-Memory done={mem['final_done']}. Retrieved memory evidence count: {retrieved_count} queries, "
        f"{evidence_count} insights."
    )


def build_compare_payload(no_memory_case: dict[str, Any], gmemory_case: dict[str, Any]) -> dict[str, Any]:
    return {
        "query": extract_case_view(gmemory_case)["query"],
        "no_memory": extract_case_view(no_memory_case),
        "gmemory": extract_case_view(gmemory_case),
        "delta_summary": summarize_delta(no_memory_case, gmemory_case),
    }
