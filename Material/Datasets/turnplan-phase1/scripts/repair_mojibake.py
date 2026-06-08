from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def maybe_fix_mojibake(text: str) -> tuple[str, bool]:
    """Fix common latin1-decoded UTF-8 mojibake conservatively."""
    try:
        candidate = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text, False

    if candidate == text:
        return text, False

    source_latin_noise = sum(1 for ch in text if 0x80 <= ord(ch) <= 0xFF)
    candidate_latin_noise = sum(1 for ch in candidate if 0x80 <= ord(ch) <= 0xFF)
    source_cjk = sum(1 for ch in text if 0x4E00 <= ord(ch) <= 0x9FFF)
    candidate_cjk = sum(1 for ch in candidate if 0x4E00 <= ord(ch) <= 0x9FFF)

    # Only accept the repaired text when it is clearly more human-readable.
    if candidate_latin_noise < source_latin_noise and candidate_cjk >= source_cjk:
        return candidate, True
    return text, False


def repair_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, str):
        fixed, changed = maybe_fix_mojibake(value)
        return fixed, int(changed)
    if isinstance(value, list):
        items = []
        changed = 0
        for item in value:
            fixed_item, item_changed = repair_value(item)
            items.append(fixed_item)
            changed += item_changed
        return items, changed
    if isinstance(value, dict):
        items: dict[str, Any] = {}
        changed = 0
        for key, item in value.items():
            fixed_item, item_changed = repair_value(item)
            items[key] = fixed_item
            changed += item_changed
        return items, changed
    return value, 0


def repair_jsonl(path: Path) -> dict[str, int]:
    rows = [json.loads(line) for line in path.open("r", encoding="utf-8") if line.strip()]
    total_changes = 0
    repaired_rows = []
    for row in rows:
        repaired_row, changed = repair_value(row)
        repaired_rows.append(repaired_row)
        total_changes += changed

    if total_changes:
        with path.open("w", encoding="utf-8") as handle:
            for row in repaired_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {"rows": len(rows), "changed_strings": total_changes}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair mojibake in canonical TurnPlan records.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "canonical_llm",
        help="Directory containing records_train.jsonl / records_val.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = {}
    for name in ("records_train.jsonl", "records_val.jsonl"):
        path = args.input_dir / name
        if not path.exists():
            raise FileNotFoundError(path)
        results[name] = repair_jsonl(path)
    print(json.dumps({"input_dir": str(args.input_dir), "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
