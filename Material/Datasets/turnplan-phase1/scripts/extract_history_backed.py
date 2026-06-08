from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dataset_contract import HISTORY_DIR


def flatten_candidate_turns(state_dict: dict) -> list[dict]:
    resident_id = state_dict.get("resident_id") or state_dict.get("sender_id")
    sessions = state_dict.get("sessions") or []
    candidates: list[dict] = []
    for session in sessions:
        turns = session.get("turns") or []
        if len(turns) < 4:
            continue
        running_history: list[dict] = []
        for index, turn in enumerate(turns):
            user_message = (turn.get("user_message") or {}).get("text")
            bot_messages = turn.get("bot_messages") or []
            bot_text = next((message.get("text") for message in bot_messages if message.get("text")), None)
            if user_message:
                running_history.append({"role": "user", "text": user_message})
            if bot_text:
                running_history.append({"role": "assistant", "text": bot_text})
            if len(running_history) < 8:
                continue
            candidate = {
                "resident_id": resident_id,
                "session_id": session.get("id"),
                "turn_index": index,
                "history": running_history[-8:],
                "focused_object": turn.get("focused_object"),
                "active_task": turn.get("active_task"),
                "active_system_task": turn.get("active_system_task"),
                "paused_tasks": turn.get("paused_tasks") or [],
            }
            candidates.append(candidate)
    return candidates


async def read_states_from_db(limit: int | None) -> list[dict]:
    backend_root = Path(__file__).resolve().parents[4] / "customer-service-backend"
    sys.path.insert(0, str(backend_root))
    from atguigu.config.config import settings
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(settings.database_url, echo=False)
    query = "SELECT resident_id, state_json FROM dialogue_states"
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        rows = result.fetchall()
    await engine.dispose()
    states = []
    for resident_id, state_json in rows:
        payload = json.loads(state_json)
        if "resident_id" not in payload:
            payload["resident_id"] = resident_id
        states.append(payload)
    return states


def read_states_from_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


async def main_async(args) -> None:
    if args.from_db:
        states = await read_states_from_db(args.limit)
    else:
        states = read_states_from_jsonl(Path(args.input_jsonl))
    candidates: list[dict] = []
    for state in states:
        candidates.extend(flatten_candidate_turns(state))
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(HISTORY_DIR / "history_candidates.jsonl", candidates)
    print(json.dumps({"states": len(states), "candidates": len(candidates), "output": str(HISTORY_DIR / 'history_candidates.jsonl')}, ensure_ascii=False, indent=2))


def parse_args():
    parser = argparse.ArgumentParser(description="Extract history-backed long-dialogue candidates.")
    parser.add_argument("--from-db", action="store_true", help="Read dialogue_states directly from the configured MySQL database.")
    parser.add_argument("--input-jsonl", help="Read exported state_json snapshots from a JSONL file.")
    parser.add_argument("--limit", type=int, default=None, help="Optional LIMIT for database extraction.")
    args = parser.parse_args()
    if not args.from_db and not args.input_jsonl:
        parser.error("Either --from-db or --input-jsonl is required.")
    return args


if __name__ == "__main__":
    asyncio.run(main_async(parse_args()))
