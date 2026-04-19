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


def _shorten(text: str, limit: int = 500) -> str:
    compact = " ".join(str(text).split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def save_compare_figure(compare_payload: dict, output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    baseline = compare_payload["no_memory"]
    gmemory = compare_payload["gmemory"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    titles = [("No Memory", baseline, "#f7ddd2"), ("G-Memory", gmemory, "#dce8f8")]

    for ax, (title, payload, color) in zip(axes, titles):
        ax.set_title(title, fontsize=16, loc="left")
        ax.axis("off")
        packet_preview = []
        for agent_name, packet in list(payload["agent_memory_packets"].items())[:2]:
            packet_preview.append(f"{agent_name}: {packet.get('insights', [])[:1]}")

        panel_text = "\n\n".join(
            [
                f"Query:\n{_shorten(payload['query'], 180)}",
                f"Outcome:\nreward={payload['final_reward']} | done={payload['final_done']}",
                f"Feedback:\n{_shorten(payload['final_feedback'], 150)}",
                f"Memory Evidence:\nqueries={len(payload['retrieved_historical_queries'])} | insights={len(payload['selected_insights'])}",
                f"Agent Packets:\n{_shorten(' | '.join(packet_preview), 200)}",
                f"Final Summary:\n{_shorten(payload['final_summary'], 320)}",
            ]
        )
        ax.text(
            0.03,
            0.97,
            panel_text,
            va="top",
            ha="left",
            fontsize=11,
            bbox={"boxstyle": "round,pad=0.8", "facecolor": color, "edgecolor": "#5b5b5b"},
            transform=ax.transAxes,
        )

    fig.suptitle(compare_payload["delta_summary"], fontsize=13, y=0.02)
    fig.subplots_adjust(left=0.04, right=0.98, top=0.92, bottom=0.10, wspace=0.14)
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return target
