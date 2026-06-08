from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from reduced_round04_contract import CANONICAL_LLM_DIR, DATASET_ROOT


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_canonical_records(bucket: str | None = None) -> list[dict]:
    rows = load_jsonl(CANONICAL_LLM_DIR / "records_train.jsonl")
    rows.extend(load_jsonl(CANONICAL_LLM_DIR / "records_val.jsonl"))
    if bucket is None:
        return rows
    return [row for row in rows if row["bucket"] == bucket]


def clone_record(record: dict) -> dict:
    return deepcopy(record)


def stable_pick(options: list[str] | tuple[str, ...], record_id: str, salt: str = "") -> str:
    joined = f"{record_id}:{salt}"
    index = sum(ord(ch) for ch in joined) % len(options)
    return options[index]


def append_curation_note(record: dict, note: str) -> None:
    meta = dict(record.get("meta", {}))
    notes = list(meta.get("curation_notes", []))
    if note not in notes:
        notes.append(note)
    meta["curation_notes"] = notes
    record["meta"] = meta


def set_history(record: dict, messages: list[tuple[str, str]]) -> None:
    record["input"]["history"] = [{"role": role, "text": text} for role, text in messages]


def get_target_slot(record: dict) -> str | None:
    active_system_task = record["input"].get("active_system_task") or {}
    slots = active_system_task.get("slots") or {}
    return active_system_task.get("slot_name") or slots.get("target_slot")


def first_task_command(record: dict) -> dict | None:
    task_payload = record["output"].get("task") or {}
    commands = task_payload.get("commands") or []
    return commands[0] if commands else None


def extract_slot(record: dict, slot_name: str) -> str | None:
    command = first_task_command(record)
    if not command or command.get("command") != "set_slots":
        return None
    slots = command.get("slots") or {}
    value = slots.get(slot_name)
    if value is None:
        return None
    return str(value)


def extract_slots(record: dict) -> dict:
    command = first_task_command(record)
    if not command or command.get("command") != "set_slots":
        return {}
    return dict(command.get("slots") or {})


def focused_title(record: dict, fallback: str = "这个") -> str:
    focused_object = record["input"].get("focused_object") or {}
    return str(focused_object.get("title") or fallback)


def dataset_output_dir(name: str) -> Path:
    return DATASET_ROOT / name
