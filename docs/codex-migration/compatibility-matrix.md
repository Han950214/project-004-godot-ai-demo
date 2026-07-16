
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
