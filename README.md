
# Codex Game Studio

这是基于 Claude Code Game Studios v1.0.0 的非官方 Codex 适配项目。固定上游 commit 为 `984023ddac0d5e27624f2baacde6105e45de375f`，完整未修改快照位于 `upstream/claude-code-game-studios-v1.0.0/`。

Codex 适配层位于 `AGENTS.md`、`.agents/skills/`、`.codex/agents/`、`.codex/hooks.json`、`.codex/rules/` 和 `.codex/config.toml`。本阶段已完成静态迁移；Godot 与 Godot MCP 实机验证因本机缺少 Godot 而延后，不宣称所有 Claude Hook 与 Codex 完全等价。

当前统计：49 个自定义 Agent、73 个 Skill、11 个路径级规则映射。首次使用前请在 Codex 中信任项目级配置与 Hooks；需要工作流时可显式调用 `$start`、`$help`、`$project-stage-detect` 或其他 Skill。

后续安装 Godot 4.x stable 后，按 `docs/codex-migration/runtime-validation-checklist.md` 完成独立运行验收。
