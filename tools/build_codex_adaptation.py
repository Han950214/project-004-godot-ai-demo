from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "upstream" / "claude-code-game-studios-v1.0.0"
SOURCE_COMMIT = "984023ddac0d5e27624f2baacde6105e45de375f"
SOURCE_TREE = "45e93bee12c3f1d80052f7406f0180e9bece8382"
SOURCE_REPOSITORY = "https://github.com/Donchitos/Claude-Code-Game-Studios.git"
SOURCE_TAG = "v1.0.0"
EXPECTED_SNAPSHOT_FILES = 417
MCP_VERSION = "0.1.1"


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


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
            value = re.sub(r"^\s+-\s+", "", raw).strip().strip('"\'')
            cast = metadata.setdefault(current_list, [])
            if isinstance(cast, list):
                cast.append(value)
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
        if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
            try:
                value = json.loads(value) if value.startswith('"') else value[1:-1]
            except json.JSONDecodeError:
                value = value[1:-1]
        metadata[key] = value
    return metadata, "\n".join(lines[end + 1 :]).lstrip("\n")


def adapt_text(text: str, skill_names: list[str]) -> str:
    replacements = [
        ("Claude Code Game Studios", "Codex Game Studio"),
        ("Claude Code", "Codex"),
        ("Claude", "Codex"),
        ("CLAUDE-local-template.md", "AGENTS-local-template.md"),
        ("CLAUDE.local.md", "AGENTS.md"),
        ("CLAUDE.md", "AGENTS.md"),
        (".claude/docs/", "docs/game-studio-reference/"),
        (".claude/skills/", ".agents/skills/"),
        (".claude/agents/", ".codex/agents/"),
        (".claude/hooks/", ".codex/hooks/"),
        (".claude/rules/", "the applicable nested AGENTS.md files under "),
        (".claude/settings.local.json", ".codex/config.toml"),
        (".claude/settings.json", ".codex/hooks.json"),
        (".claude/", ".codex/"),
        ("AskUserQuestion", "a focused user decision question"),
        ("Write tool", "file-editing capability"),
        ("Edit tool", "file-editing capability"),
        ("You have access to the Task tool", "You may accept single-level Codex subagent delegation from the main agent"),
        ("Use the Task tool", "Use optional Codex subagent delegation"),
        ("via `Task`", "through Codex subagent delegation"),
        ("via Task", "through an optional Codex subagent"),
        ("using Task", "using an optional Codex subagent"),
        ("Task tool", "Codex subagent delegation"),
        ("Task subagent", "Codex subagent"),
        ("Task calls", "subagent calls"),
        ("Task call", "subagent call"),
        ("Task prompt", "subagent prompt"),
        ("Task agents", "subagents"),
        ("parallel Task", "parallel subagent"),
        ("allowed-tools", "Codex tool requirements"),
        ("user-invocable", "explicit invocation"),
        ("argument-hint", "default prompt guidance"),
        ("The user approves all architectural decisions and file changes.",
         "The user retains final product and creative decisions; routine in-scope implementation follows the active task authorization."),
        ("The user approves all decisions and file changes.",
         "The user retains final product and creative decisions; routine in-scope implementation follows the active task authorization."),
        ("Get approval before writing files:", "Confirm scope before consequential or product-defining writes:"),
        ("Get approval before writing files", "Confirm scope before consequential or product-defining writes"),
        ("May I write this to", "Confirm the requested destination when it is ambiguous:"),
        ("May I write this accessibility audit to", "Write the approved accessibility audit to"),
        ("No commits without user instruction", "Create commits only when the active task explicitly requests them"),
        ("Use at every decision point", "Use only at consequential product decision points"),
        ("the `a focused user decision question` tool", "a focused user decision question"),
        ("Call `a focused user decision question`", "Present a focused user decision question"),
        ("Wait for \"yes\" before using Write/Edit tools", "Proceed once the active task or user has authorized that scope"),
    ]
    for source, target in replacements:
        text = text.replace(source, target)
    for source, target in {
        "WebSearch": "web search",
        "WebFetch": "open the referenced web page",
        "TodoWrite": "task plan update",
        "Glob": "file search",
        "Grep": "`rg` text search",
        "Bash": "shell",
    }.items():
        text = re.sub(rf"\b{source}\b", target, text)
    for name in sorted(skill_names, key=len, reverse=True):
        text = re.sub(rf"(?<![A-Za-z0-9_])/{re.escape(name)}\b", f"${name}", text)
    text = re.sub(r"\bmodel:\s*(?:sonnet|opus|haiku)\b", "", text, flags=re.I)
    return "\n".join(line.rstrip() for line in text.splitlines())


def narrow_description(name: str, original: str, skill_names: list[str]) -> str:
    original = re.sub(r"\s+", " ", adapt_text(original, skill_names)).strip()
    if not original:
        original = f"执行 {name} 工作流。"
    if name.startswith("team-"):
        return (
            f"{original} 仅在用户明确要求团队协作，或任务存在互斥且可独立并行的工作面时使用；"
            "不得用于普通单文件修改或自动推进下一制作阶段。"
        )
    return f"{original} 当用户明确点名该流程或当前任务与其专业目标直接匹配时使用；不用于无关的一般开发任务。"


def routing_metadata(name: str, description: str) -> dict[str, str]:
    categories = {
        "onboarding": {"adopt", "help", "onboard", "project-stage-detect", "setup-engine", "start"},
        "concept-and-design": {
            "architecture-decision", "art-bible", "asset-spec", "brainstorm", "create-architecture",
            "create-control-manifest", "design-system", "map-systems", "quick-design", "ux-design",
        },
        "review-and-analysis": {
            "architecture-review", "asset-audit", "balance-check", "consistency-check", "content-audit",
            "design-review", "estimate", "perf-profile", "reverse-document", "review-all-gdds", "scope-check",
            "security-audit", "tech-debt", "ux-review",
        },
        "production": {
            "create-epics", "create-stories", "dev-story", "milestone-review", "propagate-design-change",
            "retrospective", "sprint-plan", "sprint-status", "story-done", "story-readiness",
        },
        "quality": {
            "bug-report", "bug-triage", "code-review", "playtest-report", "qa-plan", "regression-suite",
            "smoke-check", "soak-test", "test-evidence-review", "test-flakiness", "test-helpers", "test-setup",
        },
        "release-and-operations": {
            "changelog", "day-one-patch", "hotfix", "launch-checklist", "localize", "patch-notes",
            "release-checklist",
        },
        "prototyping": {"prototype", "vertical-slice"},
        "studio-meta": {"gate-check", "skill-improve", "skill-test"},
    }
    category = "team-collaboration" if name.startswith("team-") else next(
        (candidate for candidate, names in categories.items() if name in names), "studio-meta"
    )
    stages = {
        "onboarding": "discovery/setup",
        "concept-and-design": "concept/pre-production",
        "review-and-analysis": "current-stage review",
        "production": "pre-production/production",
        "quality": "testing/acceptance",
        "release-and-operations": "release/live operations",
        "prototyping": "concept/pre-production",
        "team-collaboration": "current-stage collaboration",
        "studio-meta": "any stage",
    }
    agent_rules = (
        (("security",), "security-engineer"),
        (("localize",), "localization-lead"),
        (("audio",), "audio-director"),
        (("narrative",), "narrative-director"),
        (("art", "asset"), "art-director"),
        (("ux", "ui"), "ux-designer"),
        (("qa", "test", "bug", "smoke", "soak", "playtest", "regression"), "qa-lead"),
        (("release", "patch", "hotfix", "changelog", "launch"), "release-manager"),
        (("architecture", "perf", "tech-debt", "setup-engine"), "technical-director"),
        (("dev-story", "code-review", "prototype", "vertical-slice"), "lead-programmer"),
        (("design", "balance", "map-systems", "combat"), "game-designer"),
    )
    likely_agent = next(
        (agent for needles, agent in agent_rules if any(needle in name for needle in needles)), "producer"
    )
    use_when = description.split("。", 1)[0].split(". ", 1)[0].strip()
    if len(use_when) > 180:
        use_when = use_when[:177].rstrip() + "..."
    do_not = {
        "team-collaboration": "普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。",
        "release-and-operations": "尚未进入发布或线上运维阶段时不要使用。",
        "quality": "没有可检查实现、构建、缺陷或验收输入时不要使用。",
        "prototyping": "目标是直接交付正式生产实现且无需验证假设时不要使用。",
    }.get(category, "任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。")
    return {
        "name": name,
        "category": category,
        "stage": stages[category],
        "use_when": use_when,
        "do_not_use_when": do_not,
        "likely_agent": likely_agent,
    }


def build_router(rows: list[dict[str, str]]) -> None:
    router = ROOT / ".agents" / "skills" / "game-studio-router"
    skill = """---
name: game-studio-router
description: "在用户提出游戏策划、原型、系统设计、开发、测试、发布或明确团队协作任务，但未点名具体 Game Studio Skill 时自动路由。普通非游戏任务、已显式调用下游 $skill 或仅需简单问答时不触发。"
---

# Game Studio Router

## 目标

把用户的游戏开发请求路由到最窄、最合适的项目 Skill。用户不需要预先知道 Skill 名称。

## 路由流程

1. 只读取识别当前制作阶段和任务类别所需的最小上下文；不扫描全部历史。
2. 读取 `references/skill-index.md`，按 `stage`、`category`、`use_when` 和 `do_not_use_when` 筛选。
3. 默认只选择一个下游 Skill，并读取该 Skill 的 `SKILL.md` 后执行其流程。
4. 仅当任务确实存在两个或三个互斥且可独立并行的工作面时，才增加第二或第三个下游 Skill；写入范围必须互斥。
5. 不一次加载全部 73 个下游 Skill，不一次召集全部 Agent，不允许子代理递归委派。
6. 不自动进入下一制作阶段；阶段转换、产品方向和创意取舍仍由用户决定。
7. 如果用户已显式调用 `$skill-name`，直接遵循该 Skill，不再二次路由。

## 输出

内部记录选择的阶段、类别、下游 Skill 和原因；只向用户呈现完成任务所需的信息，不要求用户学习路由表。
"""
    write(router / "SKILL.md", skill)
    write(
        router / "agents" / "openai.yaml",
        "interface:\n"
        "  display_name: \"Game Studio Router\"\n"
        "  short_description: \"自动选择最窄的游戏工作室流程，不推进未授权阶段。\"\n"
        "  default_prompt: \"识别当前游戏开发阶段和任务类别，并路由到最合适的单个下游 Skill。\"\n"
        "policy:\n"
        "  allow_implicit_invocation: true\n",
    )
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)
    sections = [
        "# Game Studio Skill Index",
        "",
        "本索引只供 `game-studio-router` 定向选择下游 Skill；73 个下游 Skill 均关闭隐式调用，但仍支持显式 `$skill-name`。",
        "",
    ]
    for category in sorted(grouped):
        sections.extend(
            [
                f"## {category}",
                "",
                "| name | stage | use_when | do_not_use_when | likely_agent |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in sorted(grouped[category], key=lambda item: item["name"]):
            values = [
                f"`{row['name']}`",
                row["stage"],
                row["use_when"],
                row["do_not_use_when"],
                f"`{row['likely_agent']}`",
            ]
            sections.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
        sections.append("")
    write(router / "references" / "skill-index.md", "\n".join(sections))


def checkout_git(source: pathlib.Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={source.as_posix()}", "-C", str(source), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed for verified source: {result.stderr.strip()}")
    return result.stdout.strip()


def source_files(base: pathlib.Path) -> dict[str, pathlib.Path]:
    return {
        path.relative_to(base).as_posix(): path
        for path in sorted(base.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(base).parts
    }


def sha256_files(files: dict[str, pathlib.Path]) -> dict[str, str]:
    return {relative: hashlib.sha256(path.read_bytes()).hexdigest() for relative, path in files.items()}


def build_source_manifest(verified_source: pathlib.Path) -> None:
    verified_source = verified_source.resolve()
    if not (verified_source / ".git").exists():
        raise RuntimeError(f"verified source is not a Git checkout: {verified_source}")
    head = checkout_git(verified_source, "rev-parse", "HEAD")
    tree = checkout_git(verified_source, "rev-parse", "HEAD^{tree}")
    tag_commit = checkout_git(verified_source, "rev-list", "-n", "1", SOURCE_TAG)
    origin = checkout_git(verified_source, "remote", "get-url", "origin")
    status = checkout_git(verified_source, "status", "--porcelain")
    if head != SOURCE_COMMIT or tag_commit != SOURCE_COMMIT:
        raise RuntimeError(f"verified source commit mismatch: HEAD={head}, tag={tag_commit}")
    if tree != SOURCE_TREE:
        raise RuntimeError(f"verified source tree mismatch: expected {SOURCE_TREE}, got {tree}")
    if origin.rstrip("/") != SOURCE_REPOSITORY.rstrip("/"):
        raise RuntimeError(f"verified source origin mismatch: {origin}")
    if status:
        raise RuntimeError("verified source checkout is not clean")

    verified_files = source_files(verified_source)
    snapshot_files = source_files(SNAPSHOT)
    if len(verified_files) != EXPECTED_SNAPSHOT_FILES:
        raise RuntimeError(
            f"verified source file count mismatch: expected {EXPECTED_SNAPSHOT_FILES}, got {len(verified_files)}"
        )
    if set(verified_files) != set(snapshot_files):
        missing = sorted(set(verified_files) - set(snapshot_files))
        extra = sorted(set(snapshot_files) - set(verified_files))
        raise RuntimeError(f"snapshot file set mismatch: missing={missing[:8]}, extra={extra[:8]}")
    verified_hashes = sha256_files(verified_files)
    snapshot_hashes = sha256_files(snapshot_files)
    mismatches = [relative for relative in verified_hashes if verified_hashes[relative] != snapshot_hashes[relative]]
    if mismatches:
        raise RuntimeError(f"snapshot hash mismatch: {mismatches[:8]}")

    manifest = {
        "repository": SOURCE_REPOSITORY,
        "tag": SOURCE_TAG,
        "commit": SOURCE_COMMIT,
        "tree": SOURCE_TREE,
        "manifest_generated_from": "verified_source_checkout",
        "file_count": len(verified_hashes),
        "files": verified_hashes,
    }
    write(ROOT / "upstream" / "SOURCE-MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    metadata = {
        "repository": SOURCE_REPOSITORY,
        "tag": SOURCE_TAG,
        "commit": SOURCE_COMMIT,
        "tree": SOURCE_TREE,
        "license": "MIT",
        "snapshot_modified": False,
    }
    write(ROOT / "upstream" / "UPSTREAM.json", json.dumps(metadata, ensure_ascii=False, indent=2))


def build_root_files(agent_names: list[str], skill_names: list[str]) -> None:
    directors = [name for name in agent_names if name.endswith("-director")]
    leads = [name for name in agent_names if name in {"producer", "lead-programmer", "qa-lead", "localization-lead", "release-manager"}]
    readme = f"""
# Codex Game Studio

这是基于 Claude Code Game Studios v1.0.0 的非官方 Codex 适配项目。固定上游 commit 为 `{SOURCE_COMMIT}`，完整未修改快照位于 `upstream/claude-code-game-studios-v1.0.0/`。

Codex 适配层位于 `AGENTS.md`、`.agents/skills/`、`.codex/agents/`、`.codex/hooks.json`、`.codex/rules/` 和 `.codex/config.toml`。本阶段已完成静态迁移；Godot 与 Godot MCP 实机验证因本机缺少 Godot 而延后，不宣称所有 Claude Hook 与 Codex 完全等价。

当前统计：{len(agent_names)} 个自定义 Agent、{len(skill_names)} 个下游 Skill、1 个自动路由 Skill、11 个路径级规则映射。首次使用前请在 Codex 中信任项目级配置与 Hooks；用户可自然描述游戏开发任务交给 `game-studio-router`，也可显式调用 `$start`、`$help`、`$project-stage-detect` 或其他下游 Skill。

后续安装 Godot 4.x stable 后，按 `docs/codex-migration/runtime-validation-checklist.md` 完成独立运行验收。
"""
    write(ROOT / "README.md", readme)
    write(
        ROOT / ".gitignore",
        "__pycache__/\n*.py[cod]\n.tmp-npm-cache/\n.godot/\n.env\n.env.*\n",
    )
    write(
        ROOT / ".gitattributes",
        "* text=auto eol=lf\nupstream/claude-code-game-studios-v1.0.0/** binary\n",
    )

    agents_md = f"""
# Codex Game Studio 项目规则

## 定位与技术栈

- 本项目是 Claude Code Game Studios v1.0.0 的 Codex 静态适配层；上游只读快照不得修改。
- 默认目标引擎为 Godot 4.x stable，默认语言为 GDScript。Unity 与 Unreal 角色仅为完整迁移保留，除非用户明确改变引擎，不得主动路由给它们。
- 用户拥有产品、创意、范围与取舍的最终决策权；Agent 负责分析、实现和验证。非关键实现细节采用合理默认并记录，只有会改变产品方向或超出授权范围时才询问。

## 路由与层级

- 制作与总监层负责方向、跨部门冲突和质量门禁：{', '.join(directors + ['producer'])}。
- 部门负责人负责拆解、验收和升级：{', '.join(leads)}。
- 专家只在各自领域内工作；跨领域改动先报告给对应负责人或主 Agent，不得擅自扩大范围。
- 自定义 Agent 位于 `.codex/agents/`，Skill 位于 `.agents/skills/`。未显式点名 Skill 时由 `game-studio-router` 从索引选择最窄流程；只按任务需要选择角色，不得一次加载全部 Skill 或召集全部角色。
- 子代理最多 4 个线程、深度 1；只读且互斥的分析可并行，写入默认由主 Agent 单线程完成。子代理不得继续创建子代理。

## 工作流

1. 先确认当前制作阶段、输入文档和验收标准；可使用 `$start`、`$project-stage-detect`、`$help` 等对应 Skill。
2. 设计决策先给出选项、取舍和推荐；产品方向由用户决定。
3. 实现遵守最近的嵌套 `AGENTS.md`。Godot API 以项目声明版本为准，不凭记忆臆测。
4. 每个实现阶段提供与风险相称的自动测试、静态检查或试玩证据；无法运行的验证必须明确标为 deferred。
5. 不得自动进入下一制作阶段。

## Git 与安全

- 禁止自动 `git push`、`git reset`、`git clean`、`git rebase`、`git commit --amend` 和强制推送。
- 不读取或提交 `.env`、密钥、Token、Cookie 或凭据；不修改用户级 Codex 配置、系统设置或仓库外文件。
- 创建 commit 必须由当前任务明确授权；禁止 push。
- 不运行上游 Claude 脚本或安装脚本。所有上游材料仅用于审计和升级。

## 目录边界

- `upstream/`：不可编辑的来源快照与校验清单。
- `.agents/skills/`：Codex Skill；每项含 `SKILL.md`、`agents/openai.yaml`、`UPSTREAM.md`。
- `.codex/agents/`：项目级自定义 Agent。
- `.codex/hooks/`、`.codex/hooks.json`：经适配的 Codex command Hooks。
- `docs/game-studio-reference/`：由上游文档派生并转换路径/术语的活动参考。
- `docs/codex-migration/`：架构、映射、兼容性与验收证据。
- `src/`、`assets/`、`design/`、`tests/`、`prototypes/`：对应嵌套规则只影响各自子树。
"""
    write(ROOT / "AGENTS.md", agents_md)


def build_reference_docs(skill_names: list[str]) -> None:
    source = SNAPSHOT / ".claude" / "docs"
    target = ROOT / "docs" / "game-studio-reference"
    stale = target / "CLAUDE-local-template.md"
    if stale.exists():
        stale.unlink()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if relative.name == "CLAUDE-local-template.md":
            relative = relative.with_name("AGENTS-local-template.md")
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}:
            write(destination, adapt_text(path.read_text(encoding="utf-8"), skill_names))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    write(
        target / "README.md",
        "# 活动参考文档\n\n本目录由固定上游 `.claude/docs/` 派生，已将路径、命令和工具语义适配为 Codex。原始未修改版本保留在 `upstream/`。",
    )


def build_agents(skill_names: list[str]) -> list[dict[str, object]]:
    source_dir = SNAPSHOT / ".claude" / "agents"
    target_dir = ROOT / ".codex" / "agents"
    mappings: list[dict[str, object]] = []
    preface = """## Codex 适配约束

- 只在当前仓库和受命领域内工作；不得跨仓库或自主扩大范围。
- 用户保留产品与创意最终决策权。仅关键产品决策需要询问；非关键实现细节采用合理默认并记录。
- 可接受主 Agent 的单层委派，但不得递归创建子代理，也不得自动召集其他全部角色。
- 不得自主 push、reset、clean、rebase 或 amend。写入与提交必须遵守当前任务授权和最近的 AGENTS.md。
- Claude 专属模型、工具许可和斜杠命令不构成 Codex 权限；使用当前会话实际提供的能力。

"""
    for source in sorted(source_dir.glob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"))
        name = str(metadata.get("name") or source.stem)
        description = adapt_text(str(metadata.get("description") or f"Use for {name} domain work."), skill_names)
        adapted = preface + adapt_text(body, skill_names)
        toml = (
            f"name = {json.dumps(name, ensure_ascii=False)}\n"
            f"description = {json.dumps(description, ensure_ascii=False)}\n"
            f"developer_instructions = {json.dumps(adapted, ensure_ascii=False)}\n"
        )
        write(target_dir / f"{name}.toml", toml)
        removed = [key for key in ("tools", "model", "maxTurns") if key in metadata]
        mappings.append(
            {
                "source_agent": f".claude/agents/{source.name}",
                "target_toml": f".codex/agents/{name}.toml",
                "status": "converted",
                "claude_specific_fields_removed": removed,
                "behavior_differences": "继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。",
            }
        )
    return mappings


def build_skills(skill_names: list[str]) -> list[dict[str, object]]:
    source_dir = SNAPSHOT / ".claude" / "skills"
    target_dir = ROOT / ".agents" / "skills"
    mappings: list[dict[str, object]] = []
    routing_rows: list[dict[str, str]] = []
    adaptation = """## Codex 适配约束

- 将本工作流视为项目级 Skill，而不是 Codex 内置斜杠命令。
- 本下游 Skill 默认不隐式调用；仅由用户显式 `$skill-name` 或 `game-studio-router` 定向选择。不得自动启动完整制作流程或推进下一阶段。
- 用户保留产品与创意最终决策权；非关键实现细节采用合理默认并记录。
- 如需子代理，只允许单层、最多 3 个、互斥写入范围；不得多 Agent 修改同一文件。
- 使用当前 Codex 工具与沙箱；原工具许可、模型字段和权限语法已移除。

"""
    for source_skill in sorted(p for p in source_dir.iterdir() if p.is_dir()):
        source_file = source_skill / "SKILL.md"
        metadata, body = parse_frontmatter(source_file.read_text(encoding="utf-8"))
        name = str(metadata.get("name") or source_skill.name)
        description = narrow_description(name, str(metadata.get("description") or ""), skill_names)
        target = target_dir / name
        frontmatter = f"---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"
        write(target / "SKILL.md", frontmatter + adaptation + adapt_text(body, skill_names))
        short = description[:180]
        openai_yaml = (
            "interface:\n"
            f"  display_name: {json.dumps(name, ensure_ascii=False)}\n"
            f"  short_description: {json.dumps(short, ensure_ascii=False)}\n"
            f"  default_prompt: {json.dumps('使用 $' + name + ' 完成当前明确范围内的工作。', ensure_ascii=False)}\n\n"
            "policy:\n"
            "  allow_implicit_invocation: false\n"
        )
        write(target / "agents" / "openai.yaml", openai_yaml)
        upstream = f"""
# Upstream mapping

- repository: {SOURCE_REPOSITORY}
- tag: v1.0.0
- commit: {SOURCE_COMMIT}
- source: `upstream/claude-code-game-studios-v1.0.0/.claude/skills/{source_skill.name}/SKILL.md`
- status: converted

原始文件保持在上游快照中。本目录移除了 Claude 专属 frontmatter，将斜杠命令、提问、委派、路径和权限语义适配为 Codex。
"""
        write(target / "UPSTREAM.md", upstream)
        removed = [key for key in ("allowed-tools", "model", "user-invocable", "argument-hint") if key in metadata]
        mappings.append(
            {
                "source_skill": f".claude/skills/{source_skill.name}/SKILL.md",
                "target_skill": f".agents/skills/{name}/SKILL.md",
                "status": "converted",
                "claude_specific_fields_removed": removed,
                "behavior_differences": "下游 Skill 关闭隐式调用；支持显式 $skill 或由 game-studio-router 定向选择；团队 Skill 最多 3 个单层子代理。",
            }
        )
        routing_rows.append(routing_metadata(name, description))
    build_router(routing_rows)
    return mappings


def build_rules(skill_names: list[str]) -> list[dict[str, object]]:
    mappings: list[dict[str, object]] = []
    for source in sorted((SNAPSHOT / ".claude" / "rules").glob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"))
        paths = metadata.get("paths", [])
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"rule has no paths: {source}")
        target_paths: list[str] = []
        for pattern in paths:
            directory = str(pattern).split("/**", 1)[0].rstrip("/")
            target = ROOT / directory / "AGENTS.md"
            title = re.search(r"^#\s+(.+)$", body, flags=re.M)
            heading = title.group(1) if title else source.stem
            content = (
                f"# {heading}\n\n"
                f"本文件只适用于 `{directory}/` 子树。来源：`upstream/claude-code-game-studios-v1.0.0/.claude/rules/{source.name}`。\n\n"
                + re.sub(r"^#\s+.+?\n", "", adapt_text(body, skill_names), count=1, flags=re.M).lstrip()
            )
            write(target, content)
            target_paths.append(target.relative_to(ROOT).as_posix())
        mappings.append(
            {
                "source_rule": f".claude/rules/{source.name}",
                "source_paths": paths,
                "target_agents_md": target_paths,
                "status": "converted",
                "behavior_differences": "由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。",
            }
        )

    command_rules = """# 从上游 .claude/settings.json 的 shell deny 列表迁移。
prefix_rule(pattern = ["git", "push"], decision = "forbidden", justification = "本项目禁止 push；仅创建本地提交。", match = ["git push", "git push origin main"])
prefix_rule(pattern = ["git", "reset"], decision = "forbidden", justification = "禁止改写或丢弃工作区历史。", match = ["git reset --hard HEAD~1"])
prefix_rule(pattern = ["git", "clean"], decision = "forbidden", justification = "禁止自动删除未跟踪文件。", match = ["git clean -fd"])
prefix_rule(pattern = ["git", "rebase"], decision = "forbidden", justification = "禁止自动改写提交历史。", match = ["git rebase main"])
prefix_rule(pattern = ["git", "commit", "--amend"], decision = "forbidden", justification = "禁止 amend；需要修复时创建新提交。", match = ["git commit --amend"])
prefix_rule(pattern = ["git.exe", "push"], decision = "forbidden", justification = "本项目禁止 push；仅创建本地提交。", match = ["git.exe push origin main"])
prefix_rule(pattern = ["git.exe", "reset"], decision = "forbidden", justification = "禁止改写或丢弃工作区历史。", match = ["git.exe reset --hard HEAD"])
prefix_rule(pattern = ["git.exe", "clean"], decision = "forbidden", justification = "禁止自动删除未跟踪文件。", match = ["git.exe clean -fd"])
prefix_rule(pattern = ["git.exe", "rebase"], decision = "forbidden", justification = "禁止自动改写提交历史。", match = ["git.exe rebase main"])
prefix_rule(pattern = ["git.exe", "commit", "--amend"], decision = "forbidden", justification = "禁止 amend；需要修复时创建新提交。", match = ["git.exe commit --amend"])
prefix_rule(pattern = ["rm", "-rf"], decision = "forbidden", justification = "禁止递归强制删除；改用精确、可审查的文件操作。", match = ["rm -rf build"])
prefix_rule(pattern = ["Remove-Item", "-Recurse", "-Force"], decision = "forbidden", justification = "禁止 PowerShell 递归强制删除。", match = ["Remove-Item -Recurse -Force build"])
"""
    write(ROOT / ".codex" / "rules" / "game-studio-safety.rules", command_rules)
    return mappings


HOOK_SCRIPT = r'''from __future__ import annotations

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


def split_shell_segments(command: str) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for character in command:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if character in {"\\", "`"}:
            current.append(character)
            escaped = True
            continue
        if quote is not None:
            current.append(character)
            if character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            current.append(character)
            quote = character
            continue
        if character in {";", "&", "|", "\r", "\n"}:
            segment = "".join(current).strip()
            if segment:
                segments.append(segment)
            current = []
            continue
        current.append(character)
    segment = "".join(current).strip()
    if segment:
        segments.append(segment)
    return segments


def nested_shell_commands(command: str) -> list[str]:
    nested: list[str] = []
    try:
        tokens = [token.strip('"\'') for token in shlex.split(command, posix=False)]
    except ValueError:
        tokens = []
    wrappers = {
        "powershell": {"-command", "-c"},
        "powershell.exe": {"-command", "-c"},
        "pwsh": {"-command", "-c"},
        "pwsh.exe": {"-command", "-c"},
        "cmd": {"/c", "/k"},
        "cmd.exe": {"/c", "/k"},
        "bash": {"-c", "-lc"},
        "bash.exe": {"-c", "-lc"},
        "sh": {"-c"},
        "sh.exe": {"-c"},
    }
    for index, token in enumerate(tokens):
        executable = token.replace("/", "\\").rsplit("\\", 1)[-1].lower()
        options = wrappers.get(executable)
        if options is None:
            continue
        for option_index in range(index + 1, len(tokens) - 1):
            if tokens[option_index].lower() in options:
                nested.append(tokens[option_index + 1])
                break

    visible = list(command)
    in_single_quote = False
    escaped = False
    for index, character in enumerate(command):
        if escaped:
            if in_single_quote:
                visible[index] = " "
            escaped = False
            continue
        if character == "\\":
            if in_single_quote:
                visible[index] = " "
            escaped = True
            continue
        if character == "'":
            visible[index] = " "
            in_single_quote = not in_single_quote
            continue
        if in_single_quote:
            visible[index] = " "
    executable_text = "".join(visible)
    nested.extend(match.group(1) for match in re.finditer(r"\$\(([^()]*)\)", executable_text))
    nested.extend(match.group(1) for match in re.finditer(r"`([^`]*)`", executable_text))

    quote: str | None = None
    escaped = False
    stack: list[int] = []
    for index, character in enumerate(command):
        if escaped:
            escaped = False
            continue
        if character in {"\\", "`"}:
            escaped = True
            continue
        if quote is not None:
            if character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
            continue
        if character == "(":
            stack.append(index + 1)
            continue
        if character == ")" and stack:
            start = stack.pop()
            value = command[start:index].strip()
            if value:
                nested.append(value)
    return nested


def detect_forbidden_git_operation(command: str, depth: int = 0) -> str | None:
    if depth > 8:
        return "命令嵌套过深，无法安全验证 Git 操作。"
    for segment in split_shell_segments(command):
        parsed = parse_git_operation(segment)
        if parsed is None:
            continue
        subcommand, args = parsed
        if subcommand in {"push", "reset", "clean", "rebase"}:
            return f"本项目禁止 git {subcommand}。"
        if subcommand == "commit" and any(arg == "--amend" or arg.startswith("--amend=") for arg in args):
            return "本项目禁止 git commit --amend。"
    for nested in nested_shell_commands(command):
        forbidden = detect_forbidden_git_operation(nested, depth + 1)
        if forbidden:
            return forbidden
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
'''


def hook_handler(mode: str, status: str) -> dict[str, object]:
    posix = f'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/game_studio_hook.py" {mode}'
    windows = (
        'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
        "$root = git rev-parse --show-toplevel; "
        "$python = $null; "
        "if ($env:CODEX_PYTHON -and (Test-Path -LiteralPath $env:CODEX_PYTHON -PathType Leaf)) { "
        "$python = $env:CODEX_PYTHON "
        "} else { "
        "$bundled = Join-Path $env:USERPROFILE '.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'; "
        "if (Test-Path -LiteralPath $bundled -PathType Leaf) { "
        "$python = $bundled "
        "} else { "
        "$command = Get-Command python -CommandType Application -ErrorAction SilentlyContinue; "
        "if ($command) { $python = $command.Source } "
        "} "
        "}; "
        "if (-not $python) { throw 'Game Studio Hook requires an existing Python interpreter.' }; "
        f"& $python (Join-Path $root '.codex/hooks/game_studio_hook.py') {mode}"
        '"'
    )
    return {"type": "command", "command": posix, "commandWindows": windows, "timeout": 30, "statusMessage": status}


def hook_configuration() -> dict[str, object]:
    return {
        "hooks": {
            "SessionStart": [{"matcher": "startup|resume|clear|compact", "hooks": [hook_handler("session-start", "加载 Game Studio 上下文")]}],
            "PreToolUse": [{"matcher": "^Bash$", "hooks": [hook_handler("pre-tool", "执行 Game Studio 命令安全检查")]}],
            "PostToolUse": [{"matcher": "Edit|Write", "hooks": [hook_handler("post-edit", "验证 Game Studio 写入")]}],
            "PreCompact": [{"matcher": "manual|auto", "hooks": [hook_handler("pre-compact", "记录压缩前状态")]}],
            "PostCompact": [{"matcher": "manual|auto", "hooks": [hook_handler("post-compact", "恢复压缩后提示")]}],
            "SubagentStart": [{"matcher": ".*", "hooks": [hook_handler("subagent-start", "注入子代理边界")]}],
            "SubagentStop": [{"matcher": ".*", "hooks": [hook_handler("subagent-stop", "结束子代理审计")]}],
            "Stop": [{"hooks": [hook_handler("stop", "结束 Game Studio 回合")]}],
        }
    }


def build_hooks() -> list[dict[str, str]]:
    write(ROOT / ".codex" / "hooks" / "game_studio_hook.py", HOOK_SCRIPT)
    hooks = hook_configuration()
    write(ROOT / ".codex" / "hooks.json", json.dumps(hooks, ensure_ascii=False, indent=2))
    return [
        {"source_hook": "detect-gaps.sh", "source_event": "SessionStart", "target_event": "SessionStart", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py session-start", "behavior_difference": "只提供缺口提示，不写状态文件。"},
        {"source_hook": "log-agent-stop.sh", "source_event": "SubagentStop", "target_event": "SubagentStop", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py subagent-stop", "behavior_difference": "不持久化会话日志，避免隐式仓库写入。"},
        {"source_hook": "log-agent.sh", "source_event": "SubagentStart", "target_event": "SubagentStart", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py subagent-start", "behavior_difference": "改为注入单层委派边界。"},
        {"source_hook": "notify.sh", "source_event": "Notification", "target_event": "none", "status": "unsupported", "target_script": "", "behavior_difference": "当前 Codex command Hook 事件列表无 Notification；不启用 Windows toast。"},
        {"source_hook": "post-compact.sh", "source_event": "PostCompact", "target_event": "PostCompact", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py post-compact", "behavior_difference": "输出恢复提示，不依赖 Claude 状态文件。"},
        {"source_hook": "pre-compact.sh", "source_event": "PreCompact", "target_event": "PreCompact", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py pre-compact", "behavior_difference": "只读汇总 git 状态，不写 production/session-state。"},
        {"source_hook": "session-start.sh", "source_event": "SessionStart", "target_event": "SessionStart", "status": "converted", "target_script": ".codex/hooks/game_studio_hook.py session-start", "behavior_difference": "使用 Codex additionalContext。"},
        {"source_hook": "session-stop.sh", "source_event": "Stop", "target_event": "Stop", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py stop", "behavior_difference": "返回合法空 JSON，不自动写会话日志。"},
        {"source_hook": "validate-assets.sh", "source_event": "PostToolUse", "target_event": "PostToolUse", "status": "converted", "target_script": ".codex/hooks/game_studio_hook.py post-edit", "behavior_difference": "Python 标准库验证变更 JSON。"},
        {"source_hook": "validate-commit.sh", "source_event": "PreToolUse", "target_event": "PreToolUse", "status": "converted", "target_script": ".codex/hooks/game_studio_hook.py pre-tool", "behavior_difference": "只在 git commit 时验证暂存 JSON。"},
        {"source_hook": "validate-push.sh", "source_event": "PreToolUse", "target_event": "PreToolUse", "status": "converted", "target_script": ".codex/hooks/game_studio_hook.py pre-tool", "behavior_difference": "使用 permissionDecision=deny 明确拒绝 push。"},
        {"source_hook": "validate-skill-change.sh", "source_event": "PostToolUse", "target_event": "PostToolUse", "status": "adapted", "target_script": ".codex/hooks/game_studio_hook.py post-edit", "behavior_difference": "校验 Codex SKILL.md frontmatter，不递归启动 Codex。"},
    ]


def build_config() -> None:
    config = f"""
[agents]
max_threads = 4
max_depth = 1

[features]
hooks = true

[mcp_servers.godot]
command = "npx"
args = ["-y", "@coding-solo/godot-mcp@{MCP_VERSION}"]
cwd = 'E:\\Workspace\\projects\\game\\project_004_godot_ai_demo'
startup_timeout_sec = 30
tool_timeout_sec = 120
enabled = false
required = false
default_tools_approval_mode = "writes"
"""
    write(ROOT / ".codex" / "config.toml", config)


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |\n"
    divider = "| " + " | ".join("---" for _ in columns) + " |\n"
    body = ""
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            values.append(str(value).replace("|", "\\|").replace("\n", " "))
        body += "| " + " | ".join(values) + " |\n"
    return header + divider + body


def build_docs(
    agent_mappings: list[dict[str, object]],
    skill_mappings: list[dict[str, object]],
    rule_mappings: list[dict[str, object]],
    hook_mappings: list[dict[str, str]],
) -> None:
    docs = ROOT / "docs" / "codex-migration"
    architecture = f"""
# 迁移架构

固定上游 `v1.0.0` / `{SOURCE_COMMIT}` / tree `{SOURCE_TREE}` 以未修改快照保存在 `upstream/`。`SOURCE-MANIFEST.json` 只能从经过 Git commit、tree、origin 和 clean 状态验证的源 checkout 生成，再与目标快照双向比对。活动适配层与快照分离：根 `AGENTS.md` 负责总则，`.codex/agents/` 承载 49 个独立 Agent，`.agents/skills/` 承载 73 个关闭隐式调用的下游 Skill 和唯一隐式 `game-studio-router`，路径规则落到最近层级 `AGENTS.md`，生命周期行为由 `.codex/hooks.json` 和 Python command Hook 实现。

状态词严格区分 `preserved`、`converted`、`adapted`、`deferred`、`unsupported`。Godot 与 MCP 运行验证为 `deferred_missing_godot`，不影响静态迁移验收。
"""
    write(docs / "architecture.md", architecture)
    compatibility = """
# 兼容性矩阵

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 上游源码与 Claude 配置 | preserved | 完整快照，逐文件 SHA-256 固定，不作为活动配置。 |
| Agents | converted | 独立 TOML；移除 Claude 模型/工具字段，继承 Codex 会话权限。 |
| Skills | converted | 73 个下游 Skill 保留完整工作流并关闭隐式调用；唯一隐式 `game-studio-router` 按索引定向选择。 |
| 路径 Rules | converted | 最近层级 `AGENTS.md`。 |
| Shell deny 规则 | adapted | `.codex/rules/game-studio-safety.rules` 与 PreToolUse 提供双层辅助护栏；不能替代任务边界、沙箱、审批和权限系统。 |
| Session/Tool/Compact/Subagent/Stop Hooks | adapted | 当前 Codex command Hook 事件；不做隐式状态日志写入。 |
| Notification Hook | unsupported | 当前稳定事件列表没有 Notification，Windows toast 未启用。 |
| Codex 运行发现 | deferred | WindowsApps CLI 执行受限；需新任务/重启后实测。 |
| Godot 与 MCP | deferred | 缺少 Godot；项目配置固定包版本且默认 disabled。 |
"""
    write(docs / "compatibility-matrix.md", compatibility)
    write(docs / "agents-mapping.md", "# Agents 映射\n\n" + markdown_table(agent_mappings, ["source_agent", "target_toml", "status", "claude_specific_fields_removed", "behavior_differences"]))
    write(docs / "skills-mapping.md", "# Skills 映射\n\n" + markdown_table(skill_mappings, ["source_skill", "target_skill", "status", "claude_specific_fields_removed", "behavior_differences"]))
    write(docs / "rules-mapping.md", "# Rules 映射\n\n" + markdown_table(rule_mappings, ["source_rule", "source_paths", "target_agents_md", "status", "behavior_differences"]) + "\nShell deny 配置另迁移为 `.codex/rules/game-studio-safety.rules`；共 1 个 command rules 文件。Rules 与 Hooks 都是辅助护栏，不能替代任务边界、Codex 沙箱、审批和权限系统。")
    write(docs / "hooks-mapping.md", "# Hooks 映射\n\n" + markdown_table(hook_mappings, ["source_hook", "source_event", "target_event", "status", "target_script", "behavior_difference"]) + "\n运行加载验证：`deferred_codex_cli`。")
    godot_mcp = f"""
# Godot MCP

- npm package: `@coding-solo/godot-mcp@{MCP_VERSION}`
- dist-tag `latest`: `{MCP_VERSION}`（迁移日查询）
- repository: `https://github.com/Coding-Solo/godot-mcp.git`
- license: MIT
- project config: `.codex/config.toml`

本机缺少 Godot，因此服务器配置固定版本但 `enabled = false`，没有写入 `GODOT_PATH`，也未进行 MCP 启动或工具调用。安装 Godot 4.x stable 后设置项目可见的 `GODOT_PATH`，再人工启用服务器并按运行清单验收。运行状态：`deferred_missing_godot`。
"""
    write(docs / "godot-mcp.md", godot_mcp)
    verification = """
# 静态验证

先以 `python tools/build_codex_adaptation.py --verified-source <checkout>` 从固定、clean 的上游 checkout 生成 `SOURCE-MANIFEST.json` 并双向验证快照。再运行 `python tools/verify_codex_migration.py`（Windows 也可使用可用的 Python 3.12 可执行文件）验证来源清单、固定数量、Router/Skill 结构、TOML/JSON、路径规则、Hooks、安全边界和跨项目引用。另运行 `python -m unittest tests/test_verify_codex_migration.py` 与 `git diff --check`。

Codex CLI、Hook 实际加载、Skill/Agent 实际发现、Godot 编辑器和 MCP 工具调用属于后续运行验收，不得从静态结果推断成功。
"""
    write(docs / "verification.md", verification)
    runtime = """
# 运行验收清单

- [ ] 安装并确认 Godot 4.x stable：`godot --version`。
- [ ] 设置不含凭据的 `GODOT_PATH`，在 `.codex/config.toml` 启用 Godot MCP。
- [ ] 启动 MCP server，确认固定包版本。
- [ ] 调用 get Godot version、list projects、project info。
- [ ] 调用 launch editor、run project、get debug output、stop project。
- [ ] 在新的 Codex App 任务中确认 73 个下游 Skill、`game-studio-router` 与 49 个自定义 Agent 可发现。
- [ ] 在受信任项目中审阅并信任 Hooks，逐项触发 SessionStart、PreToolUse、PostToolUse、Pre/PostCompact、SubagentStart/Stop、Stop。
- [ ] 确认 `notify.sh` 仍为 unsupported，未误报为已转换。
"""
    write(docs / "runtime-validation-checklist.md", runtime)
    manifest = {
        "upstream": {"repository": SOURCE_REPOSITORY, "tag": "v1.0.0", "commit": SOURCE_COMMIT},
        "agents": agent_mappings,
        "skills": skill_mappings,
        "router": {
            "name": "game-studio-router",
            "status": "adapted",
            "implicit_invocation": True,
            "downstream_skills": len(skill_mappings),
        },
        "rules": rule_mappings,
        "hooks": hook_mappings,
        "godot_mcp": {"package": "@coding-solo/godot-mcp", "version": MCP_VERSION, "enabled": False, "runtime": "deferred_missing_godot"},
    }
    write(docs / "migration-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Codex adaptation from a verified upstream checkout.")
    parser.add_argument(
        "--verified-source",
        type=pathlib.Path,
        required=True,
        help="Clean Git checkout at the pinned upstream commit used to generate SOURCE-MANIFEST.json.",
    )
    args = parser.parse_args(argv)
    if not SNAPSHOT.is_dir():
        raise SystemExit(f"missing snapshot: {SNAPSHOT}")
    source_skills = sorted(p.name for p in (SNAPSHOT / ".claude" / "skills").iterdir() if p.is_dir())
    source_agents = sorted(p.stem for p in (SNAPSHOT / ".claude" / "agents").glob("*.md"))
    build_source_manifest(args.verified_source)
    build_root_files(source_agents, source_skills)
    build_reference_docs(source_skills)
    agent_mappings = build_agents(source_skills)
    skill_mappings = build_skills(source_skills)
    rule_mappings = build_rules(source_skills)
    hook_mappings = build_hooks()
    build_config()
    build_docs(agent_mappings, skill_mappings, rule_mappings, hook_mappings)
    print(json.dumps({"agents": len(agent_mappings), "skills": len(skill_mappings), "rules": len(rule_mappings), "hooks": len(hook_mappings)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
