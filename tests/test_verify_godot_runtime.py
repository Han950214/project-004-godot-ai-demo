from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "verify_godot_runtime.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_godot_runtime", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeRunner:
    def __init__(self) -> None:
        self.version_output = "4.7.1.stable.official.a13da4feb\n"
        self.import_output = "Godot Engine v4.7.1.stable.official\n"
        self.runtime_output = (
            "Godot Engine v4.7.1.stable.official\n"
            "CODEX_GODOT_RUNTIME_START\n"
            "CODEX_GODOT_RUNTIME_READY\n"
        )
        self.tracked_files = ""

    def __call__(self, command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        if command[0] == "git":
            return subprocess.CompletedProcess(command, 0, self.tracked_files, "")
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, self.version_output, "")
        if "--editor" in command:
            return subprocess.CompletedProcess(command, 0, self.import_output, "")
        return subprocess.CompletedProcess(command, 0, self.runtime_output, "")


class VerifyGodotRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.executable = self.root / "Godot_v4.7.1-stable_win64.exe"
        self.executable.write_bytes(b"test placeholder; not a Godot binary")
        (self.root / "_sc_").touch()
        (self.root / ".codex").mkdir()
        (self.root / ".codex" / "config.toml").write_text(
            """[mcp_servers.godot]
command = "npx"
args = ["-y", "@coding-solo/godot-mcp@0.1.1"]
cwd = 'E:\\Workspace\\projects\\game\\project_004_godot_ai_demo'
enabled = true
required = false
default_tools_approval_mode = "writes"
enabled_tools = [
  "get_godot_version",
  "list_projects",
  "get_project_info",
  "launch_editor",
  "run_project",
  "get_debug_output",
  "stop_project",
]

[mcp_servers.godot.env]
GODOT_PATH = 'E:\\Workspace\\tools\\Godot\\4.7.1\\Godot_v4.7.1-stable_win64.exe'
DEBUG = "true"
""",
            encoding="utf-8",
        )
        (self.root / "demo" / "scenes").mkdir(parents=True)
        (self.root / "demo" / "scripts").mkdir()
        (self.root / "demo" / "project.godot").write_text(
            '[application]\nrun/main_scene="res://scenes/main.tscn"\n', encoding="utf-8"
        )
        (self.root / "demo" / "scenes" / "main.tscn").write_text(
            '[gd_scene load_steps=2 format=3]\n'
            '[ext_resource type="Script" path="res://scripts/main.gd" id="1"]\n'
            '[node name="Main" type="Control"]\nscript = ExtResource("1")\n',
            encoding="utf-8",
        )
        (self.root / "demo" / "scripts" / "main.gd").write_text(
            'extends Control\nfunc _ready():\n'
            '    print("CODEX_GODOT_RUNTIME_START")\n'
            '    print("CODEX_GODOT_RUNTIME_READY")\n',
            encoding="utf-8",
        )
        self.runner = FakeRunner()

    def test_runtime_correct_version_and_project_pass_validation(self) -> None:
        verifier = load_verifier()

        errors, summary = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertEqual([], errors)
        self.assertEqual("4.7.1.stable.official.a13da4feb", summary["godot_version"])
        self.assertTrue(summary["runtime_start_marker_found"])
        self.assertTrue(summary["runtime_ready_marker_found"])

    def test_runtime_missing_executable_fails_validation(self) -> None:
        verifier = load_verifier()
        self.executable.unlink()

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("executable is missing" in error for error in errors), errors)

    def test_runtime_missing_self_contained_marker_fails_validation(self) -> None:
        verifier = load_verifier()
        (self.root / "_sc_").unlink()

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("self-contained marker" in error for error in errors), errors)

    def test_runtime_wrong_godot_version_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.version_output = "4.7.stable.official.deadbeef\n"

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("unexpected Godot version" in error for error in errors), errors)

    def test_runtime_disabled_mcp_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("enabled = true", "enabled = false"),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("must be enabled" in error for error in errors), errors)

    def test_runtime_unpinned_mcp_package_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "@coding-solo/godot-mcp@0.1.1", "@coding-solo/godot-mcp@latest"
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("package must be pinned" in error for error in errors), errors)

    def test_runtime_incomplete_mcp_tool_allowlist_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace('  "stop_project",\n', ""),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("enabled_tools must exactly match" in error for error in errors), errors)

    def test_runtime_extra_mcp_write_tool_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                '  "stop_project",\n', '  "stop_project",\n  "create_scene",\n'
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("enabled_tools must exactly match" in error for error in errors), errors)

    def test_runtime_missing_demo_main_scene_fails_validation(self) -> None:
        verifier = load_verifier()
        (self.root / "demo" / "scenes" / "main.tscn").unlink()

        errors, summary = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("main scene is missing" in error for error in errors), errors)
        self.assertFalse(summary["demo_project_valid"])

    def test_runtime_missing_success_log_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.runtime_output = "Godot Engine v4.7.1.stable.official\n"

        errors, summary = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("runtime output lacks marker" in error for error in errors), errors)
        self.assertFalse(summary["runtime_start_marker_found"])
        self.assertFalse(summary["runtime_ready_marker_found"])

    def test_runtime_git_tracked_godot_binary_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.tracked_files = "vendor/Godot_v4.7.1-stable_win64.exe\n"

        errors, summary = verifier.verify_runtime(
            self.root, godot_executable=self.executable, runner=self.runner
        )

        self.assertTrue(any("binary is tracked" in error for error in errors), errors)
        self.assertTrue(summary["godot_binary_tracked"])


if __name__ == "__main__":
    unittest.main()
