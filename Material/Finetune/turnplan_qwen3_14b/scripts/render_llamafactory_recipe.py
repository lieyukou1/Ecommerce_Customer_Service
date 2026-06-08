from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render AutoDL-ready LLaMA-Factory train / merge / serve recipes.")
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--train-dataset-name", default="turnplan_phase1_train")
    parser.add_argument("--val-dataset-name", default="turnplan_phase1_val")
    parser.add_argument("--wandb-project", default="ecs-turnplan")
    parser.add_argument("--report-to", default="wandb")
    parser.add_argument("--template", default="qwen3_nothink")
    parser.add_argument("--cutoff-len", type=int, default=3072)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=16)
    parser.add_argument("--num-train-epochs", type=float, default=3.0)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--warmup-ratio", type=float, default=0.08)
    parser.add_argument("--lora-r", type=int, default=64)
    parser.add_argument("--lora-alpha", type=int, default=128)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--save-steps", type=int, default=50)
    parser.add_argument("--eval-steps", type=int, default=50)
    parser.add_argument("--logging-steps", type=int, default=5)
    return parser.parse_args()


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    args = parse_args()
    run_root = args.work_root / "artifacts" / "manifests" / args.run_name
    adapter_dir = args.work_root / "artifacts" / "adapters" / args.run_name
    merged_dir = args.work_root / "artifacts" / "merged" / args.run_name
    reports_dir = args.work_root / "artifacts" / "reports" / args.run_name

    train_config = {
        "model_name_or_path": str(args.model_dir),
        "stage": "sft",
        "do_train": True,
        "do_eval": True,
        "finetuning_type": "lora",
        "lora_target": "all",
        "lora_rank": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "quantization_bit": 4,
        "double_quantization": True,
        "quantization_type": "nf4",
        "template": args.template,
        "flash_attn": "auto",
        "dataset_dir": str(args.dataset_dir),
        "dataset": args.train_dataset_name,
        "eval_dataset": args.val_dataset_name,
        "cutoff_len": args.cutoff_len,
        "overwrite_cache": True,
        "preprocessing_num_workers": 8,
        "output_dir": str(adapter_dir),
        "overwrite_output_dir": True,
        "logging_steps": args.logging_steps,
        "save_steps": args.save_steps,
        "eval_steps": args.eval_steps,
        "plot_loss": True,
        "save_total_limit": 3,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": 1,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "num_train_epochs": args.num_train_epochs,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": args.warmup_ratio,
        "optim": "paged_adamw_32bit",
        "bf16": True,
        "ddp_timeout": 180000000,
        "report_to": args.report_to,
        "run_name": args.run_name,
    }

    merge_config = {
        "model_name_or_path": str(args.model_dir),
        "adapter_name_or_path": str(adapter_dir),
        "template": args.template,
        "finetuning_type": "lora",
        "export_dir": str(merged_dir),
        "export_device": "cpu",
        "export_size": 4,
        "export_legacy_format": False,
    }

    serve_script = f"""#!/usr/bin/env bash
set -eo pipefail
source /root/.config/ecs-llm/env.sh
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/autodl-tmp/ecs-llm/envs/ecs-vllm

python -m vllm.entrypoints.openai.api_server \\
  --host 0.0.0.0 \\
  --port 8000 \\
  --model {merged_dir} \\
  --served-model-name {args.run_name} \\
  --dtype bfloat16 \\
  --gpu-memory-utilization 0.90 \\
  --reasoning-parser qwen3 \\
  --default-chat-template-kwargs '{{"enable_thinking": false}}' \\
  --generation-config vllm \\
  --max-model-len 8192
"""

    run_root.mkdir(parents=True, exist_ok=True)
    write_yaml(run_root / "train_qwen3_14b_qlora.yaml", train_config)
    write_yaml(run_root / "merge_qwen3_14b.yaml", merge_config)
    (run_root / "serve_candidate_vllm.sh").write_text(serve_script, encoding="utf-8")

    manifest = {
        "run_name": args.run_name,
        "work_root": str(args.work_root),
        "model_dir": str(args.model_dir),
        "dataset_dir": str(args.dataset_dir),
        "adapter_dir": str(adapter_dir),
        "merged_dir": str(merged_dir),
        "reports_dir": str(reports_dir),
        "train_config": str(run_root / "train_qwen3_14b_qlora.yaml"),
        "merge_config": str(run_root / "merge_qwen3_14b.yaml"),
        "serve_script": str(run_root / "serve_candidate_vllm.sh"),
        "profile": {
            "cutoff_len": args.cutoff_len,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "num_train_epochs": args.num_train_epochs,
            "learning_rate": args.learning_rate,
            "warmup_ratio": args.warmup_ratio,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "train_dataset_name": args.train_dataset_name,
            "val_dataset_name": args.val_dataset_name,
        },
    }
    (run_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
