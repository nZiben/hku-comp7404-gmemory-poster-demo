from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGET = PROJECT_ROOT / "official_gmemory"
DEFAULT_REPO = "https://github.com/bingreeky/GMemory.git"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch the official G-Memory repository into the expected local path.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO)
    parser.add_argument("--target-dir", default=str(DEFAULT_TARGET))
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()
    if (target_dir / ".git").exists() or (target_dir / "README.md").exists():
        print(f"Official repo already present: {target_dir}")
        return 0

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    print(f"Cloning {args.repo_url} into {target_dir}")
    try:
        subprocess.run(
            ["git", "clone", args.repo_url, str(target_dir)],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print("Clone failed.", file=sys.stderr)
        print(
            f"Please run manually: git clone {args.repo_url} {target_dir}",
            file=sys.stderr,
        )
        return exc.returncode

    print(f"Official repo ready: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
