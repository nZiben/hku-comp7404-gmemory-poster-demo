from __future__ import annotations

import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CACHE_ROOT = _PROJECT_ROOT / ".demo_cache"
_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
(_CACHE_ROOT / "matplotlib").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE_ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE_ROOT / "matplotlib"))

import matplotlib

matplotlib.use("Agg")


def _shorten(text: str, limit: int = 52) -> str:
    compact = " ".join(str(text).split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def save_architecture_overview(output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")

    boxes = [
        ((0.05, 0.62), "Official G-Memory Repo\nentry points, MAS workflows,\nPDDL/FEVER environments"),
        ((0.38, 0.62), "Demo Wrapper Layer\nsmall-task selection,\nmock/live backend switch,\nstructured result capture"),
        ((0.72, 0.62), "Poster Outputs\ncompare JSON, figures,\nnotebook, replay cache"),
        ((0.38, 0.18), "Memory Introspection\nquery retrieval,\ninsight selection,\nagent packets"),
    ]
    for (x, y), label in boxes:
        ax.text(
            x,
            y,
            label,
            ha="left",
            va="center",
            fontsize=12,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f7f3e8", "edgecolor": "#6f5f44", "linewidth": 1.5},
            transform=ax.transAxes,
        )

    arrow = dict(arrowstyle="->", color="#6f5f44", linewidth=2)
    ax.annotate("", xy=(0.36, 0.62), xytext=(0.28, 0.62), xycoords="axes fraction", arrowprops=arrow)
    ax.annotate("", xy=(0.70, 0.62), xytext=(0.62, 0.62), xycoords="axes fraction", arrowprops=arrow)
    ax.annotate("", xy=(0.52, 0.33), xytext=(0.52, 0.52), xycoords="axes fraction", arrowprops=arrow)

    fig.tight_layout()
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return target


def save_memory_hierarchy_figure(compare_payload: dict, output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt
    import networkx as nx

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    gmemory = compare_payload["gmemory"]
    graph = nx.DiGraph()

    query_label = _shorten(gmemory["query"], 58)
    graph.add_node("query", label=f"Query\n{query_label}", layer="query")

    for index, task in enumerate(gmemory["retrieved_historical_queries"][:4], start=1):
        node_id = f"hist_{index}"
        graph.add_node(node_id, label=f"Retrieved Task {index}\n{_shorten(task)}", layer="history")
        graph.add_edge("query", node_id)

    for index, insight in enumerate(gmemory["selected_insights"][:3], start=1):
        node_id = f"insight_{index}"
        graph.add_node(node_id, label=f"Insight {index}\n{_shorten(insight)}", layer="insight")
        graph.add_edge("query", node_id)

    for index, traj in enumerate(gmemory["selected_successful_trajectories"][:2], start=1):
        key_steps = traj.get("key_steps") or traj.get("task_main") or "successful trajectory"
        node_id = f"traj_{index}"
        graph.add_node(node_id, label=f"Trajectory {index}\n{_shorten(key_steps)}", layer="trajectory")
        graph.add_edge(f"hist_{min(index, max(1, len(gmemory['retrieved_historical_queries'])))}", node_id)

    for index, (agent_name, packet) in enumerate(list(gmemory["agent_memory_packets"].items())[:3], start=1):
        insights = packet.get("insights", [])
        snippet = insights[0] if insights else "no role-specific insight packet"
        node_id = f"agent_{index}"
        graph.add_node(node_id, label=f"{agent_name}\n{_shorten(snippet)}", layer="agent")
        for insight_index in range(1, min(3, len(gmemory["selected_insights"])) + 1):
            graph.add_edge(f"insight_{insight_index}", node_id)

    positions = {}
    layer_positions = {
        "query": (0.5, 0.92),
        "history": (0.22, 0.62),
        "insight": (0.50, 0.62),
        "trajectory": (0.78, 0.62),
        "agent": (0.50, 0.22),
    }
    layer_counts: dict[str, int] = {}
    for node, attributes in graph.nodes(data=True):
        layer = attributes["layer"]
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        count = layer_counts[layer]
        x, y = layer_positions[layer]
        positions[node] = (x + (count - 1) * 0.18 - 0.09, y)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("G-Memory Retrieval and Injection Path", fontsize=16, loc="left")
    ax.axis("off")
    colors = {
        "query": "#d7eadf",
        "history": "#f7efd4",
        "insight": "#dce8f8",
        "trajectory": "#f9ddd2",
        "agent": "#e9dff4",
    }

    for layer, color in colors.items():
        nodes = [node for node, data in graph.nodes(data=True) if data["layer"] == layer]
        if nodes:
            nx.draw_networkx_nodes(graph, positions, nodelist=nodes, node_color=color, node_size=6500, ax=ax)

    nx.draw_networkx_edges(graph, positions, width=1.8, edge_color="#5b5b5b", arrows=True, ax=ax)
    labels = {node: data["label"] for node, data in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=9, ax=ax)

    fig.tight_layout()
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return target
