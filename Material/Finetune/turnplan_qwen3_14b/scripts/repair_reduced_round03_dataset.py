from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
DEFAULT_INPUT_DIR = DATASET_ROOT / "reduced_round03_curated_v1"
DEFAULT_OUTPUT_DIR = DATASET_ROOT / "reduced_round03_repair_v1"

# These are the most knowledge-shaped all-null rows from the candidate fail set.
# The reduced round_03 goal is no longer to maximize this bucket at the cost of
# active-context task handling, so we trim the noisiest train examples.
DROP_IDS = {
    "tp_ambiguous_all_null_train_006",
    "tp_ambiguous_all_null_train_008",
    "tp_ambiguous_all_null_train_010",
    "tp_ambiguous_all_null_train_013",
    "tp_ambiguous_all_null_train_016",
    "tp_ambiguous_all_null_train_017",
    "tp_ambiguous_all_null_train_019",
    "tp_ambiguous_all_null_train_021",
    "tp_ambiguous_all_null_train_029",
    "tp_ambiguous_all_null_train_030",
    "tp_ambiguous_all_null_train_032",
    "tp_ambiguous_all_null_train_033",
    "tp_r3_ambiguous_all_null_train_036",
    "tp_r3_ambiguous_all_null_train_040",
    "tp_r3_ambiguous_all_null_train_043",
    "tp_r3_ambiguous_all_null_train_045",
    "tp_r3_ambiguous_all_null_train_047",
    "tp_r3_ambiguous_all_null_train_049",
    "tp_r3_ambiguous_all_null_train_050",
    "tp_r3_ambiguous_all_null_train_052",
}

RULE_TOPIC_USER_TEMPLATES = (
    "{value}",
    "{value}这块",
    "就{value}这个",
    "先看{value}",
    "{value}相关的",
)

SERVICE_ITEM_USER_TEMPLATES = (
    "{title}",
    "就{title}这个",
    "{title}这项",
    "先看{title}",
    "查{title}这个",
)

RULE_TOPIC_ASSISTANT_TEMPLATES = (
    "你直接说下想问哪一类就行。",
    "你告诉我具体是哪一项就行。",
    "你直接说下是哪个规则主题。",
)

SERVICE_ITEM_ASSISTANT_TEMPLATES = (
    "你直接说项目名就行。",
    "你告诉我具体是哪个服务项目。",
    "你把项目名称说一下就行。",
)

CANCEL_USER_TEMPLATES = (
    "这条投诉先撤掉吧，先别往下提了。",
    "这个投诉先停一下，后面要不要再提我再说。",
    "这单先别继续投诉了，先放一放。",
    "先别往下提投诉了，我再想想。",
    "{title}这个先别投诉了，先到这吧。",
)

CANCEL_ASSISTANT_TEMPLATES = (
    "那这条投诉还继续往下提吗？",
    "这个投诉还继续提交吗？",
    "这单的投诉要不要继续走下去？",
)

RESUME_USER_TEMPLATES = (
    "还是接着{title}这个弄吧。",
    "刚才那个{title}继续吧。",
    "先把{title}这个接着办完。",
    "就继续刚才这个，别换了。",
)

RESUME_ASSISTANT_TEMPLATES = (
    "行，你要继续的话我们就接着这个。",
    "好，那我继续按刚才这个往下走。",
    "没问题，我们就继续这件事。",
)

RULE_TOPIC_VARIANTS = (
    "{value}",
    "{value}这块",
    "就说{value}",
    "先看{value}",
    "{value}相关的",
    "想问{value}",
    "{value}这一项",
    "先聊{value}",
    "我说的是{value}",
)

SERVICE_ITEM_VARIANTS = (
    "{title}",
    "{title}这项",
    "就{title}",
    "先看{title}",
    "{title}这个项目",
    "我说的是{title}",
    "{title}这一项",
    "先查{title}",
    "还是看{title}",
)

CANCEL_VARIANTS = (
    "这个投诉先停一下，后面要不要再提我再说。",
    "这条投诉先撤掉吧，先别往下提了。",
    "这单先别继续投诉了，先放一放。",
    "先别往下提投诉了，我再想想。",
    "{title}这个先别投诉了，先到这吧。",
    "这事先别按投诉往下走了。",
    "这个先别继续往投诉那边走了。",
    "先把这条投诉收住，后面再看。",
    "这回先不提投诉了，先搁一下。",
    "先停在这吧，这个投诉我暂时不往下弄。",
    "这单投诉先别提交了，我再想想。",
    "这个投诉先压一压，回头再说。",
)

RESUME_VARIANTS = (
    "就继续刚才这个，别换了。",
    "还是接着{title}这个弄吧。",
    "刚才那个{title}继续吧。",
    "先把{title}这个接着办完。",
    "这个先接着往下弄。",
    "还是说回{title}这个吧。",
    "刚才这件事继续就行。",
    "先按刚才这个接着来。",
    "{title}这个接着往下办。",
    "别换了，还是这个继续。",
    "就沿着刚才这件事往下走。",
    "这个先继续，别岔开。",
)

FORCED_USER_MESSAGE_OVERRIDES = {
    "tp_task_interrupt_resume_cancel_train_004": "那就接着说卫生间排风那单吧。",
    "tp_r3_task_interrupt_resume_cancel_val_008": "车位地锁那个，咱们继续。",
    "tp_task_interrupt_resume_cancel_train_005": "这事先算了，投诉先不提。",
    "tp_task_interrupt_resume_cancel_train_021": "北卧窗框那单先别投诉了。",
    "tp_r3_task_interrupt_resume_cancel_train_052": "阳台窗轨那个先压着吧。",
    "tp_r3_task_interrupt_resume_cancel_train_059": "厨房渗水这个先不走投诉了。",
    "tp_r3_task_interrupt_resume_cancel_val_017": "投诉先收一收，晚点再说。",
    "tp_task_interrupt_resume_cancel_train_017": "这个先别递投诉了。",
    "tp_r3_task_interrupt_resume_cancel_train_061": "我先不追这个投诉了。",
    "tp_r3_task_interrupt_resume_cancel_val_013": "先不往投诉那边走了。",
    "tp_task_interrupt_resume_cancel_train_020": "车位地锁那单继续催。",
    "tp_r3_task_interrupt_resume_cancel_train_058": "继续盯车位地锁那个。",
    "tp_task_interrupt_resume_cancel_train_025": "厨房渗水那事先别投诉。",
    "tp_r3_task_interrupt_resume_cancel_train_049": "等报价出来再决定投不投诉。",
    "tp_r3_task_interrupt_resume_cancel_train_057": "先搁这儿吧，不投诉了。",
    "tp_r3_task_interrupt_resume_cancel_train_077": "这回先别提投诉了。",
    "tp_task_interrupt_resume_cancel_train_029": "阳台窗轨这单先不提投诉。",
    "tp_r3_task_interrupt_resume_cancel_val_010": "投诉先放放，回头再说。",
    "tp_task_interrupt_resume_cancel_train_032": "车位地锁那个继续催着。",
    "tp_r3_task_interrupt_resume_cancel_val_015": "那个车位地锁的催办接着来。",
    "tp_task_interrupt_resume_cancel_train_036": "主卧空调那单接着催。",
    "tp_r3_task_interrupt_resume_cancel_train_067": "空调不制冷那单继续跟一下。",
    "tp_r3_task_interrupt_resume_cancel_train_068": "阳台窗轨这边先不走投诉。",
    "tp_task_interrupt_resume_cancel_val_001": "投诉这个先搁一下吧。",
    "tp_r3_task_interrupt_resume_cancel_train_070": "车位地锁那边继续往下办。",
    "tp_task_interrupt_resume_cancel_val_004": "车位地锁那个事接着办。",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def stable_choice(options: tuple[str, ...], record_id: str) -> str:
    return options[sum(ord(ch) for ch in record_id) % len(options)]


def append_curation_note(record: dict, note: str) -> None:
    meta = dict(record.get("meta", {}))
    notes = list(meta.get("curation_notes", []))
    if note not in notes:
        notes.append(note)
    meta["curation_notes"] = notes
    record["meta"] = meta


def extract_slot_value(record: dict, slot_name: str) -> str | None:
    task = record["output"].get("task") or {}
    for command in task.get("commands", []):
        if command.get("command") == "set_slots":
            slots = command.get("slots", {})
            if slot_name in slots:
                return str(slots[slot_name])
    return None


def patch_active_context_slot_fill(record: dict) -> bool:
    active_system_task = record["input"].get("active_system_task") or {}
    target_slot = ((active_system_task.get("slots") or {}).get("target_slot"))
    history = list(record["input"].get("history") or [])

    if target_slot == "rule_topic":
        slot_value = extract_slot_value(record, "rule_topic")
        if not slot_value:
            return False
        template = stable_choice(RULE_TOPIC_USER_TEMPLATES, record["id"])
        record["input"]["user_message"] = template.format(value=slot_value)
        if history and history[-1]["role"] == "assistant":
            history[-1]["text"] = stable_choice(RULE_TOPIC_ASSISTANT_TEMPLATES, record["id"])
        record["input"]["history"] = history
        append_curation_note(record, "repair_v1_active_slot_rule_topic")
        return True

    if target_slot == "service_item_id":
        focused_object = record["input"].get("focused_object") or {}
        title = focused_object.get("title")
        if not title:
            return False
        template = stable_choice(SERVICE_ITEM_USER_TEMPLATES, record["id"])
        record["input"]["user_message"] = template.format(title=title)
        if history and history[-1]["role"] == "assistant":
            history[-1]["text"] = stable_choice(SERVICE_ITEM_ASSISTANT_TEMPLATES, record["id"])
        record["input"]["history"] = history
        append_curation_note(record, "repair_v1_active_slot_service_item")
        return True

    return False


def patch_interrupt_resume_cancel(record: dict) -> bool:
    task = record["output"].get("task") or {}
    commands = [item.get("command") for item in task.get("commands", [])]
    history = list(record["input"].get("history") or [])
    focused_object = record["input"].get("focused_object") or {}
    title = focused_object.get("title", "这个")

    if commands == ["cancel_flow"]:
        template = stable_choice(CANCEL_USER_TEMPLATES, record["id"])
        record["input"]["user_message"] = template.format(title=title)
        if history and history[-1]["role"] == "assistant":
            history[-1]["text"] = stable_choice(CANCEL_ASSISTANT_TEMPLATES, record["id"])
        append_curation_note(record, "repair_v1_cancel_flow_boundary")
        record["input"]["history"] = history
        return True

    if commands == ["resume_flow"]:
        template = stable_choice(RESUME_USER_TEMPLATES, record["id"])
        record["input"]["user_message"] = template.format(title=title)
        if history and history[-1]["role"] == "assistant":
            history[-1]["text"] = stable_choice(RESUME_ASSISTANT_TEMPLATES, record["id"])
        append_curation_note(record, "repair_v1_resume_flow_boundary")
        record["input"]["history"] = history
        return True

    return False


def retouch_duplicate_message(record: dict, occurrence_index: int) -> bool:
    bucket = record["bucket"]
    active_system_task = record["input"].get("active_system_task") or {}
    target_slot = ((active_system_task.get("slots") or {}).get("target_slot"))
    focused_object = record["input"].get("focused_object") or {}
    title = focused_object.get("title", "这个")
    task = record["output"].get("task") or {}
    commands = [item.get("command") for item in task.get("commands", [])]

    if bucket == "active_task_slot_fill" and target_slot == "rule_topic":
        value = extract_slot_value(record, "rule_topic")
        if value:
            record["input"]["user_message"] = RULE_TOPIC_VARIANTS[occurrence_index % len(RULE_TOPIC_VARIANTS)].format(value=value)
            append_curation_note(record, "repair_v1_dedup_rule_topic")
            return True

    if bucket == "active_task_slot_fill" and target_slot == "service_item_id":
        record["input"]["user_message"] = SERVICE_ITEM_VARIANTS[occurrence_index % len(SERVICE_ITEM_VARIANTS)].format(title=title)
        append_curation_note(record, "repair_v1_dedup_service_item")
        return True

    if bucket == "task_interrupt_resume_cancel" and commands == ["cancel_flow"]:
        record["input"]["user_message"] = CANCEL_VARIANTS[occurrence_index % len(CANCEL_VARIANTS)].format(title=title)
        append_curation_note(record, "repair_v1_dedup_cancel_flow")
        return True

    if bucket == "task_interrupt_resume_cancel" and commands == ["resume_flow"]:
        record["input"]["user_message"] = RESUME_VARIANTS[occurrence_index % len(RESUME_VARIANTS)].format(title=title)
        append_curation_note(record, "repair_v1_dedup_resume_flow")
        return True

    return False


def build_message_variants(record: dict) -> list[str]:
    bucket = record["bucket"]
    active_system_task = record["input"].get("active_system_task") or {}
    target_slot = ((active_system_task.get("slots") or {}).get("target_slot"))
    focused_object = record["input"].get("focused_object") or {}
    title = focused_object.get("title", "这个")
    task = record["output"].get("task") or {}
    commands = [item.get("command") for item in task.get("commands", [])]

    variants: list[str] = []
    if bucket == "active_task_slot_fill" and target_slot == "rule_topic":
        value = extract_slot_value(record, "rule_topic")
        if value:
            variants = [template.format(value=value) for template in RULE_TOPIC_VARIANTS]

    elif bucket == "active_task_slot_fill" and target_slot == "service_item_id":
        variants = [template.format(title=title) for template in SERVICE_ITEM_VARIANTS]

    elif bucket == "task_interrupt_resume_cancel" and commands == ["cancel_flow"]:
        variants = [template.format(title=title) for template in CANCEL_VARIANTS]

    elif bucket == "task_interrupt_resume_cancel" and commands == ["resume_flow"]:
        variants = [template.format(title=title) for template in RESUME_VARIANTS]

    return variants


def dedupe_user_messages(rows: list[dict]) -> int:
    counts = Counter(row["input"]["user_message"] for row in rows)
    used_messages = set(counts.keys())
    changed = 0

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["input"]["user_message"]].append(row)

    for message, items in grouped.items():
        if len(items) <= 1:
            continue
        for occurrence_index, row in enumerate(items[1:], start=1):
            original = row["input"]["user_message"]
            variants = build_message_variants(row)
            replacement = None
            for candidate in variants:
                if candidate != original and candidate not in used_messages:
                    replacement = candidate
                    break
            if replacement is None and retouch_duplicate_message(row, occurrence_index):
                replacement = row["input"]["user_message"]
            if replacement and replacement != original:
                row["input"]["user_message"] = replacement
                used_messages.add(replacement)
                append_curation_note(row, "repair_v1_global_dedup")
                changed += 1
    return changed


def collect_duplicate_user_messages(rows: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[row["input"]["user_message"]].append(row["id"])
    return {message: ids for message, ids in grouped.items() if len(ids) > 1}


def repair_record(record: dict) -> tuple[dict | None, list[str]]:
    cloned = json.loads(json.dumps(record, ensure_ascii=False))
    actions: list[str] = []
    if cloned["id"] in DROP_IDS:
        return None, ["dropped"]

    if cloned["bucket"] == "active_task_slot_fill":
        if patch_active_context_slot_fill(cloned):
            actions.append("patched_active_context_slot_fill")

    if cloned["bucket"] == "task_interrupt_resume_cancel":
        if patch_interrupt_resume_cancel(cloned):
            actions.append("patched_interrupt_resume_cancel")

    override = FORCED_USER_MESSAGE_OVERRIDES.get(cloned["id"])
    if override:
        cloned["input"]["user_message"] = override
        append_curation_note(cloned, "repair_v1_forced_user_message_override")
        actions.append("forced_user_message_override")

    return cloned, actions


def build_summary(rows: list[dict], dropped: list[str], patched: list[str], action_counts: Counter) -> str:
    counts = defaultdict(lambda: {"train": 0, "val": 0})
    for row in rows:
        counts[row["bucket"]][row["split"]] += 1

    lines = [
        "# reduced_round03_repair_v1 Summary",
        "",
        "- source dataset: `reduced_round03_curated_v1`",
        "- purpose: reduce bucket tug-of-war before the next reduced round_03 retry",
        "",
        "| bucket | train | val |",
        "| --- | ---: | ---: |",
    ]
    for bucket in sorted(counts):
        lines.append(f"| `{bucket}` | {counts[bucket]['train']} | {counts[bucket]['val']} |")

    lines.extend(
        [
            "",
            f"- total_records: `{len(rows)}`",
            f"- dropped_records: `{len(dropped)}`",
            f"- patched_records: `{len(patched)}`",
            "",
            "## Patch Actions",
            "",
        ]
    )
    for action, count in sorted(action_counts.items()):
        lines.append(f"- `{action}`: `{count}`")

    lines.extend(["", "## Dropped IDs", ""])
    for record_id in dropped:
        lines.append(f"- `{record_id}`")

    lines.extend(["", "## Patched IDs", ""])
    for record_id in patched:
        lines.append(f"- `{record_id}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair reduced round_03 dataset with focused bucket patches.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input_dir / "records_train.jsonl") + read_jsonl(args.input_dir / "records_val.jsonl")
    repaired_rows: list[dict] = []
    dropped: list[str] = []
    patched: list[str] = []
    action_counts: Counter = Counter()

    for row in rows:
        repaired, actions = repair_record(row)
        if repaired is None:
            dropped.append(row["id"])
            action_counts.update(actions)
            continue
        if actions:
            patched.append(repaired["id"])
            action_counts.update(actions)
        repaired_rows.append(repaired)

    dedup_global = dedupe_user_messages(repaired_rows)
    if dedup_global:
        action_counts["dedup_global_user_message"] += dedup_global

    duplicate_messages = collect_duplicate_user_messages(repaired_rows)
    if duplicate_messages:
        raise RuntimeError(
            "duplicate user_message remained after global dedupe: "
            + json.dumps(duplicate_messages, ensure_ascii=False, indent=2)
        )

    train_rows = [row for row in repaired_rows if row["split"] == "train"]
    val_rows = [row for row in repaired_rows if row["split"] == "val"]

    write_jsonl(args.output_dir / "records_train.jsonl", train_rows)
    write_jsonl(args.output_dir / "records_val.jsonl", val_rows)

    manifest = {
        "dataset_id": args.output_dir.name,
        "source_dataset": args.input_dir.name,
        "train_total": len(train_rows),
        "val_total": len(val_rows),
        "bucket_counts": {
            bucket: {
                "train": sum(1 for row in train_rows if row["bucket"] == bucket),
                "val": sum(1 for row in val_rows if row["bucket"] == bucket),
            }
            for bucket in sorted({row["bucket"] for row in repaired_rows})
        },
        "dropped_ids": dropped,
        "patched_ids": patched,
        "action_counts": dict(action_counts),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(
        build_summary(repaired_rows, dropped, patched, action_counts),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "train_total": len(train_rows),
                "val_total": len(val_rows),
                "dropped": len(dropped),
                "patched": len(patched),
                "action_counts": dict(action_counts),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
