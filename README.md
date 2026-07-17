
# Codex Game Studio

Windows 运行验证使用项目级 `sandbox_mode = "workspace-write"`，唯一额外可写根为 `E:\Workspace\tools\Godot\4.7.1\editor_data`。该边界仅支持 Godot 4.7.1 自包含编辑器保存设置与缓存，不启用网络访问，也不授予整个 Godot 安装目录写权限。Godot console 的版本、`--import` 和 headless Demo 运行已在此边界下通过；Phase 2B MCP Live Validation 也已通过七项受限 MCP 工具的实际调用。

这是基于 Claude Code Game Studios v1.0.0 的非官方 Codex 适配项目。固定上游 commit 为 `984023ddac0d5e27624f2baacde6105e45de375f`，完整未修改快照位于 `upstream/claude-code-game-studios-v1.0.0/`。

Codex 适配层位于 `AGENTS.md`、`.agents/skills/`、`.codex/agents/`、`.codex/hooks.json`、`.codex/rules/` 和 `.codex/config.toml`。静态迁移、Godot 4.7.1 Stable 便携部署、CLI、项目解析、headless Demo 运行以及 Phase 2B Godot MCP 实时验收均已完成。Phase 2C 已完成 Router、五个代表性 Skill 与三个代表性 Agent 的只读调用；当前项目 Hook 已由用户确认信任且启用，但 Desktop 表面不暴露生命周期事件回执，因此阶段结论为 `passed_with_surface_limitations`，不宣称所有 73 个 Skill、49 个 Agent 或全部 Hook 已逐项运行。

当前统计：49 个自定义 Agent、73 个下游 Skill、1 个自动路由 Skill、11 个路径级规则映射。首次使用前请在 Codex 中信任项目级配置与 Hooks；用户可自然描述游戏开发任务交给 `game-studio-router`，也可显式调用 `$start`、`$help`、`$project-stage-detect` 或其他下游 Skill。

最小运行验收项目位于 `demo/`。使用 `python tools/verify_godot_runtime.py` 验证固定 Godot 路径、Demo、headless 日志、MCP 0.1.1 配置和七工具白名单；完整步骤与当前延期项见 `docs/codex-migration/runtime-validation-checklist.md`。

## Phase 2B 实时 MCP 验收

2026-07-17 已在当前 Codex 会话通过 Godot MCP 实际调用全部七项受限工具，并完成编辑器启动、Demo 运行、调试输出读取及仅停止本轮运行实例。新鲜输出含 `CODEX_GODOT_RUNTIME_START` 与 `CODEX_GODOT_RUNTIME_READY`，错误列表为空。详见 `docs/runtime-evidence/godot-mcp-live-validation.md`；不会把此前 CLI 日志当作 MCP 验收证据。

## Phase 2C 运行发现验收

2026-07-17 至 2026-07-18 已证明 `game-studio-router` 在当前会话加载，完成三次自然语言路由、五个下游 Skill 工作流和三个项目 Agent 的代表性只读调用，并以静态验证器确认 73 个下游 Skill、1 个 Router 与 49 个 Agent 的完整性。QA 调用发现并修复了组合 Git 命令绕过 Hook 检查的问题；续验又修复了 Windows PATH 无 `python` 时 Hook 无法启动的问题，配置命令直接调用已通过。当前任务中，用户确认已信任当前 Hook 哈希；安全 Git 与 `qa-lead` 只读探针未产生可观察的生命周期回执，详见 `docs/runtime-evidence/codex-skills-agents-hooks-live-validation.md`。
