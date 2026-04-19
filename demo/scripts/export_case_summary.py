from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo.utils.caching import ensure_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a compact markdown summary from a compare JSON record.")
    parser.add_argument("--compare-json", required=True)
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "demo/outputs/summaries"))
    args = parser.parse_args()

    compare_record = json.loads(Path(args.compare_json).read_text(encoding="utf-8"))
    compare_payload = compare_record["compare_payload"]
    output_dir = ensure_dir(args.output_dir)
    output_path = output_dir / (Path(args.compare_json).stem + ".md")

    markdown = "\n".join(
        [
            f"# {compare_record['run_id']}",
            "",
            f"- Backend: `{compare_record['backend']}`",
            f"- Task: `{compare_record['scenario']['task']}`",
            f"- MAS type: `{compare_record['scenario']['mas_type']}`",
            f"- Delta summary: {compare_payload['delta_summary']}",
            "",
            "## No Memory",
            f"- reward={compare_payload['no_memory']['final_reward']}, done={compare_payload['no_memory']['final_done']}",
            f"- feedback: {compare_payload['no_memory']['final_feedback']}",
            "",
            "## G-Memory",
            f"- reward={compare_payload['gmemory']['final_reward']}, done={compare_payload['gmemory']['final_done']}",
            f"- feedback: {compare_payload['gmemory']['final_feedback']}",
            f"- retrieved queries: {len(compare_payload['gmemory']['retrieved_historical_queries'])}",
            f"- selected insights: {len(compare_payload['gmemory']['selected_insights'])}",
        ]
    )
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Exported summary: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
