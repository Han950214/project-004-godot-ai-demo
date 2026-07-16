from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "verify_codex_migration.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_codex_migration", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
            [sys.executable, str(ROOT / ".codex" / "hooks" / "game_studio_hook.py"), mode],
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

    def test_post_edit_hook_accepts_generated_skills(self) -> None:
        output = self.run_hook(
            "post-edit",
            {"cwd": str(ROOT), "hook_event_name": "PostToolUse", "tool_name": "apply_patch", "tool_input": {"command": "patch"}},
        )
        self.assertEqual({}, output)


if __name__ == "__main__":
    unittest.main()
