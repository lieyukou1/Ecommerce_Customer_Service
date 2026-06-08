from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a reusable vLLM OpenAI-compatible launcher script.")
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--served-model-name", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--env-prefix", default="/root/autodl-tmp/ecs-llm/envs/ecs-vllm")
    parser.add_argument("--reasoning-parser", default="")
    parser.add_argument("--disable-thinking", action="store_true")
    parser.add_argument("--generation-config", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extra_lines: list[str] = []
    if args.reasoning_parser:
        extra_lines.append(f"  --reasoning-parser {args.reasoning_parser} \\\n")
    if args.disable_thinking:
        extra_lines.append("  --default-chat-template-kwargs '{\"enable_thinking\": false}' \\\n")
    if args.generation_config:
        extra_lines.append(f"  --generation-config {args.generation_config} \\\n")

    script = f"""#!/usr/bin/env bash
set -eo pipefail
source /root/.config/ecs-llm/env.sh
source /root/miniconda3/etc/profile.d/conda.sh
conda activate {args.env_prefix}

python -m vllm.entrypoints.openai.api_server \\
  --host {args.host} \\
  --port {args.port} \\
  --model {args.model_dir} \\
  --served-model-name {args.served_model_name} \\
  --dtype {args.dtype} \\
  --gpu-memory-utilization {args.gpu_memory_utilization:.2f} \\
{''.join(extra_lines)}\
  --max-model-len {args.max_model_len}
"""
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(script, encoding="utf-8")
    print(args.output_path)


if __name__ == "__main__":
    main()
