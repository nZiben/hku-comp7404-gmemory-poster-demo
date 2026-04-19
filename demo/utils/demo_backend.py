from __future__ import annotations

import re
from dataclasses import dataclass


def _content(messages, index: int) -> str:
    if len(messages) <= index:
        return ""
    message = messages[index]
    return getattr(message, "content", str(message))


def _extract_current_task_section(user_prompt: str) -> str:
    marker = "## Your Turn: Take Action!"
    return user_prompt.rsplit(marker, 1)[-1]


def _ball_count(task_section: str) -> int:
    matches = re.findall(r"ball(\d+)\s+is at roomb", task_section.lower())
    return len(set(matches)) or 4


def _completed_steps(task_section: str) -> int:
    return max(0, len(re.findall(r"(?m)^>", task_section)) - 1)


def _has_memory(user_prompt: str) -> bool:
    return "Task 1:" in user_prompt or "1. Carry" in user_prompt


def _single_gripper_plan(ball_count: int) -> list[str]:
    actions = []
    for ball_index in range(1, ball_count + 1):
        ball = f"ball{ball_index}"
        actions.extend(
            [
                f"pick {ball} rooma right",
                "move rooma roomb",
                f"drop {ball} roomb right",
            ]
        )
        if ball_index != ball_count:
            actions.append("move roomb rooma")
    return actions


def _paired_plan(ball_count: int) -> list[str]:
    actions = []
    ball_index = 1
    while ball_index <= ball_count:
        first_ball = f"ball{ball_index}"
        actions.append(f"pick {first_ball} rooma right")
        if ball_index + 1 <= ball_count:
            second_ball = f"ball{ball_index + 1}"
            actions.append(f"pick {second_ball} rooma left")
        actions.append("move rooma roomb")
        actions.append(f"drop {first_ball} roomb right")
        if ball_index + 1 <= ball_count:
            actions.append(f"drop {second_ball} roomb left")
        if ball_index + 2 <= ball_count:
            actions.append("move roomb rooma")
        ball_index += 2
    return actions


def _numbered(lines: list[str]) -> str:
    return "\n".join(f"{index}. {line}" for index, line in enumerate(lines, start=1))


@dataclass
class DemoHeuristicLLM:
    """Deterministic local backend for smoke tests and replay-safe demo generation."""

    model_name: str = "demo-mock-gripper"

    def __call__(
        self,
        messages,
        temperature: float = 0.0,
        max_tokens: int = 512,
        stop_strs: list[str] | None = None,
        num_comps: int = 1,
    ) -> str:
        system_prompt = _content(messages, 0)
        user_prompt = _content(messages, 1)

        if "score the relevance between two pieces of text" in system_prompt:
            return self._score_relevance(user_prompt)
        if "extracting key points" in system_prompt:
            return self._extract_key_steps(user_prompt)
        if "failed trajectory" in system_prompt and "analytical agent" in system_prompt:
            return self._detect_mistake()
        if "advanced reasoning agent capable of deriving rules" in system_prompt:
            return self._compare_rules()
        if "advanced reasoning agent that can add, edit or remove rules" in system_prompt:
            return self._success_rules()
        if "skilled at summarizing and distilling insights" in system_prompt:
            return self._merge_rules(user_prompt)
        if "thoughtful and context-aware agent" in system_prompt:
            return self._project_insights(user_prompt)
        if "smart agent designed to solve problems" in system_prompt or "assist the solver agent" in system_prompt:
            return self._solve_task(user_prompt)

        return "think: Keep the plan short and consistent."

    def _score_relevance(self, user_prompt: str) -> str:
        return "9" if "ball" in user_prompt.lower() and "room" in user_prompt.lower() else "5"

    def _extract_key_steps(self, user_prompt: str) -> str:
        task_section = _extract_current_task_section(user_prompt)
        ball_count = _ball_count(task_section)
        if "ball" in user_prompt.lower():
            return _numbered(
                [
                    "Identify which balls still need to reach the target room.",
                    "Pick up one or two balls in rooma using the available grippers.",
                    "Move from rooma to roomb only after the intended pickup batch is ready.",
                    "Drop the carried balls in roomb and repeat until all goal conditions are satisfied.",
                ][: 3 if ball_count <= 2 else 4]
            )
        return _numbered(["Trace the successful actions and repeat the shortest reliable pattern."])

    def _detect_mistake(self) -> str:
        return "The agent wastes moves by transporting one object at a time, so it runs out of budget before satisfying every goal condition."

    def _success_rules(self) -> str:
        return "\n".join(
            [
                "ADD: Carry two transferable objects before moving between rooms, because batching transfers reduces wasted travel.",
                "ADD: Reuse both grippers when possible, because parallel pickups shorten the full interaction trajectory.",
            ]
        )

    def _compare_rules(self) -> str:
        return "\n".join(
            [
                "ADD: Batch pickups before changing rooms, because repeated back-and-forth movement creates avoidable plan failures.",
                "ADD: Use the second gripper whenever it is free, because single-arm transport underuses the available coordination capacity.",
            ]
        )

    def _merge_rules(self, user_prompt: str) -> str:
        candidate_lines = [
            "Batch pickups before changing rooms, because reducing repeated travel keeps the plan within budget.",
            "Use both grippers whenever possible, because parallel transport shortens the collaboration trajectory.",
        ]
        if "no more than 1" in user_prompt.lower():
            candidate_lines = candidate_lines[:1]
        return _numbered(candidate_lines)

    def _project_insights(self, user_prompt: str) -> str:
        role_match = re.search(r"### Agent's Role:\n(.+)", user_prompt)
        role = role_match.group(1).strip().lower() if role_match else "agent"
        if "ground truth" in role:
            return _numbered(
                [
                    "Recommend the two-gripper transfer pattern first, because your role is to break the solver out of inefficient loops.",
                    "Call out unnecessary room changes, because corrective guidance should focus on the main budget bottleneck.",
                ]
            )
        return _numbered(
            [
                "Carry two balls before moving rooms, because batching transfers keeps the solver inside the step budget.",
                "Treat both grippers as active resources, because unused capacity slows the plan unnecessarily.",
            ]
        )

    def _solve_task(self, user_prompt: str) -> str:
        task_section = _extract_current_task_section(user_prompt)
        ball_count = _ball_count(task_section)
        step_index = _completed_steps(task_section)
        has_memory = _has_memory(user_prompt)
        plan = _paired_plan(ball_count) if has_memory else _single_gripper_plan(ball_count)

        if step_index >= len(plan):
            return "check valid actions"
        return plan[step_index]
