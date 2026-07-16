from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import tomllib


EXPECTED_COMMIT = "984023ddac0d5e27624f2baacde6105e45de375f"
EXPECTED_MCP_VERSION = "0.1.1"
REQUIRED_SNAPSHOT_PATHS = (
    ".claude",
    "CLAUDE.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "UPGRADING.md",
    "CONTRIBUTING.md",
    "CCGS Skill Testing Framework",
    "design",
    "docs",
    "production",
    "src",
)


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, text
    metadata: dict[str, object] = {}
    current_list: str | None = None
    for raw in lines[1:end]:
        if re.match(r"^\s+-\s+", raw) and current_list:
            item = re.sub(r"^\s+-\s+", "", raw).strip().strip('"\'')
            values = metadata.setdefault(current_list, [])
            if isinstance(values, list):
                values.append(item)
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.groups()
        if not value:
            metadata[key] = []
            current_list = key
            continue
        current_list = None
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        metadata[key] = value
    return metadata, "\n".join(lines[end + 1 :]).lstrip("\n")


def read_json(path: pathlib.Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def read_toml(path: pathlib.Path, errors: list[str]) -> dict[str, object]:
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
        return value
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid TOML {path}: {exc}")
        return {}


def expected_rule_targets(snapshot: pathlib.Path, errors: list[str]) -> set[str]:
    targets: set[str] = set()
    for path in sorted((snapshot / ".claude" / "rules").glob("*.md")):
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        paths = metadata.get("paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"source rule lacks paths: {path}")
            continue
        for pattern in paths:
            directory = str(pattern).split("/**", 1)[0].rstrip("/")
            targets.add(f"{directory}/AGENTS.md")
    return targets


def verify_repository(root: pathlib.Path) -> tuple[list[str], dict[str, object]]:
    root = root.resolve()
    errors: list[str] = []
    snapshot = root / "upstream" / "claude-code-game-studios-v1.0.0"
    summary: dict[str, object] = {
        "source_agents": 0,
        "converted_agents": 0,
        "source_skills": 0,
        "converted_skills": 0,
        "source_rules": 0,
        "nested_agents_files": 0,
        "source_hooks": 0,
        "mapped_hooks": 0,
    }

    if not snapshot.is_dir():
        errors.append(f"missing upstream snapshot: {snapshot}")
        return errors, summary
    for relative in REQUIRED_SNAPSHOT_PATHS:
        if not (snapshot / relative).exists():
            errors.append(f"snapshot missing required path: {relative}")
    if (snapshot / ".git").exists():
        errors.append("upstream snapshot contains .git")

    upstream = read_json(root / "upstream" / "UPSTREAM.json", errors)
    if not isinstance(upstream, dict):
        errors.append("UPSTREAM.json must be an object")
    else:
        if upstream.get("commit") != EXPECTED_COMMIT:
            errors.append("UPSTREAM.json commit mismatch")
        if upstream.get("tag") != "v1.0.0":
            errors.append("UPSTREAM.json tag mismatch")
        if upstream.get("license") != "MIT":
            errors.append("UPSTREAM.json license mismatch")
        if upstream.get("snapshot_modified") is not False:
            errors.append("UPSTREAM.json must record snapshot_modified=false")

    hash_manifest = read_json(root / "upstream" / "SNAPSHOT-SHA256.json", errors)
    manifest_files = hash_manifest.get("files") if isinstance(hash_manifest, dict) else None
    if not isinstance(manifest_files, dict) or not manifest_files:
        errors.append("snapshot hash manifest is empty")
    else:
        actual_files = {path.relative_to(snapshot).as_posix(): path for path in snapshot.rglob("*") if path.is_file()}
        if set(actual_files) != set(manifest_files):
            errors.append("snapshot file set differs from SHA-256 manifest")
        for relative, expected in manifest_files.items():
            path = actual_files.get(str(relative))
            if path is None:
                continue
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f"snapshot hash mismatch: {relative}")

    source_agents = sorted((snapshot / ".claude" / "agents").glob("*.md"))
    converted_agents = sorted((root / ".codex" / "agents").glob("*.toml"))
    summary["source_agents"] = len(source_agents)
    summary["converted_agents"] = len(converted_agents)
    if len(converted_agents) != len(source_agents):
        errors.append(f"agent count mismatch: source={len(source_agents)} converted={len(converted_agents)}")
    agent_names: list[str] = []
    for path in converted_agents:
        value = read_toml(path, errors)
        for field in ("name", "description", "developer_instructions"):
            if not isinstance(value.get(field), str) or not str(value[field]).strip():
                errors.append(f"agent missing {field}: {path}")
        if isinstance(value.get("name"), str):
            agent_names.append(str(value["name"]))
    if len(agent_names) != len(set(agent_names)):
        errors.append("duplicate custom agent name")

    source_skills = sorted((snapshot / ".claude" / "skills").glob("*/SKILL.md"))
    converted_skills = sorted((root / ".agents" / "skills").glob("*/SKILL.md"))
    summary["source_skills"] = len(source_skills)
    summary["converted_skills"] = len(converted_skills)
    if len(converted_skills) != len(source_skills):
        errors.append(f"skill count mismatch: source={len(source_skills)} converted={len(converted_skills)}")
    skill_names: list[str] = []
    for path in converted_skills:
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        for field in ("name", "description"):
            if not isinstance(metadata.get(field), str) or not str(metadata[field]).strip():
                errors.append(f"skill missing frontmatter {field}: {path}")
        if not body.strip():
            errors.append(f"empty skill body: {path}")
        if isinstance(metadata.get("name"), str):
            skill_names.append(str(metadata["name"]))
        openai_yaml = path.parent / "agents" / "openai.yaml"
        upstream_md = path.parent / "UPSTREAM.md"
        if not openai_yaml.is_file():
            errors.append(f"missing agents/openai.yaml: {path.parent}")
        else:
            yaml_text = openai_yaml.read_text(encoding="utf-8")
            if not re.search(r"(?m)^interface:\s*$", yaml_text):
                errors.append(f"openai.yaml missing interface: {openai_yaml}")
            if not re.search(r"(?ms)^policy:\s*\n\s+allow_implicit_invocation:\s*true\s*$", yaml_text):
                errors.append(f"implicit invocation not enabled: {openai_yaml}")
        if not upstream_md.is_file():
            errors.append(f"missing UPSTREAM.md: {path.parent}")
    if len(skill_names) != len(set(skill_names)):
        errors.append("duplicate skill name")

    source_rules = sorted((snapshot / ".claude" / "rules").glob("*.md"))
    expected_targets = expected_rule_targets(snapshot, errors)
    summary["source_rules"] = len(source_rules)
    summary["nested_agents_files"] = len(expected_targets)
    for relative in expected_targets:
        if not (root / relative).is_file():
            errors.append(f"missing nested AGENTS.md: {relative}")
    if not (root / "AGENTS.md").is_file():
        errors.append("missing root AGENTS.md")

    config = read_toml(root / ".codex" / "config.toml", errors)
    agents_config = config.get("agents") if isinstance(config, dict) else None
    if not isinstance(agents_config, dict) or agents_config.get("max_threads") != 4 or agents_config.get("max_depth") != 1:
        errors.append("invalid [agents] limits in config.toml")
    features = config.get("features") if isinstance(config, dict) else None
    if not isinstance(features, dict) or features.get("hooks") is not True:
        errors.append("hooks feature is not enabled")
    mcp = config.get("mcp_servers") if isinstance(config, dict) else None
    godot = mcp.get("godot") if isinstance(mcp, dict) else None
    if not isinstance(godot, dict):
        errors.append("missing project Godot MCP config")
    else:
        args = godot.get("args")
        if not isinstance(args, list) or f"@coding-solo/godot-mcp@{EXPECTED_MCP_VERSION}" not in args:
            errors.append("Godot MCP package is not pinned")
        if godot.get("enabled") is not False:
            errors.append("Godot MCP must remain disabled until Godot is installed")

    hooks_value = read_json(root / ".codex" / "hooks.json", errors)
    hooks = hooks_value.get("hooks") if isinstance(hooks_value, dict) else None
    required_events = {"SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "PostCompact", "SubagentStart", "SubagentStop", "Stop"}
    if not isinstance(hooks, dict) or set(hooks) != required_events:
        errors.append("hooks.json event set mismatch")
    else:
        for event, groups in hooks.items():
            if not isinstance(groups, list):
                errors.append(f"hook event must be a list: {event}")
                continue
            for group in groups:
                handlers = group.get("hooks") if isinstance(group, dict) else None
                if not isinstance(handlers, list):
                    errors.append(f"hook group missing handlers: {event}")
                    continue
                for handler in handlers:
                    if not isinstance(handler, dict) or handler.get("type") != "command":
                        errors.append(f"only command hooks are allowed: {event}")
                        continue
                    for key in ("command", "commandWindows"):
                        command = handler.get(key)
                        if not isinstance(command, str) or "git rev-parse --show-toplevel" not in command:
                            errors.append(f"hook does not resolve git root via {key}: {event}")
    hook_script = root / ".codex" / "hooks" / "game_studio_hook.py"
    if not hook_script.is_file():
        errors.append("missing hook script")
    else:
        try:
            compile(hook_script.read_text(encoding="utf-8"), str(hook_script), "exec")
        except SyntaxError as exc:
            errors.append(f"invalid hook Python: {exc}")

    manifest = read_json(root / "docs" / "codex-migration" / "migration-manifest.json", errors)
    if isinstance(manifest, dict):
        mapped_hooks = manifest.get("hooks")
        summary["source_hooks"] = len(list((snapshot / ".claude" / "hooks").glob("*.*")))
        summary["mapped_hooks"] = len(mapped_hooks) if isinstance(mapped_hooks, list) else 0
        if summary["source_hooks"] != summary["mapped_hooks"]:
            errors.append("hook mapping count mismatch")

    for path in root.rglob("*.json"):
        if ".git" not in path.parts and ".tmp-npm-cache" not in path.parts:
            read_json(path, errors)
    for path in root.rglob("*.toml"):
        if ".git" not in path.parts:
            read_toml(path, errors)

    sensitive_names = {".env", ".env.local", "credentials.json", "id_rsa", "id_ed25519"}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and path.name.lower() in sensitive_names:
            errors.append(f"sensitive file present: {path.relative_to(root)}")
    secret_patterns = (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"))
    for base in (root / ".codex", root / ".agents", root / "docs" / "codex-migration"):
        for path in base.rglob("*") if base.exists() else ():
            if not path.is_file() or path.suffix.lower() not in {".md", ".toml", ".json", ".yaml", ".py", ".rules"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(pattern.search(text) for pattern in secret_patterns):
                errors.append(f"credential-like content: {path.relative_to(root)}")

    forbidden_projects = ("A" + "OS", "Search" + "Lens", "Token" + " Monitor")
    for base in (root / ".codex", root / ".agents", root / "AGENTS.md"):
        paths = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in paths:
            if path.is_file() and path.name != "UPSTREAM.md":
                text = path.read_text(encoding="utf-8", errors="replace")
                if any(term in text for term in forbidden_projects):
                    errors.append(f"cross-project reference: {path.relative_to(root)}")
                for line in text.splitlines():
                    requires_cli = re.search(r"(?i)(?:run|execute|command|运行|执行).{0,24}\bclaude(?:\.exe)?\b", line)
                    is_prohibition = re.search(r"(?i)(?:do not|must not|never|禁止|不得|不运行|不执行).{0,32}\bclaude\b", line)
                    if requires_cli and not is_prohibition:
                        errors.append(f"active config requires Claude CLI: {path.relative_to(root)}")
                        break

    rules_file = root / ".codex" / "rules" / "game-studio-safety.rules"
    if not rules_file.is_file():
        errors.append("missing Codex command rules")
    else:
        rules_text = rules_file.read_text(encoding="utf-8")
        for phrase in ('["git", "push"]', '["git", "reset"]', '["git", "clean"]', '["git", "rebase"]', '["git", "commit", "--amend"]'):
            if phrase not in rules_text or 'decision = "forbidden"' not in rules_text:
                errors.append(f"safety rule missing: {phrase}")

    required_docs = (
        "architecture.md",
        "compatibility-matrix.md",
        "agents-mapping.md",
        "skills-mapping.md",
        "hooks-mapping.md",
        "rules-mapping.md",
        "godot-mcp.md",
        "verification.md",
        "runtime-validation-checklist.md",
    )
    for name in required_docs:
        if not (root / "docs" / "codex-migration" / name).is_file():
            errors.append(f"missing migration document: {name}")

    product_extensions = {".gd", ".cs", ".cpp", ".h", ".tscn", ".tres", ".gdshader"}
    for base_name in ("src", "assets", "design", "production", "prototypes"):
        base = root / base_name
        for path in base.rglob("*") if base.exists() else ():
            if path.is_file() and path.suffix.lower() in product_extensions:
                errors.append(f"unexpected product code or asset: {path.relative_to(root)}")

    return errors, summary


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    errors, summary = verify_repository(root)
    if errors:
        print("verification=failed")
        for error in errors:
            print(f"ERROR: {error}")
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 1
    print("verification=passed")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
