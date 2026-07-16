from __future__ import annotations

import json
import pathlib
import re
import shlex
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


def parse_git_operation(command: str) -> tuple[str, list[str]] | None:
    try:
        tokens = [token.strip('"\'') for token in shlex.split(command, posix=False)]
    except ValueError:
        return None
    git_index: int | None = None
    for index, token in enumerate(tokens):
        executable = token.replace("/", "\\").rsplit("\\", 1)[-1].lower()
        if executable in {"git", "git.exe"}:
            git_index = index
            break
    if git_index is None:
        return None
    args = tokens[git_index + 1 :]
    options_with_value = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
    flag_options = {"--no-pager", "--paginate"}
    index = 0
    while index < len(args):
        token = args[index]
        if token == "--":
            index += 1
            break
        if token in options_with_value:
            index += 2
            continue
        if token in flag_options:
            index += 1
            continue
        if any(token.startswith(option + "=") for option in options_with_value if option.startswith("--")):
            index += 1
            continue
        if token.startswith("-C") and token != "-C":
            index += 1
            continue
        if token.startswith("-c") and token != "-c":
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    if index >= len(args):
        return None
    return args[index].lower(), args[index + 1 :]


def detect_forbidden_git_operation(command: str) -> str | None:
    parsed = parse_git_operation(command)
    if parsed is None:
        return None
    subcommand, args = parsed
    if subcommand in {"push", "reset", "clean", "rebase"}:
        return f"本项目禁止 git {subcommand}。"
    if subcommand == "commit" and any(arg == "--amend" or arg.startswith("--amend=") for arg in args):
        return "本项目禁止 git commit --amend。"
    return None


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
        forbidden = detect_forbidden_git_operation(command)
        if forbidden:
            deny(forbidden)
            return 0
        if re.search(r"(?i)(?:^|\s)(?:cat|type|Get-Content)\b[^\n]*[\\/]?\.env\b", command):
            deny("禁止读取 .env。")
            return 0
        parsed_git = parse_git_operation(command)
        if parsed_git is not None and parsed_git[0] == "commit":
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
