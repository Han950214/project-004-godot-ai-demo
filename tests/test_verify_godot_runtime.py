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
        self.commands: list[list[str]] = []
        self.version_output = "4.7.1.stable.official.a13da4feb\n"
        self.import_output = "Godot Engine v4.7.1.stable.official\n"
        self.runtime_output = (
            "Godot Engine v4.7.1.stable.official\n"
            "CODEX_GODOT_RUNTIME_START\n"
            "CODEX_GODOT_RUNTIME_READY\n"
        )
        self.import_returncode = 0
        self.runtime_returncode = 0
        self.tracked_files = ""

    def __call__(self, command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        if command[0] == "git":
            return subprocess.CompletedProcess(command, 0, self.tracked_files, "")
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, self.version_output, "")
        if "--import" in command:
            return subprocess.CompletedProcess(
                command, self.import_returncode, self.import_output, ""
            )
        return subprocess.CompletedProcess(
            command, self.runtime_returncode, self.runtime_output, ""
        )


class VerifyGodotRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.gui_executable = self.root / "Godot_v4.7.1-stable_win64.exe"
        self.console_executable = self.root / "Godot_v4.7.1-stable_win64_console.exe"
        self.executable = self.console_executable
        self.gui_executable.write_bytes(b"test placeholder; not a Godot binary")
        self.console_executable.write_bytes(b"test placeholder; not a Godot binary")
        (self.root / "_sc_").touch()
        (self.root / ".codex").mkdir()
        (self.root / ".codex" / "config.toml").write_text(
            """sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  'E:\\Workspace\\tools\\Godot\\4.7.1\\editor_data',
]

[mcp_servers.godot]
command = 'E:\\Program Files\\nodejs\\npx.cmd'
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

    def test_runtime_exact_editor_data_writable_root_passes_validation(self) -> None:
        verifier = load_verifier()

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertEqual([], errors)

    def test_runtime_missing_editor_data_writable_root_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        text = config.read_text(encoding="utf-8")
        text = text[text.index("[mcp_servers.godot]") :]
        config.write_text(text, encoding="utf-8")

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("sandbox_mode must be workspace-write" in error for error in errors), errors)
        self.assertTrue(any("writable_roots must exactly match" in error for error in errors), errors)

    def test_runtime_entire_godot_directory_writable_root_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                r"E:\Workspace\tools\Godot\4.7.1\editor_data",
                r"E:\Workspace\tools\Godot\4.7.1",
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("writable_roots must exactly match" in error for error in errors), errors)

    def test_runtime_second_writable_root_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "  'E:\\Workspace\\tools\\Godot\\4.7.1\\editor_data',\n",
                "  'E:\\Workspace\\tools\\Godot\\4.7.1\\editor_data',\n"
                "  'E:\\Workspace\\projects\\game',\n",
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("writable_roots must exactly match" in error for error in errors), errors)

    def test_runtime_danger_full_access_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'sandbox_mode = "workspace-write"',
                'sandbox_mode = "danger-full-access"',
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("sandbox_mode must be workspace-write" in error for error in errors), errors)

    def test_runtime_network_access_true_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "[sandbox_workspace_write]\n",
                "[sandbox_workspace_write]\nnetwork_access = true\n",
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("network_access must not be enabled" in error for error in errors), errors)

    def test_runtime_correct_version_and_project_pass_validation(self) -> None:
        verifier = load_verifier()

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertEqual([], errors)
        self.assertEqual("4.7.1.stable.official.a13da4feb", summary["godot_version"])
        self.assertTrue(summary["runtime_start_marker_found"])
        self.assertTrue(summary["runtime_ready_marker_found"])

    def test_runtime_defaults_to_console_executable(self) -> None:
        verifier = load_verifier()

        self.assertEqual(
            verifier.EXPECTED_GODOT_CONSOLE_PATH,
            verifier.verify_runtime.__kwdefaults__["godot_executable"],
        )

    def test_runtime_commands_use_console_import_contract(self) -> None:
        verifier = load_verifier()

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.console_executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertEqual([], errors)
        godot_commands = [command for command in self.runner.commands if command[0] != "git"]
        self.assertTrue(all(command[0] == str(self.console_executable) for command in godot_commands))
        import_command = next(command for command in godot_commands if "--import" in command)
        self.assertIn("--headless", import_command)
        self.assertIn("--verbose", import_command)
        self.assertNotIn("--editor", import_command)
        self.assertNotIn("2", import_command)
        runtime_command = next(command for command in godot_commands if "--quit-after" in command)
        self.assertIn("--verbose", runtime_command)

    def test_runtime_mcp_godot_path_must_remain_gui_executable(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "Godot_v4.7.1-stable_win64.exe",
                "Godot_v4.7.1-stable_win64_console.exe",
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.console_executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("GODOT_PATH" in error for error in errors), errors)

    def test_runtime_missing_gui_executable_fails_validation(self) -> None:
        verifier = load_verifier()
        self.gui_executable.unlink()

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.console_executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("GUI executable is missing" in error for error in errors), errors)

    def test_runtime_access_violation_reports_hex_and_stops_after_import(self) -> None:
        verifier = load_verifier()
        for returncode in (3221225477, -1073741819):
            with self.subTest(returncode=returncode):
                self.runner = FakeRunner()
                self.runner.import_returncode = returncode

                errors, summary = verifier.verify_runtime(
                    self.root,
                    godot_executable=self.console_executable,
                    godot_gui_executable=self.gui_executable,
                    runner=self.runner,
                )

                self.assertTrue(any("0xC0000005" in error for error in errors), errors)
                self.assertFalse(summary["headless_run"])
                self.assertFalse(any("--quit-after" in command for command in self.runner.commands))

    def test_runtime_import_failure_does_not_run_project(self) -> None:
        verifier = load_verifier()
        self.runner.import_returncode = 1

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.console_executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("headless import failed" in error for error in errors), errors)
        self.assertFalse(summary["headless_run"])
        self.assertFalse(any("--quit-after" in command for command in self.runner.commands))

    def test_runtime_import_error_output_does_not_run_project(self) -> None:
        verifier = load_verifier()
        self.runner.import_output = "ERROR: Cannot open resource\n"

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.console_executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("import output contains errors" in error for error in errors), errors)
        self.assertTrue(summary["godot_errors_found"])
        self.assertFalse(summary["headless_run"])
        self.assertFalse(any("--quit-after" in command for command in self.runner.commands))

    def test_runtime_npx_command_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                r"E:\Program Files\nodejs\npx.cmd", "npx"
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("must not use the PowerShell-resolved" in error for error in errors), errors)

    def test_runtime_npx_ps1_command_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("npx.cmd", "npx.ps1"),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("must not use npx.ps1" in error for error in errors), errors)

    def test_runtime_execution_policy_bypass_fails_validation(self) -> None:
        verifier = load_verifier()
        config = self.root / ".codex" / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                '"-y",', '"-ExecutionPolicy=Bypass", "-y",'
            ),
            encoding="utf-8",
        )

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("must not change PowerShell execution policy" in error for error in errors), errors)

    def test_runtime_missing_executable_fails_validation(self) -> None:
        verifier = load_verifier()
        self.executable.unlink()

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("executable is missing" in error for error in errors), errors)

    def test_runtime_missing_self_contained_marker_fails_validation(self) -> None:
        verifier = load_verifier()
        (self.root / "_sc_").unlink()

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("self-contained marker" in error for error in errors), errors)

    def test_runtime_wrong_godot_version_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.version_output = "4.7.stable.official.deadbeef\n"

        errors, _ = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
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
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
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
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
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
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
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
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("enabled_tools must exactly match" in error for error in errors), errors)

    def test_runtime_missing_demo_main_scene_fails_validation(self) -> None:
        verifier = load_verifier()
        (self.root / "demo" / "scenes" / "main.tscn").unlink()

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("main scene is missing" in error for error in errors), errors)
        self.assertFalse(summary["demo_project_valid"])

    def test_runtime_missing_success_log_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.runtime_output = "Godot Engine v4.7.1.stable.official\n"

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("runtime output lacks marker" in error for error in errors), errors)
        self.assertFalse(summary["runtime_start_marker_found"])
        self.assertFalse(summary["runtime_ready_marker_found"])

    def test_runtime_git_tracked_godot_binary_fails_validation(self) -> None:
        verifier = load_verifier()
        self.runner.tracked_files = "vendor/Godot_v4.7.1-stable_win64.exe\n"

        errors, summary = verifier.verify_runtime(
            self.root,
            godot_executable=self.executable,
            godot_gui_executable=self.gui_executable,
            runner=self.runner,
        )

        self.assertTrue(any("binary is tracked" in error for error in errors), errors)
        self.assertTrue(summary["godot_binary_tracked"])


if __name__ == "__main__":
    unittest.main()
