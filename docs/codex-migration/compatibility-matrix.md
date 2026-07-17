
# 兼容性矩阵

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 上游源码与 Claude 配置 | preserved | 完整快照，逐文件 SHA-256 固定，不作为活动配置。 |
| Agents | runtime_sampled | 49 个 TOML 静态完整性通过；`godot-specialist`、`qa-lead`、`producer` 三个代表性 Agent 已完成只读调用。 |
| Skills | runtime_sampled | 73 个下游 Skill 与唯一隐式 `game-studio-router` 静态完整性通过；Router 三次路由与五个代表性 Skill 工作流已实际执行。 |
| 路径 Rules | converted | 最近层级 `AGENTS.md`。 |
| Shell deny 规则 | adapted | `.codex/rules/game-studio-safety.rules` 与 PreToolUse 提供双层辅助护栏；不能替代任务边界、沙箱、审批和权限系统。 |
| Session/Tool/Compact/Subagent/Stop Hooks | passed_with_surface_limitations | 用户已确认当前配置哈希受信任，且 Hooks 已启用、配置可解析；安全 Git 与 `qa-lead` 探针未暴露生命周期回执。处理器模拟与配置命令直接调用不计为事件触发。 |
| Notification Hook | unsupported | 当前稳定事件列表没有 Notification，Windows toast 未启用。 |
| Codex 运行发现 | partial | Router、五个代表性 Skill 与三个代表性 Agent 已验收；没有全量运行时 Skill/Agent 列表接口，完整数量来自静态验证。 |
| Godot 与 MCP | passed | Godot 4.7.1 CLI/headless 与当前会话七项 MCP 工具均已真实验收。 |
