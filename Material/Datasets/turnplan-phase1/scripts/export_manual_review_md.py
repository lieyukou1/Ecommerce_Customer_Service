from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dataset_contract import CANONICAL_DIR


DEFAULT_INPUT_DIR = CANONICAL_DIR.parent / "canonical_llm"
DEFAULT_OUTPUT_PATH = CANONICAL_DIR.parent / "docs" / "turnplan-phase1-manual-review.md"

BUCKET_ORDER = [
    "chitchat",
    "directive_exit_runtime",
    "ambiguous_all_null",
    "service_item_knowledge",
    "work_order_read_only_task",
    "work_order_business_urge",
    "work_order_business_complaint",
    "active_task_slot_fill",
    "object_context_followup",
    "task_interrupt_resume_cancel",
]

BUCKET_TITLES = {
    "chitchat": "闲聊",
    "directive_exit_runtime": "退出当前上下文",
    "ambiguous_all_null": "方向不明 / 继续澄清",
    "service_item_knowledge": "服务项目知识咨询",
    "work_order_read_only_task": "工单 / 规则 / 列表只读查询",
    "work_order_business_urge": "工单催办",
    "work_order_business_complaint": "工单投诉",
    "active_task_slot_fill": "当前任务补槽",
    "object_context_followup": "对象上下文追问",
    "task_interrupt_resume_cancel": "任务打断 / 恢复 / 取消 / 切换",
}

SPLIT_TITLES = {
    "train": "训练集",
    "val": "验证集",
}


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def maybe_fix_mojibake(text: str) -> str:
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    mojibake_markers = "ÃÂæåçéèêîïôöûüñ¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾"
    if not any(ch in text for ch in mojibake_markers):
        return text
    if repaired.count("\ufffd") > text.count("\ufffd"):
        return text
    if any("\u4e00" <= ch <= "\u9fff" for ch in repaired):
        return repaired
    return text


def normalize_text(value: str) -> str:
    return maybe_fix_mojibake(value).strip()


def build_markdown(input_dir: Path) -> str:
    records_by_split_bucket: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for split in ("train", "val"):
        for row in read_jsonl(input_dir / f"records_{split}.jsonl"):
            records_by_split_bucket[split][row["bucket"]].append(row)

    lines: list[str] = []
    lines.append("# TurnPlan Phase 1 人工抽检阅读版")
    lines.append("")
    lines.append(f"- 最后修改时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("- 文档定位：只保留本次训练样本里的对话文本，供人工抽检")
    lines.append("- 上级入口：[README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)")
    lines.append("- 下级入口：无")
    lines.append("")
    lines.append("## 使用说明")
    lines.append("")
    lines.append("- 已过滤：`id`、`json`、`runtime_state`、`output`、`meta`、模型信息。")
    lines.append("- 只保留两部分：历史对话、当前用户这句话。")
    lines.append("- 为了便于你人工反馈，保留了最小定位信息：数据集切分、场景桶、样本序号。")
    lines.append("")

    global_index = 1
    for split in ("train", "val"):
        split_total = sum(len(records_by_split_bucket[split][bucket]) for bucket in BUCKET_ORDER)
        lines.append(f"## {SPLIT_TITLES[split]}（{split_total} 条）")
        lines.append("")
        for bucket in BUCKET_ORDER:
            rows = records_by_split_bucket[split][bucket]
            if not rows:
                continue
            lines.append(f"### {BUCKET_TITLES.get(bucket, bucket)}（{len(rows)} 条）")
            lines.append("")
            for bucket_index, row in enumerate(rows, start=1):
                lines.append(f"#### 样本 {global_index:03d}（{bucket_index:02d}）")
                lines.append("")
                lines.append("历史对话：")
                lines.append("")
                history = row["input"]["history"]
                if history:
                    for turn in history:
                        role = "用户" if turn["role"] == "user" else "客服"
                        lines.append(f"- {role}：{normalize_text(turn['text'])}")
                else:
                    lines.append("- 无")
                lines.append("")
                lines.append(f"当前用户：{normalize_text(row['input']['user_message'])}")
                lines.append("")
                global_index += 1
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Markdown manual-review view for TurnPlan records.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    content = build_markdown(args.input_dir)
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(content, encoding="utf-8")
    print(json.dumps({"output_path": str(args.output_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
