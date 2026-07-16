
# 运行验收清单

- [x] 部署并确认 Godot 4.7.1 Stable x86_64 标准版：主程序与 console 程序的 `--version` 均返回 `4.7.1.stable.official.a13da4feb`。
- [x] 校验官方 Release ZIP 的 SHA-256 与主程序 Authenticode 签名，并启用 `_sc_` 自包含模式。
- [x] 完成 `demo/` 项目识别、编辑器解析、headless 主场景运行和确定性日志验证。
- [x] 设置不含凭据的固定 `GODOT_PATH`，在 `.codex/config.toml` 启用固定版本 Godot MCP。
- [x] 将 MCP 白名单限制为七个读取、启动、调试和停止工具；未启用场景或资源写入工具。
- [ ] 重启或新建 Codex 任务，确认 MCP server 以固定包版本启动。当前状态：`deferred_restart_required`。
- [ ] 调用 get Godot version、list projects、project info。当前状态：`deferred_restart_required`。
- [ ] 调用 launch editor、run project、get debug output、stop project。当前状态：`deferred_restart_required`。
- [ ] 在新的 Codex App 任务中确认 73 个下游 Skill、`game-studio-router` 与 49 个自定义 Agent 可发现。
- [ ] 在受信任项目中审阅并信任 Hooks，逐项触发 SessionStart、PreToolUse、PostToolUse、Pre/PostCompact、SubagentStart/Stop、Stop。
- [ ] 确认 `notify.sh` 仍为 unsupported，未误报为已转换。
