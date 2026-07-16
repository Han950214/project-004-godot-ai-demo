from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys


for stream in (sys.stdin, sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def emit(value: dict[str, object]) -> None:
    print(json.dumps(value, ensure_ascii=False))


def read_input() -> dict[str, object]:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def repo_root(cwd: str) -> pathlib.Path:
    result = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return pathlib.Path(result.stdout.strip() or cwd).resolve()


def deny(reason: str) -> None:
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}})


def changed_files(root: pathlib.Path) -> list[pathlib.Path]:
    commands = (["git", "diff", "--name-only"], ["git", "ls-files", "--others", "--exclude-standard"])
    names: set[str] = set()
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, encoding="utf-8")
        names.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return [root / name for name in sorted(names)]


def validate_json(paths: list[pathlib.Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path.suffix.lower() != ".json" or not path.is_file():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
    return errors


def validate_skills(paths: list[pathlib.Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path.name != "SKILL.md" or ".agents" not in path.parts or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        try:
            end = lines.index("---", 1) if lines and lines[0] == "---" else -1
        except ValueError:
            end = -1
        frontmatter = "\n".join(lines[1:end]) if end > 1 else ""
        if not re.search(r"(?m)^name:\s*\S+\s*$", frontmatter) or not re.search(r"(?m)^description:\s*.+$", frontmatter):
            errors.append(f"invalid Skill frontmatter: {path}")
    return errors


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    data = read_input()
    cwd = str(data.get("cwd") or pathlib.Path.cwd())
    root = repo_root(cwd)

    if mode == "session-start":
        missing = [name for name in ("design/gdd", "production/sprints") if not (root / name).exists()]
        suffix = f" 尚未建立：{', '.join(missing)}。" if missing else ""
        emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "先读取根 AGENTS.md 与目标目录最近的嵌套 AGENTS.md；不得自动 push 或推进下一制作阶段。" + suffix}})
        return 0

    if mode == "pre-tool":
        tool_input = data.get("tool_input")
        command = str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
        dangerous = [
            (r"(?i)(?:^|\s)git\s+push\b", "本项目禁止 git push。"),
            (r"(?i)(?:^|\s)git\s+(?:reset|clean|rebase)\b", "本项目禁止 reset、clean 或 rebase。"),
            (r"(?i)(?:^|\s)git\s+commit\s+--amend\b", "本项目禁止 git commit --amend。"),
            (r"(?i)(?:^|\s)(?:cat|type|Get-Content)\b[^\n]*[\\/]?\.env\b", "禁止读取 .env。"),
        ]
        for pattern, reason in dangerous:
            if re.search(pattern, command):
                deny(reason)
                return 0
        if re.search(r"(?i)(?:^|\s)git\s+commit\b", command):
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=root, check=False, capture_output=True, text=True, encoding="utf-8")
            errors = validate_json([root / line for line in result.stdout.splitlines() if line.strip()])
            if errors:
                deny("提交前 JSON 校验失败：" + "; ".join(errors[:5]))
                return 0
        emit({})
        return 0

    if mode == "post-edit":
        files = changed_files(root)
        errors = validate_json(files) + validate_skills(files)
        emit({"systemMessage": "写入后静态校验失败：" + "; ".join(errors[:8]), "continue": False, "stopReason": "修复静态校验问题"} if errors else {})
        return 0

    if mode == "pre-compact":
        names = [path.relative_to(root).as_posix() for path in changed_files(root)[:30]]
        emit({"systemMessage": "压缩前工作区改动：" + (", ".join(names) if names else "无")})
        return 0

    if mode == "post-compact":
        emit({"systemMessage": "上下文已压缩；继续前复核 AGENTS.md、当前计划和 git status。"})
        return 0

    if mode == "subagent-start":
        emit({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "只完成受命领域；不得递归创建子代理、跨仓库工作或 push。"}})
        return 0

    if mode in {"subagent-stop", "stop"}:
        emit({})
        return 0

    emit({"systemMessage": f"未知 Game Studio Hook 模式：{mode}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
