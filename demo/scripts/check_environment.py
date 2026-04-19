from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_ROOT = PROJECT_ROOT / "official_gmemory"


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def status_line(ok: bool, label: str, detail: str) -> str:
    marker = "[OK]" if ok else "[MISSING]"
    return f"{marker} {label}: {detail}"


def main() -> int:
    print("G-Memory Poster Demo Environment Check")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Official repo: {OFFICIAL_ROOT}")
    print()

    checks: list[bool] = []

    repo_ok = OFFICIAL_ROOT.exists()
    checks.append(repo_ok)
    print(status_line(repo_ok, "official repo", "found" if repo_ok else "official_gmemory/ is missing"))

    data_paths = {
        "pddl": OFFICIAL_ROOT / "data/pddl/test.jsonl",
        "fever": OFFICIAL_ROOT / "data/fever/fever_dev.jsonl",
        "sciworld": OFFICIAL_ROOT / "data/sciworld/test.jsonl",
    }
    for name, path in data_paths.items():
        ok = path.exists()
        checks.append(ok)
        print(status_line(ok, f"dataset:{name}", str(path)))

    print()
    mock_modules = ["yaml", "jsonlines", "networkx", "matplotlib", "pandas", "nbformat", "numpy", "attr"]
    mock_ready = True
    for module_name in mock_modules:
        ok = has_module(module_name)
        mock_ready &= ok
        print(status_line(ok, f"python:{module_name}", "importable" if ok else "install required"))

    print()
    openai_ready = has_module("openai") and bool(os.getenv("OPENAI_API_BASE")) and bool(os.getenv("OPENAI_API_KEY"))
    print(status_line(has_module("openai"), "python:openai", "importable" if has_module("openai") else "install required"))
    print(status_line(bool(os.getenv("OPENAI_API_BASE")), "env:OPENAI_API_BASE", "set" if os.getenv("OPENAI_API_BASE") else "not set"))
    print(status_line(bool(os.getenv("OPENAI_API_KEY")), "env:OPENAI_API_KEY", "set" if os.getenv("OPENAI_API_KEY") else "not set"))

    print()
    heavy_optional = ["langchain_chroma", "sentence_transformers", "finch"]
    for module_name in heavy_optional:
        print(status_line(has_module(module_name), f"optional:{module_name}", "available" if has_module(module_name) else "demo fallback will use simple mode"))

    print()
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print()
    print(f"Mock demo ready: {'yes' if repo_ok and mock_ready else 'no'}")
    print(f"OpenAI live mode ready: {'yes' if repo_ok and mock_ready and openai_ready else 'no'}")

    if not (repo_ok and mock_ready):
        print()
        print("Recommended next step:")
        print("  pip install -r demo/requirements-demo.txt")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
