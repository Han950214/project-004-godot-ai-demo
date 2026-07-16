
# Godot MCP

- npm package: `@coding-solo/godot-mcp@0.1.1`
- dist-tag `latest`: `0.1.1`（迁移日查询）
- repository: `https://github.com/Coding-Solo/godot-mcp.git`
- license: MIT
- project config: `.codex/config.toml`

Godot 4.7.1 Stable x86_64 标准版已作为自包含便携程序部署到 `E:\Workspace\tools\Godot\4.7.1`。项目配置现为 `enabled = true`、`required = false`、`default_tools_approval_mode = "writes"`，并设置固定 `GODOT_PATH`。

工具白名单精确限制为：

- `get_godot_version`
- `list_projects`
- `get_project_info`
- `launch_editor`
- `run_project`
- `get_debug_output`
- `stop_project`

场景创建和资源写入工具没有启用。本任务的 Codex 进程启动时 MCP 尚为关闭状态，因此当前会话没有重新加载新增工具；配置、CLI 和 headless Demo 已验证，实际 MCP 工具调用状态为 `deferred_restart_required`，留待 Phase 2B。
