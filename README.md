
# Codex Game Studio

这是基于 Claude Code Game Studios v1.0.0 的非官方 Codex 适配项目。固定上游 commit 为 `984023ddac0d5e27624f2baacde6105e45de375f`，完整未修改快照位于 `upstream/claude-code-game-studios-v1.0.0/`。

Codex 适配层位于 `AGENTS.md`、`.agents/skills/`、`.codex/agents/`、`.codex/hooks.json`、`.codex/rules/` 和 `.codex/config.toml`。静态迁移与 Godot 4.7.1 Stable 便携部署、CLI、项目解析及 headless Demo 运行验收已经完成；当前任务尚未重新加载新启用的项目级 Godot MCP，因此七项 MCP 实际工具调用留待重启后的 Phase 2B，不宣称所有 Claude Hook 与 Codex 完全等价。

当前统计：49 个自定义 Agent、73 个下游 Skill、1 个自动路由 Skill、11 个路径级规则映射。首次使用前请在 Codex 中信任项目级配置与 Hooks；用户可自然描述游戏开发任务交给 `game-studio-router`，也可显式调用 `$start`、`$help`、`$project-stage-detect` 或其他下游 Skill。

最小运行验收项目位于 `demo/`。使用 `python tools/verify_godot_runtime.py` 验证固定 Godot 路径、Demo、headless 日志、MCP 0.1.1 配置和七工具白名单；完整步骤与当前延期项见 `docs/codex-migration/runtime-validation-checklist.md`。
