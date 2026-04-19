from __future__ import annotations

import re
from pathlib import Path


TASK_HEADER_RE = re.compile(r"-+ Task: (?P<task_id>\d+) -+")
ACTION_RE = re.compile(r"Act (?P<step>\d+): (?P<action>.*)")
OBS_RE = re.compile(r"Obs (?P<step>\d+): (?P<observation>.*)")
REWARD_RE = re.compile(r"reward: (?P<reward>[-+]?\d+(?:\.\d+)?)")
DONE_RE = re.compile(r"done: (?P<done>True|False)")
TIME_RE = re.compile(r"Total execution time: (?P<seconds>\d+(?:\.\d+)?) seconds")


def parse_total_task_log(path: str | Path) -> dict:
    target = Path(path)
    if not target.exists():
        return {
            "path": str(target),
            "exists": False,
            "tasks": [],
            "runtime_seconds": None,
        }

    tasks: list[dict] = []
    current = None
    runtime_seconds = None

    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.split(" - ", 1)[-1] if " - " in raw_line else raw_line
        header_match = TASK_HEADER_RE.search(line)
        if header_match:
            current = {
                "task_id": int(header_match.group("task_id")),
                "steps": [],
                "reward": None,
                "done": None,
            }
            tasks.append(current)
            continue

        if current is None:
            time_match = TIME_RE.search(line)
            if time_match:
                runtime_seconds = float(time_match.group("seconds"))
            continue

        action_match = ACTION_RE.search(line)
        if action_match:
            current["steps"].append(
                {
                    "step": int(action_match.group("step")),
                    "action": action_match.group("action").strip(),
                    "observation": None,
                }
            )
            continue

        observation_match = OBS_RE.search(line)
        if observation_match and current["steps"]:
            current["steps"][-1]["observation"] = observation_match.group("observation").strip()
            continue

        reward_match = REWARD_RE.search(line)
        if reward_match:
            current["reward"] = float(reward_match.group("reward"))

        done_match = DONE_RE.search(line)
        if done_match:
            current["done"] = done_match.group("done") == "True"

        time_match = TIME_RE.search(line)
        if time_match:
            runtime_seconds = float(time_match.group("seconds"))

    return {
        "path": str(target.resolve()),
        "exists": True,
        "tasks": tasks,
        "runtime_seconds": runtime_seconds,
        "task_count": len(tasks),
    }
