from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "verify_codex_migration.py"
BUILD_PATH = ROOT / "tools" / "build_codex_adaptation.py"
HOOK_PATH = ROOT / ".codex" / "hooks" / "game_studio_hook.py"
SNAPSHOT = ROOT / "upstream" / "claude-code-game-studios-v1.0.0"
SOURCE_MANIFEST = ROOT / "upstream" / "SOURCE-MANIFEST.json"


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_verifier():
    return load_module(MODULE_PATH, "verify_codex_migration")


def load_builder():
    return load_module(BUILD_PATH, "build_codex_adaptation")


def load_hook():
    return load_module(HOOK_PATH, "game_studio_hook")


class VerifyCodexMigrationTests(unittest.TestCase):
    def test_frontmatter_parser_requires_name_and_description(self) -> None:
        verifier = load_verifier()
        metadata, body = verifier.parse_frontmatter(
            "---\nname: sample\ndescription: narrow trigger\n---\n\n# Workflow\n"
        )
        self.assertEqual("sample", metadata["name"])
        self.assertEqual("narrow trigger", metadata["description"])
        self.assertIn("# Workflow", body)

    def test_repository_passes_all_static_checks(self) -> None:
        verifier = load_verifier()
        errors, summary = verifier.verify_repository(ROOT)
        self.assertEqual([], errors)
        self.assertEqual(49, summary["converted_agents"])
        self.assertEqual(73, summary["converted_skills"])

    def snapshot_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], pathlib.Path, pathlib.Path]:
        temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(temporary.name)
        snapshot = root / "snapshot"
        manifest = root / "SOURCE-MANIFEST.json"
        shutil.copytree(SNAPSHOT, snapshot)
        shutil.copy2(SOURCE_MANIFEST, manifest)
        return temporary, snapshot, manifest

    def test_source_manifest_matches_snapshot(self) -> None:
        verifier = load_verifier()
        self.assertEqual([], verifier.verify_snapshot(SNAPSHOT, SOURCE_MANIFEST))

    def test_modified_snapshot_file_fails(self) -> None:
        verifier = load_verifier()
        temporary, snapshot, manifest = self.snapshot_fixture()
        self.addCleanup(temporary.cleanup)
        target = snapshot / "README.md"
        target.write_bytes(target.read_bytes() + b"\nmodified\n")
        errors = verifier.verify_snapshot(snapshot, manifest)
        self.assertTrue(any("hash mismatch" in error for error in errors), errors)

    def test_missing_snapshot_file_fails(self) -> None:
        verifier = load_verifier()
        temporary, snapshot, manifest = self.snapshot_fixture()
        self.addCleanup(temporary.cleanup)
        (snapshot / "README.md").unlink()
        errors = verifier.verify_snapshot(snapshot, manifest)
        self.assertTrue(any("file set" in error for error in errors), errors)

    def test_extra_snapshot_file_fails(self) -> None:
        verifier = load_verifier()
        temporary, snapshot, manifest = self.snapshot_fixture()
        self.addCleanup(temporary.cleanup)
        (snapshot / "unexpected.txt").write_text("unexpected", encoding="utf-8")
        errors = verifier.verify_snapshot(snapshot, manifest)
        self.assertTrue(any("file set" in error for error in errors), errors)

    def test_manifest_commit_or_tree_mismatch_fails(self) -> None:
        verifier = load_verifier()
        for field in ("commit", "tree"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
                manifest[field] = "0" * 40
                path = pathlib.Path(temporary) / "SOURCE-MANIFEST.json"
                path.write_text(json.dumps(manifest), encoding="utf-8")
                errors = verifier.verify_snapshot(SNAPSHOT, path)
                self.assertTrue(any(field in error for error in errors), errors)

    def test_forbidden_git_variants_are_detected(self) -> None:
        hook = load_hook()
        commands = (
            "git push origin main",
            "git.exe push origin main",
            r"git -C E:\repo push origin main",
            "git -c core.askPass= push origin main",
            r'"C:\Program Files\Git\cmd\git.exe" push origin main',
            r"git --git-dir E:\repo\.git push origin main",
            "git reset --hard HEAD",
            r"git -C E:\repo reset --hard HEAD",
            "git.exe clean -fd",
            "git -c advice.detachedHead=false rebase main",
            r"git -C E:\repo commit --amend",
            r"git --git-dir=E:\repo\.git push origin main",
            r"git --work-tree E:\repo push origin main",
            r"git --namespace team reset --hard HEAD",
            r"git --no-pager clean -fd",
            r"git --paginate rebase main",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNotNone(hook.detect_forbidden_git_operation(command))

    def test_forbidden_git_operation_after_safe_command_is_detected(self) -> None:
        hook = load_hook()
        commands = (
            "git status; git push origin main",
            "git status && git reset --hard HEAD",
            "git log | git.exe clean -fd",
            "git status;git -c advice.detachedHead=false rebase main",
            'powershell -Command "git status; git push origin main"',
            'cmd /c "git status && git reset --hard HEAD"',
            "git status $(git push origin main)",
            "(git push origin main)",
            'Write-Output "$(git push origin main)"',
            """bash -c 'echo "$(git push origin main)"'""",
            "echo `git push origin main`",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNotNone(hook.detect_forbidden_git_operation(command))

    def test_safe_git_variants_are_allowed(self) -> None:
        hook = load_hook()
        commands = (
            "git status",
            r"git -C E:\repo status",
            "git diff",
            "git log",
            'git commit -m "normal commit"',
            'git commit -m "document git push; keep local"',
            'git commit -m "document powershell -Command (git push)"',
            "Write-Output '$(git push origin main)'",
            "git commit -m 'document $(git push)'",
            "git --no-pager status",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(hook.detect_forbidden_git_operation(command))

    def test_generated_hook_matches_build_source(self) -> None:
        builder = load_builder()
        generated = builder.HOOK_SCRIPT.replace("\r\n", "\n").rstrip()
        checked_in = HOOK_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip()
        self.assertEqual(generated, checked_in)

    def test_generated_hook_configuration_matches_build_source(self) -> None:
        builder = load_builder()
        checked_in = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(builder.hook_configuration(), checked_in)

    @unittest.skipUnless(os.name == "nt", "Windows Hook command")
    def test_windows_hook_command_runs_without_python_on_path(self) -> None:
        builder = load_builder()
        command = str(builder.hook_handler("session-start", "test")["commandWindows"])
        git = shutil.which("git")
        self.assertIsNotNone(git)
        windows = pathlib.Path(os.environ["SystemRoot"])
        env = os.environ.copy()
        env["CODEX_PYTHON"] = sys.executable
        env["PATH"] = os.pathsep.join(
            (
                str(pathlib.Path(str(git)).parent),
                str(windows / "System32" / "WindowsPowerShell" / "v1.0"),
                str(windows / "System32"),
                str(windows),
            )
        )
        result = subprocess.run(
            command,
            cwd=ROOT,
            input=json.dumps({"cwd": str(ROOT), "hook_event_name": "SessionStart"}),
            text=True,
            encoding="utf-8",
            capture_output=True,
            shell=True,
            env=env,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual("SessionStart", output["hookSpecificOutput"]["hookEventName"])

    def test_router_is_only_implicit_skill_and_index_is_complete(self) -> None:
        verifier = load_verifier()
        errors, summary = verifier.verify_skill_configuration(ROOT)
        self.assertEqual([], errors)
        self.assertEqual(73, summary["downstream_skills"])
        self.assertEqual(73, summary["indexed_skills"])
        self.assertEqual(["game-studio-router"], summary["implicit_skills"])

    def test_missing_skill_description_fails(self) -> None:
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as temporary:
            skill = pathlib.Path(temporary)
            (skill / "agents").mkdir()
            (skill / "SKILL.md").write_text("---\nname: sample\n---\n\n# Sample\n", encoding="utf-8")
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n  display_name: sample\n  short_description: sample\n  default_prompt: sample\npolicy:\n  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            errors, _ = verifier.validate_skill_directory(skill)
            self.assertTrue(any("description" in error for error in errors), errors)

    def test_invalid_openai_yaml_structure_fails(self) -> None:
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as temporary:
            skill = pathlib.Path(temporary)
            (skill / "agents").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: sample\n---\n\n# Sample\n", encoding="utf-8"
            )
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n  display_name: sample\n  short_description: sample\npolicy:\n  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            errors, _ = verifier.validate_skill_directory(skill)
            self.assertTrue(any("default_prompt" in error for error in errors), errors)

    def run_hook(self, mode: str, payload: dict[str, object]) -> dict[str, object]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "safe.directory",
                "GIT_CONFIG_VALUE_0": ROOT.as_posix(),
            }
        )
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH), mode],
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
            env=env,
        )
        return json.loads(result.stdout)

    def test_pre_tool_hook_blocks_push(self) -> None:
        output = self.run_hook(
            "pre-tool",
            {"cwd": str(ROOT), "hook_event_name": "PreToolUse", "tool_input": {"command": "git push origin main"}},
        )
        decision = output["hookSpecificOutput"]
        self.assertEqual("deny", decision["permissionDecision"])

    def test_post_edit_hook_accepts_valid_generated_skills(self) -> None:
        output = self.run_hook(
            "post-edit",
            {"cwd": str(ROOT), "hook_event_name": "PostToolUse", "tool_name": "apply_patch", "tool_input": {"command": "patch"}},
        )
        self.assertEqual({}, output)


if __name__ == "__main__":
    unittest.main()
