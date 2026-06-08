from pathlib import Path


def load_prompt(prompt_file_name: str) -> str:
    """
    功能：按提示词名称读取对应的 jinja2 模板内容。

    输入：
    - prompt_file_name: 提示词模板文件名，不带 `.jinja2` 后缀。

    输出：
    - str: 模板文件完整文本。

    调用情况：
    - `TurnPlanner._predict_from_inputs_prompt()`
    - `ClarifyResponder.respond()`
    - `ChitchatResponder.respond()`

    副作用：
    - 会读取本地提示词文件。
    """
    prompt_file_path = Path(__file__).resolve().parents[0] / "jinja2" / f"{prompt_file_name}.jinja2"
    return prompt_file_path.read_text(encoding="utf-8")
