from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence


EXPECTED_VERSION = "4.7.1.stable"
EXPECTED_GODOT_PATH = pathlib.Path(
    r"E:\Workspace\tools\Godot\4.7.1\Godot_v4.7.1-stable_win64.exe"
)
EXPECTED_MCP_PACKAGE = "@coding-solo/godot-mcp@0.1.1"
EXPECTED_MCP_TOOLS = (
    "get_godot_version",
    "list_projects",
    "get_project_info",
    "launch_editor",
    "run_project",
    "get_debug_output",
    "stop_project",
)
RUNTIME_START_MARKER = "CODEX_GODOT_RUNTIME_START"
RUNTIME_READY_MARKER = "CODEX_GODOT_RUNTIME_READY"
GODOT_ERROR_PATTERNS = (
    re.compile(r"^ERROR:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\bSCRIPT ERROR\b", re.IGNORECASE),
    re.compile(r"\bParse Error\b", re.IGNORECASE),
    re.compile(r"\bParser Error\b", re.IGNORECASE),
    re.compile(r"Failed (?:loading|to load) resource", re.IGNORECASE),
    re.compile(r"Cannot open (?:file|resource)", re.IGNORECASE),
)

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def run_command(command: Sequence[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, **kwargs)  # type: ignore[arg-type]


def _read_toml(path: pathlib.Path, errors: list[str]) -> dict[str, object]:
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid TOML {path}: {exc}")
        return {}
    return value


def _command_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in (result.stdout, result.stderr) if part)


def _run(
    runner: CommandRunner,
    command: list[str],
    *,
    timeout: int,
    errors: list[str],
    label: str,
) -> tuple[subprocess.CompletedProcess[str] | None, str]:
    try:
        result = runner(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        errors.append(f"{label} timed out after {timeout} seconds")
        return None, ""
    except OSError as exc:
        errors.append(f"{label} could not start: {exc}")
        return None, ""
    output = _command_output(result)
    if result.returncode != 0:
        errors.append(f"{label} failed with exit code {result.returncode}")
    return result, output


def _verify_mcp(root: pathlib.Path, errors: list[str], summary: dict[str, object]) -> None:
    config = _read_toml(root / ".codex" / "config.toml", errors)
    servers = config.get("mcp_servers") if isinstance(config, dict) else None
    godot = servers.get("godot") if isinstance(servers, dict) else None
    if not isinstance(godot, dict):
        errors.append("missing project Godot MCP config")
        return

    args = godot.get("args")
    if args != ["-y", EXPECTED_MCP_PACKAGE]:
        errors.append("Godot MCP package must be pinned to @coding-solo/godot-mcp@0.1.1")
    if godot.get("enabled") is not True:
        errors.append("Godot MCP must be enabled")
    if godot.get("required") is not False:
        errors.append("Godot MCP must remain optional")
    if godot.get("default_tools_approval_mode") != "writes":
        errors.append("Godot MCP approval mode must be writes")
    tools = godot.get("enabled_tools")
    if tools != list(EXPECTED_MCP_TOOLS):
        errors.append(
            "Godot MCP enabled_tools must exactly match the seven runtime validation tools"
        )
    env = godot.get("env")
    expected_path = str(EXPECTED_GODOT_PATH)
    if not isinstance(env, dict) or env.get("GODOT_PATH") != expected_path:
        errors.append(f"Godot MCP GODOT_PATH must be {expected_path}")

    summary["godot_mcp_enabled"] = godot.get("enabled") is True
    summary["godot_mcp_tools"] = tools if isinstance(tools, list) else []


def _verify_demo(root: pathlib.Path, errors: list[str]) -> None:
    demo = root / "demo"
    project = demo / "project.godot"
    if not project.is_file():
        errors.append("missing demo/project.godot")
        return
    try:
        project_text = project.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read demo/project.godot: {exc}")
        return
    match = re.search(r'^run/main_scene\s*=\s*"res://([^"\r\n]+)"', project_text, re.MULTILINE)
    if not match:
        errors.append("demo/project.godot does not configure run/main_scene")
        return
    scene = demo / pathlib.PurePosixPath(match.group(1))
    if not scene.is_file():
        errors.append(f"demo main scene is missing: {scene.relative_to(root)}")
        return
    try:
        scene_text = scene.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read demo main scene: {exc}")
        return
    script_match = re.search(r'path="res://([^"\r\n]+\.gd)"', scene_text)
    if not script_match:
        errors.append("demo main scene does not reference a GDScript")
        return
    script = demo / pathlib.PurePosixPath(script_match.group(1))
    if not script.is_file():
        errors.append(f"demo GDScript is missing: {script.relative_to(root)}")
        return
    script_text = script.read_text(encoding="utf-8")
    for marker in (RUNTIME_START_MARKER, RUNTIME_READY_MARKER):
        if marker not in script_text:
            errors.append(f"demo GDScript lacks marker: {marker}")


def _verify_no_tracked_binary(
    root: pathlib.Path, runner: CommandRunner, errors: list[str], summary: dict[str, object]
) -> None:
    result, output = _run(
        runner,
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            "ls-files",
        ],
        timeout=15,
        errors=errors,
        label="git tracked-file check",
    )
    if result is None or result.returncode != 0:
        return
    tracked = [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]
    tracked_binary = [
        path
        for path in tracked
        if pathlib.PurePosixPath(path).name.lower().startswith("godot_v")
        and pathlib.PurePosixPath(path).suffix.lower() in {".exe", ".zip"}
    ]
    if tracked_binary:
        errors.append(f"Godot binary is tracked by Git: {tracked_binary}")
    summary["godot_binary_tracked"] = bool(tracked_binary)


def verify_runtime(
    root: pathlib.Path,
    *,
    godot_executable: pathlib.Path = EXPECTED_GODOT_PATH,
    runner: CommandRunner = run_command,
) -> tuple[list[str], dict[str, object]]:
    root = root.resolve()
    godot_executable = godot_executable.resolve()
    errors: list[str] = []
    summary: dict[str, object] = {
        "godot_version": "",
        "godot_mcp_enabled": False,
        "godot_mcp_tools": [],
        "godot_binary_tracked": False,
        "demo_project_valid": False,
        "headless_run": False,
        "runtime_start_marker_found": False,
        "runtime_ready_marker_found": False,
        "godot_errors_found": False,
    }

    if not godot_executable.is_file():
        errors.append(f"Godot executable is missing: {godot_executable}")
    if not any((godot_executable.parent / name).is_file() for name in ("_sc_", "._sc_")):
        errors.append(f"Godot self-contained marker is missing beside {godot_executable.name}")
    _verify_mcp(root, errors, summary)
    demo_error_count = len(errors)
    _verify_demo(root, errors)
    summary["demo_project_valid"] = len(errors) == demo_error_count
    _verify_no_tracked_binary(root, runner, errors, summary)
    if not godot_executable.is_file():
        return errors, summary

    version_result, version_output = _run(
        runner,
        [str(godot_executable), "--version"],
        timeout=15,
        errors=errors,
        label="Godot version check",
    )
    version = version_output.strip().splitlines()[0] if version_output.strip() else ""
    summary["godot_version"] = version
    if version_result is not None and EXPECTED_VERSION not in version.lower():
        errors.append(f"unexpected Godot version: {version or '<empty>'}")

    demo = root / "demo"
    import_result, import_output = _run(
        runner,
        [
            str(godot_executable),
            "--headless",
            "--editor",
            "--path",
            str(demo),
            "--quit-after",
            "2",
        ],
        timeout=60,
        errors=errors,
        label="Godot headless editor import",
    )
    runtime_result, runtime_output = _run(
        runner,
        [str(godot_executable), "--headless", "--path", str(demo), "--quit-after", "300"],
        timeout=30,
        errors=errors,
        label="Godot headless project run",
    )
    combined_output = "\n".join((import_output, runtime_output))
    godot_errors = [pattern.pattern for pattern in GODOT_ERROR_PATTERNS if pattern.search(combined_output)]
    if godot_errors:
        errors.append(f"Godot output contains runtime errors: {godot_errors}")
    start_found = RUNTIME_START_MARKER in runtime_output
    ready_found = RUNTIME_READY_MARKER in runtime_output
    if not start_found:
        errors.append(f"runtime output lacks marker: {RUNTIME_START_MARKER}")
    if not ready_found:
        errors.append(f"runtime output lacks marker: {RUNTIME_READY_MARKER}")
    summary["headless_run"] = (
        import_result is not None
        and import_result.returncode == 0
        and runtime_result is not None
        and runtime_result.returncode == 0
    )
    summary["runtime_start_marker_found"] = start_found
    summary["runtime_ready_marker_found"] = ready_found
    summary["godot_errors_found"] = bool(godot_errors)
    return errors, summary


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    errors, summary = verify_runtime(root)
    if errors:
        print("runtime_verification=failed")
        for error in errors:
            print(f"ERROR: {error}")
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 1
    print("runtime_verification=passed")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
