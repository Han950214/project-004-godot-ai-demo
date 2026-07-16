
# 运行验收清单

- [ ] 安装并确认 Godot 4.x stable：`godot --version`。
- [ ] 设置不含凭据的 `GODOT_PATH`，在 `.codex/config.toml` 启用 Godot MCP。
- [ ] 启动 MCP server，确认固定包版本。
- [ ] 调用 get Godot version、list projects、project info。
- [ ] 调用 launch editor、run project、get debug output、stop project。
- [ ] 在新的 Codex App 任务中确认 73 个下游 Skill、`game-studio-router` 与 49 个自定义 Agent 可发现。
- [ ] 在受信任项目中审阅并信任 Hooks，逐项触发 SessionStart、PreToolUse、PostToolUse、Pre/PostCompact、SubagentStart/Stop、Stop。
- [ ] 确认 `notify.sh` 仍为 unsupported，未误报为已转换。
