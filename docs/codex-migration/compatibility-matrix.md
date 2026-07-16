
# 兼容性矩阵

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 上游源码与 Claude 配置 | preserved | 完整快照，逐文件 SHA-256 固定，不作为活动配置。 |
| Agents | converted | 独立 TOML；移除 Claude 模型/工具字段，继承 Codex 会话权限。 |
| Skills | converted | Codex frontmatter、UI 元数据和隐式调用策略；完整工作流保留并适配。 |
| 路径 Rules | converted | 最近层级 `AGENTS.md`。 |
| Shell deny 规则 | adapted | `.codex/rules/game-studio-safety.rules` 与 PreToolUse 双层防护。 |
| Session/Tool/Compact/Subagent/Stop Hooks | adapted | 当前 Codex command Hook 事件；不做隐式状态日志写入。 |
| Notification Hook | unsupported | 当前稳定事件列表没有 Notification，Windows toast 未启用。 |
| Codex 运行发现 | deferred | WindowsApps CLI 执行受限；需新任务/重启后实测。 |
| Godot 与 MCP | deferred | 缺少 Godot；项目配置固定包版本且默认 disabled。 |
