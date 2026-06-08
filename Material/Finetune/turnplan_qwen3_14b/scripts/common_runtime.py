from __future__ import annotations

import json
import re
import sys
import time
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "customer-service-backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from atguigu.domain.messages import BotMessage, FocusedObject, MessageType, UserMessage  # noqa: E402
from atguigu.domain.state import DialogueState, Session, TaskOutcome, Turn, TurnRoute  # noqa: E402
from atguigu.domain.contexts import SystemContext, TaskContext  # noqa: E402
from atguigu.engine.builder import FLOW_CONFIG_DIR, FLOW_CONFIG_FILES  # noqa: E402
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS  # noqa: E402
from atguigu.task.flow.loader import FlowLoader  # noqa: E402


def load_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open("r", encoding="utf-8") if line.strip()]


def normalize_conversation_state(value: str | None) -> str:
    if not value:
        return "idle"
    return value.lower()


def build_turns_from_history(history: list[dict], resident_id: str) -> list[Turn]:
    turns: list[Turn] = []
    current_user: UserMessage | None = None
    current_bot_messages: list[BotMessage] = []

    for item in history:
        role = item["role"]
        text = item["text"]
        if role == "user":
            if current_user is not None:
                turns.append(
                    Turn(
                        turn_id=str(uuid.uuid4()),
                        user_message=current_user,
                        bot_messages=current_bot_messages,
                    )
                )
            current_user = UserMessage(
                resident_id=resident_id,
                message_id=str(uuid.uuid4()),
                type=MessageType.TEXT,
                text=text,
            )
            current_bot_messages = []
        else:
            if current_user is None:
                current_user = UserMessage(
                    resident_id=resident_id,
                    message_id=str(uuid.uuid4()),
                    type=MessageType.TEXT,
                    text="",
                )
            current_bot_messages.append(BotMessage(text=text))

    if current_user is not None:
        turns.append(
            Turn(
                turn_id=str(uuid.uuid4()),
                user_message=current_user,
                bot_messages=current_bot_messages,
            )
        )
    return turns


def build_last_route(payload: dict | None) -> TurnRoute | None:
    if not payload:
        return None
    if "kind" in payload and "event" in payload:
        return TurnRoute.from_dict(payload)
    track = payload.get("track")
    semantic_kind = payload.get("semantic_kind")
    return TurnRoute(
        kind=track or "unknown",
        event=track or "unknown",
        semantic_kind=semantic_kind,
    )


def build_last_task_outcome(payload: dict | None) -> TaskOutcome | None:
    if not payload:
        return None
    if "kind" in payload:
        return TaskOutcome.from_dict(payload)
    return TaskOutcome(
        kind=payload.get("semantic_kind", "unknown"),
        semantic_kind=payload.get("semantic_kind"),
    )


def build_active_system_task(payload: dict | None) -> SystemContext | None:
    if not payload:
        return None
    if "response" in payload or "slot_name" in payload:
        return SystemContext.from_dict(payload)
    if payload.get("flow_id") == "system_collect_information":
        target_slot = payload.get("slots", {}).get("target_slot", "")
        normalized = {
            "flow_id": "system_collect_information",
            "step_id": payload.get("step_id"),
            "slot_name": target_slot,
            "response": {},
        }
        return SystemContext.from_dict(normalized)
    return SystemContext.from_dict(
        {
            "flow_id": payload["flow_id"],
            "step_id": payload.get("step_id"),
        }
    )


def build_state_from_input(input_payload: dict, resident_id: str = "turnplan_eval_resident") -> DialogueState:
    turns = build_turns_from_history(input_payload.get("history", []), resident_id=resident_id)
    session = Session(
        session_id="eval_session",
        started_at=time.time(),
        last_activity_at=time.time(),
        turns=turns,
    )
    runtime_state = input_payload.get("runtime_state", {})
    state = DialogueState(
        resident_id=resident_id,
        active_task=_build_task_context(input_payload.get("active_task")),
        paused_tasks=[task for task in (_build_task_context(item) for item in input_payload.get("paused_tasks", [])) if task is not None],
        active_system_task=build_active_system_task(input_payload.get("active_system_task")),
        focused_object=FocusedObject.from_dict(input_payload["focused_object"]) if input_payload.get("focused_object") else None,
        conversation_state=normalize_conversation_state(runtime_state.get("conversation_state")),
        last_route=build_last_route(runtime_state.get("last_route")),
        last_task_outcome=build_last_task_outcome(runtime_state.get("last_task_outcome")),
        sessions=[session],
        current_session_id=session.session_id,
    )
    state.pending_turn = Turn(
        turn_id="pending_turn",
        user_message=UserMessage(
            resident_id=resident_id,
            message_id="pending_message",
            type=MessageType.TEXT,
            text=input_payload["user_message"],
        ),
        bot_messages=[],
    )
    return state


def _build_task_context(payload: dict | None) -> TaskContext | None:
    if not payload:
        return None
    if "slots" in payload:
        return TaskContext.from_dict(payload)
    return TaskContext(
        flow_id=payload["flow_id"],
        step_id=payload.get("step_id"),
        slots=dict(payload.get("filled_slots") or {}),
    )


def turnplan_to_dict(turn_plan: Any) -> dict:
    if turn_plan is None:
        return {
            "task": None,
            "knowledge": None,
            "chitchat": None,
            "directive": None,
        }

    task_payload = None
    if getattr(turn_plan, "task", None) is not None:
        task_payload = {
            "commands": [command_to_dict(command) for command in turn_plan.task.commands]
        }

    knowledge_payload = None
    if getattr(turn_plan, "knowledge", None) is not None:
        knowledge_payload = {
            "intents": list(turn_plan.knowledge.intents)
        }

    chitchat_payload = None
    if getattr(turn_plan, "chitchat", None) is not None:
        chitchat_payload = {}

    directive_payload = None
    if getattr(turn_plan, "directive", None) is not None:
        directive_payload = {"action": turn_plan.directive.action}

    return {
        "task": task_payload,
        "knowledge": knowledge_payload,
        "chitchat": chitchat_payload,
        "directive": directive_payload,
    }


def command_to_dict(command: Any) -> dict:
    if is_dataclass(command):
        payload = asdict(command)
    else:
        payload = dict(command.__dict__)
    if payload.get("flow") is None:
        payload.pop("flow", None)
    if payload.get("slots") is None:
        payload.pop("slots", None)
    return payload


def active_track(output_payload: dict) -> str:
    active = [name for name, value in output_payload.items() if value is not None]
    if not active:
        return "all_null"
    if len(active) > 1:
        return "multiple"
    return active[0]


def extract_command_names(output_payload: dict) -> list[str]:
    task = output_payload.get("task")
    if not task:
        return []
    return [item["command"] for item in task.get("commands", [])]


def extract_flow_sequence(output_payload: dict) -> list[str]:
    task = output_payload.get("task")
    if not task:
        return []
    flows = []
    for item in task.get("commands", []):
        if item["command"] in {"start_flow", "resume_flow"} and item.get("flow"):
            flows.append(item["flow"])
    return flows


def extract_merged_slots(output_payload: dict) -> dict[str, Any]:
    task = output_payload.get("task")
    if not task:
        return {}
    merged: dict[str, Any] = {}
    for item in task.get("commands", []):
        if item["command"] == "set_slots":
            merged.update(item.get("slots", {}))
    return merged


def parse_json_text(raw_text: str) -> tuple[dict | None, str | None]:
    try:
        return json.loads(raw_text), None
    except json.JSONDecodeError:
        pass

    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
        try:
            return json.loads(stripped), None
        except json.JSONDecodeError:
            pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start >= 0 and end > start:
        candidate = raw_text[start:end + 1]
        try:
            return json.loads(candidate), None
        except json.JSONDecodeError as exc:
            return None, str(exc)
    return None, "no valid json object found"


def build_bucket_metrics(bucket_predictions: list[dict]) -> dict[str, Any]:
    total = len(bucket_predictions)
    if total == 0:
        return {
            "count": 0,
            "track_accuracy": 0.0,
            "json_valid_rate": 0.0,
            "protocol_gate_pass_rate": 0.0,
            "effective_protocol_gate_pass_rate": 0.0,
        }
    track_matches = sum(item["track_match"] for item in bucket_predictions)
    json_valid = sum(item["json_valid"] for item in bucket_predictions)
    gate_pass = sum(item["protocol_gate_accepted"] for item in bucket_predictions)
    effective_gate_pass = sum(item.get("effective_gate_pass", item["protocol_gate_accepted"]) for item in bucket_predictions)
    return {
        "count": total,
        "track_accuracy": track_matches / total,
        "json_valid_rate": json_valid / total,
        "protocol_gate_pass_rate": gate_pass / total,
        "effective_protocol_gate_pass_rate": effective_gate_pass / total,
    }


def load_flows_and_intents():
    flows = FlowLoader().load_many([FLOW_CONFIG_DIR / file_name for file_name in FLOW_CONFIG_FILES])
    return flows, KNOWLEDGE_INTENTS
