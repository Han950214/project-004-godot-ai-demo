from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import tomllib


EXPECTED_REPOSITORY = "https://github.com/Donchitos/Claude-Code-Game-Studios.git"
EXPECTED_TAG = "v1.0.0"
EXPECTED_COMMIT = "984023ddac0d5e27624f2baacde6105e45de375f"
EXPECTED_TREE = "45e93bee12c3f1d80052f7406f0180e9bece8382"
EXPECTED_MCP_VERSION = "0.1.1"
EXPECTED_AGENTS = 49
EXPECTED_SKILLS = 73
EXPECTED_RULES = 11
EXPECTED_HOOKS = 12
EXPECTED_SNAPSHOT_FILES = 417
ROUTER_NAME = "game-studio-router"
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
FORBIDDEN_GIT_COMMANDS = (
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
SAFE_GIT_COMMANDS = (
    "git status",
    r"git -C E:\repo status",
    "git diff",
    "git log",
    'git commit -m "normal commit"',
    "git --no-pager status",
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


def verify_snapshot(snapshot: pathlib.Path, manifest_path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    manifest = read_json(manifest_path, errors)
    if not isinstance(manifest, dict):
        errors.append("source manifest must be an object")
        return errors
    expected_metadata = {
        "repository": EXPECTED_REPOSITORY,
        "tag": EXPECTED_TAG,
        "commit": EXPECTED_COMMIT,
        "tree": EXPECTED_TREE,
        "manifest_generated_from": "verified_source_checkout",
    }
    for field, expected in expected_metadata.items():
        if manifest.get(field) != expected:
            errors.append(f"source manifest {field} mismatch: expected {expected}, got {manifest.get(field)}")
    files = manifest.get("files")
    if not isinstance(files, dict):
        errors.append("source manifest files must be an object")
        return errors
    if manifest.get("file_count") != EXPECTED_SNAPSHOT_FILES or len(files) != EXPECTED_SNAPSHOT_FILES:
        errors.append(
            f"source manifest file count mismatch: expected {EXPECTED_SNAPSHOT_FILES}, "
            f"declared={manifest.get('file_count')}, listed={len(files)}"
        )
    nested_git = [path for path in snapshot.rglob(".git")]
    if nested_git:
        errors.append("upstream snapshot contains .git")
    actual_files = {
        path.relative_to(snapshot).as_posix(): path
        for path in snapshot.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(snapshot).parts
    }
    if len(actual_files) != EXPECTED_SNAPSHOT_FILES:
        errors.append(f"snapshot file count mismatch: expected {EXPECTED_SNAPSHOT_FILES}, got {len(actual_files)}")
    expected_set = {str(relative) for relative in files}
    actual_set = set(actual_files)
    if actual_set != expected_set:
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)
        errors.append(f"snapshot file set mismatch: missing={missing[:8]}, extra={extra[:8]}")
    for relative in sorted(actual_set & expected_set):
        expected_hash = files.get(relative)
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"invalid source manifest hash: {relative}")
            continue
        actual_hash = hashlib.sha256(actual_files[relative].read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"snapshot hash mismatch: {relative}")
    return errors


def parse_restricted_yaml(text: str) -> tuple[dict[str, object], list[str]]:
    data: dict[str, object] = {}
    errors: list[str] = []
    section: str | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw:
            errors.append(f"openai.yaml line {number}: tabs are not allowed")
            continue
        if indent == 0:
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*", raw)
            if not match:
                errors.append(f"openai.yaml line {number}: expected a top-level mapping")
                section = None
                continue
            section = match.group(1)
            if section in data:
                errors.append(f"openai.yaml line {number}: duplicate section {section}")
            data[section] = {}
            continue
        if indent != 2 or section is None:
            errors.append(f"openai.yaml line {number}: only two-level mappings are supported")
            continue
        match = re.fullmatch(r"  ([A-Za-z_][A-Za-z0-9_-]*):\s*(.+)", raw)
        if not match:
            errors.append(f"openai.yaml line {number}: invalid mapping entry")
            continue
        key, raw_value = match.groups()
        container = data[section]
        if not isinstance(container, dict):
            errors.append(f"openai.yaml line {number}: invalid section {section}")
            continue
        if key in container:
            errors.append(f"openai.yaml line {number}: duplicate key {section}.{key}")
            continue
        value: object
        if raw_value in {"true", "false"}:
            value = raw_value == "true"
        elif raw_value.startswith('"'):
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                errors.append(f"openai.yaml line {number}: invalid quoted string: {exc}")
                continue
        elif raw_value.startswith("'") and raw_value.endswith("'"):
            value = raw_value[1:-1]
        else:
            value = raw_value
        container[key] = value
    return data, errors


def validate_skill_directory(skill: pathlib.Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    summary: dict[str, object] = {"name": skill.name, "implicit": None}
    skill_file = skill / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"missing SKILL.md: {skill}")
    else:
        metadata, body = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        for field in ("name", "description"):
            if not isinstance(metadata.get(field), str) or not str(metadata[field]).strip():
                errors.append(f"skill missing frontmatter {field}: {skill_file}")
        if isinstance(metadata.get("name"), str):
            summary["name"] = metadata["name"]
        if not body.strip():
            errors.append(f"empty skill body: {skill_file}")
    yaml_path = skill / "agents" / "openai.yaml"
    if not yaml_path.is_file():
        errors.append(f"missing agents/openai.yaml: {skill}")
        return errors, summary
    data, yaml_errors = parse_restricted_yaml(yaml_path.read_text(encoding="utf-8"))
    errors.extend(f"{yaml_path}: {error}" for error in yaml_errors)
    if set(data) != {"interface", "policy"}:
        errors.append(f"openai.yaml top-level keys must be interface and policy: {yaml_path}")
    interface = data.get("interface")
    required_interface = {"display_name", "short_description", "default_prompt"}
    if not isinstance(interface, dict) or set(interface) != required_interface:
        errors.append(f"openai.yaml interface must contain exactly {sorted(required_interface)}: {yaml_path}")
    elif any(not isinstance(interface.get(key), str) or not str(interface[key]).strip() for key in required_interface):
        errors.append(f"openai.yaml interface values must be non-empty strings: {yaml_path}")
    policy = data.get("policy")
    if not isinstance(policy, dict) or set(policy) != {"allow_implicit_invocation"}:
        errors.append(f"openai.yaml policy must contain only allow_implicit_invocation: {yaml_path}")
    elif not isinstance(policy.get("allow_implicit_invocation"), bool):
        errors.append(f"openai.yaml allow_implicit_invocation must be boolean: {yaml_path}")
    else:
        summary["implicit"] = policy["allow_implicit_invocation"]
    return errors, summary


def verify_skill_configuration(root: pathlib.Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    skill_root = root / ".agents" / "skills"
    directories = sorted(path for path in skill_root.iterdir() if path.is_dir()) if skill_root.is_dir() else []
    router = skill_root / ROUTER_NAME
    downstream = [path for path in directories if path.name != ROUTER_NAME]
    summary: dict[str, object] = {
        "downstream_skills": len(downstream),
        "indexed_skills": 0,
        "implicit_skills": [],
    }
    if len(downstream) != EXPECTED_SKILLS:
        errors.append(f"downstream skill count mismatch: expected {EXPECTED_SKILLS}, got {len(downstream)}")
    if not router.is_dir():
        errors.append("missing game-studio-router")
    names: list[str] = []
    implicit: list[str] = []
    for directory in directories:
        directory_errors, metadata = validate_skill_directory(directory)
        errors.extend(directory_errors)
        name = metadata.get("name")
        if isinstance(name, str):
            names.append(name)
            if metadata.get("implicit") is True:
                implicit.append(name)
        if directory.name != ROUTER_NAME and not (directory / "UPSTREAM.md").is_file():
            errors.append(f"missing UPSTREAM.md: {directory}")
        expected_implicit = directory.name == ROUTER_NAME
        if metadata.get("implicit") is not expected_implicit:
            errors.append(
                f"implicit invocation mismatch for {directory.name}: expected {str(expected_implicit).lower()}"
            )
    if len(names) != len(set(names)):
        errors.append("duplicate skill name")
    summary["implicit_skills"] = sorted(implicit)
    if sorted(implicit) != [ROUTER_NAME]:
        errors.append(f"only {ROUTER_NAME} may allow implicit invocation: got {sorted(implicit)}")
    index_path = router / "references" / "skill-index.md"
    indexed: list[str] = []
    if not index_path.is_file():
        errors.append("missing game-studio-router skill index")
    else:
        for line in index_path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\| `([^`]+)` \|", line)
            if match:
                indexed.append(match.group(1))
        downstream_names = {path.name for path in downstream}
        if set(indexed) != downstream_names or len(indexed) != len(downstream_names):
            missing = sorted(downstream_names - set(indexed))
            extra = sorted(set(indexed) - downstream_names)
            errors.append(f"skill index mismatch: missing={missing}, extra={extra}, rows={len(indexed)}")
    summary["indexed_skills"] = len(indexed)
    return errors, summary


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


def load_hook_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("verified_game_studio_hook", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load hook: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_git_guard(root: pathlib.Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    hook_path = root / ".codex" / "hooks" / "game_studio_hook.py"
    if not hook_path.is_file():
        return ["missing hook script"], {"forbidden": 0, "safe": 0}
    try:
        compile(hook_path.read_text(encoding="utf-8"), str(hook_path), "exec")
        hook = load_hook_module(hook_path)
    except (SyntaxError, OSError, RuntimeError) as exc:
        return [f"invalid hook Python: {exc}"], {"forbidden": 0, "safe": 0}
    detector = getattr(hook, "detect_forbidden_git_operation", None)
    if not callable(detector):
        return ["hook lacks detect_forbidden_git_operation"], {"forbidden": 0, "safe": 0}
    for command in FORBIDDEN_GIT_COMMANDS:
        if detector(command) is None:
            errors.append(f"dangerous Git command not detected: {command}")
    for command in SAFE_GIT_COMMANDS:
        if detector(command) is not None:
            errors.append(f"safe Git command incorrectly blocked: {command}")
    return errors, {"forbidden": len(FORBIDDEN_GIT_COMMANDS), "safe": len(SAFE_GIT_COMMANDS)}


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
    errors.extend(verify_snapshot(snapshot, root / "upstream" / "SOURCE-MANIFEST.json"))
    if (root / "upstream" / "SNAPSHOT-SHA256.json").exists():
        errors.append("legacy self-generated SNAPSHOT-SHA256.json must not exist")

    upstream = read_json(root / "upstream" / "UPSTREAM.json", errors)
    if not isinstance(upstream, dict):
        errors.append("UPSTREAM.json must be an object")
    else:
        expected_upstream = {
            "repository": EXPECTED_REPOSITORY,
            "tag": EXPECTED_TAG,
            "commit": EXPECTED_COMMIT,
            "tree": EXPECTED_TREE,
            "license": "MIT",
            "snapshot_modified": False,
        }
        for field, expected in expected_upstream.items():
            if upstream.get(field) != expected:
                errors.append(f"UPSTREAM.json {field} mismatch")

    source_agents = sorted((snapshot / ".claude" / "agents").glob("*.md"))
    converted_agents = sorted((root / ".codex" / "agents").glob("*.toml"))
    summary["source_agents"] = len(source_agents)
    summary["converted_agents"] = len(converted_agents)
    if len(source_agents) != EXPECTED_AGENTS or len(converted_agents) != EXPECTED_AGENTS:
        errors.append(
            f"agent count mismatch: expected={EXPECTED_AGENTS}, source={len(source_agents)}, converted={len(converted_agents)}"
        )
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
    summary["source_skills"] = len(source_skills)
    summary["converted_skills"] = len(
        [path for path in (root / ".agents" / "skills").glob("*/SKILL.md") if path.parent.name != ROUTER_NAME]
    )
    if len(source_skills) != EXPECTED_SKILLS:
        errors.append(f"source skill count mismatch: expected {EXPECTED_SKILLS}, got {len(source_skills)}")
    skill_errors, skill_summary = verify_skill_configuration(root)
    errors.extend(skill_errors)
    summary.update(skill_summary)
    source_skill_names = {path.parent.name for path in source_skills}
    converted_skill_names = {
        path.name for path in (root / ".agents" / "skills").iterdir() if path.is_dir() and path.name != ROUTER_NAME
    }
    if source_skill_names != converted_skill_names:
        errors.append("source and converted downstream skill names differ")

    source_rules = sorted((snapshot / ".claude" / "rules").glob("*.md"))
    expected_targets = expected_rule_targets(snapshot, errors)
    summary["source_rules"] = len(source_rules)
    summary["nested_agents_files"] = len(expected_targets)
    if len(source_rules) != EXPECTED_RULES or len(expected_targets) != EXPECTED_RULES:
        errors.append(
            f"rule count mismatch: expected={EXPECTED_RULES}, source={len(source_rules)}, mapped={len(expected_targets)}"
        )
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
    required_events = {
        "SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "PostCompact",
        "SubagentStart", "SubagentStop", "Stop",
    }
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
    guard_errors, guard_summary = verify_git_guard(root)
    errors.extend(guard_errors)
    summary.update({f"git_guard_{key}": value for key, value in guard_summary.items()})

    manifest = read_json(root / "docs" / "codex-migration" / "migration-manifest.json", errors)
    source_hooks = sorted((snapshot / ".claude" / "hooks").glob("*.*"))
    summary["source_hooks"] = len(source_hooks)
    if len(source_hooks) != EXPECTED_HOOKS:
        errors.append(f"source hook count mismatch: expected {EXPECTED_HOOKS}, got {len(source_hooks)}")
    if isinstance(manifest, dict):
        mapped_hooks = manifest.get("hooks")
        summary["mapped_hooks"] = len(mapped_hooks) if isinstance(mapped_hooks, list) else 0
        if summary["mapped_hooks"] != EXPECTED_HOOKS:
            errors.append(f"hook mapping count mismatch: expected {EXPECTED_HOOKS}, got {summary['mapped_hooks']}")
        router_manifest = manifest.get("router")
        if not isinstance(router_manifest, dict) or router_manifest.get("name") != ROUTER_NAME:
            errors.append("migration manifest lacks router metadata")

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
    secret_patterns = (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    )
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
        for executable in ("git", "git.exe"):
            for operation in ("push", "reset", "clean", "rebase"):
                phrase = f'["{executable}", "{operation}"]'
                if phrase not in rules_text:
                    errors.append(f"safety rule missing: {phrase}")
            amend = f'["{executable}", "commit", "--amend"]'
            if amend not in rules_text:
                errors.append(f"safety rule missing: {amend}")
        if 'decision = "forbidden"' not in rules_text:
            errors.append("safety rules are not forbidden")

    required_docs = (
        "architecture.md", "compatibility-matrix.md", "agents-mapping.md", "skills-mapping.md",
        "hooks-mapping.md", "rules-mapping.md", "godot-mcp.md", "verification.md",
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
