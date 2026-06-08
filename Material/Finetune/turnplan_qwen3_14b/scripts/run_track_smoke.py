from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path
from typing import Any

from common_runtime import REPO_ROOT, build_state_from_input

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.plan.turn_plan import ClarifyContext, ClarifyReason, KnowledgeTurnPlan


DEFAULT_CASES = REPO_ROOT / "Material" / "Finetune" / "turnplan_qwen3_14b" / "smoke" / "smoke_cases.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run smoke prompts through real clarify/knowledge/chitchat handlers.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label", default="unnamed")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_clarify_context(payload: dict | None) -> ClarifyContext | None:
    if payload is None:
        return None
    source = payload.get("source")
    if source == "object":
        return ClarifyContext.for_object_intent()
    reason = payload.get("reason")
    if reason is None:
        return None
    return ClarifyContext.for_validation(ClarifyReason(reason))


def looks_like_json(text: str) -> bool:
    if "```" in text:
        return True
    if re.search(r'"\s*(task|knowledge|chitchat|directive|command|slots)\s*"\s*:', text):
        return True
    if re.search(r"\{[\s\S]{0,120}\}", text):
        return True
    return False


def build_flags(text: str) -> dict[str, bool]:
    stripped = text.strip()
    lowered = stripped.lower()
    return {
        "json_like": looks_like_json(stripped),
        "too_short": len(stripped) < 8,
        "hard_tone": any(token in stripped for token in ["字段", "JSON", "command", "slot", "格式"]),
        "refusal_like": any(token in lowered for token in ["cannot", "can't", "sorry"]) or "无法" in stripped,
    }


async def run_case(case: dict, clarify_responder: ClarifyResponder, knowledge_handler: KnowledgeHandler, chitchat_handler: ChitchatHandler) -> dict:
    state = build_state_from_input(case["context"])
    track = case["track"]
    if track == "clarify":
        messages = await clarify_responder.respond(state, build_clarify_context(case.get("clarify_context")))
    elif track == "knowledge":
        messages = knowledge_handler.handle(
            state=state,
            turn_plan=KnowledgeTurnPlan(intents=list(case.get("knowledge_intents", []))),
        )
    elif track == "chitchat":
        messages = chitchat_handler.handle(state=state)
    else:
        raise ValueError(f"unsupported track: {track}")

    text = "\n".join(message.text or "" for message in messages).strip()
    return {
        "id": case["id"],
        "track": track,
        "notes": case.get("notes"),
        "user_message": case["context"]["user_message"],
        "response_text": text,
        "flags": build_flags(text),
    }


def build_summary(label: str, results: list[dict]) -> str:
    lines = [
        f"# Track Smoke - {label}",
        "",
        "| id | track | json_like | too_short | hard_tone | refusal_like |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        flags = item["flags"]
        lines.append(
            f"| {item['id']} | {item['track']} | {flags['json_like']} | {flags['too_short']} | {flags['hard_tone']} | {flags['refusal_like']} |"
        )

    lines.extend(["", "## Outputs", ""])
    for item in results:
        lines.append(f"### {item['id']} ({item['track']})")
        lines.append(f"- user: {item['user_message']}")
        lines.append(f"- notes: {item.get('notes') or ''}")
        lines.append(f"- reply: {item['response_text']}")
        lines.append("")
    return "\n".join(lines)


async def main() -> None:
    args = parse_args()
    cases = load_cases(args.cases)
    if args.limit > 0:
        cases = cases[: args.limit]

    clarify_responder = ClarifyResponder()
    knowledge_handler = KnowledgeHandler(knowledge_intents=KNOWLEDGE_INTENTS)
    chitchat_handler = ChitchatHandler()

    results = []
    for case in cases:
        results.append(await run_case(case, clarify_responder, knowledge_handler, chitchat_handler))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "summary.md").write_text(build_summary(args.label, results), encoding="utf-8")
    print(json.dumps({"label": args.label, "cases": len(results), "output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
