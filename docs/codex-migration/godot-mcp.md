
# Godot MCP

## Windows 沙箱边界

项目级 `.codex/config.toml` 固定使用 `sandbox_mode = "workspace-write"`，并仅将 `E:\Workspace\tools\Godot\4.7.1\editor_data` 加入 `writable_roots`。未启用 `network_access`，未扩大到整个 Godot 安装目录、工作区或其他仓库。该权限只解决 `_sc_` 自包含模式保存编辑器设置、缓存和 `user://` 数据所需的写入；MCP 包版本、GUI `GODOT_PATH` 和七项工具白名单保持不变。

配置与 console 运行验证已经通过，但当前会话没有重新加载 MCP。`Phase 2B=blocked_pending_restart`，不得从静态配置或 CLI 成功推断七项 MCP 工具已经可调用。

- npm package: `@coding-solo/godot-mcp@0.1.1`
- dist-tag `latest`: `0.1.1`（迁移日查询）
- repository: `https://github.com/Coding-Solo/godot-mcp.git`
- license: MIT
- project config: `.codex/config.toml`

Godot 4.7.1 Stable x86_64 标准版已作为自包含便携程序部署到 `E:\Workspace\tools\Godot\4.7.1`。项目配置现为 `enabled = true`、`required = false`、`default_tools_approval_mode = "writes"`，并设置固定 `GODOT_PATH`。

Windows 上 `command = "npx"` 可能解析为受 PowerShell Execution Policy 限制的 `npx.ps1`。本项目改用固定 `E:\Program Files\nodejs\npx.cmd` 启动 MCP，未修改 PowerShell Execution Policy。

MCP 的 `GODOT_PATH` 继续指向 GUI 主程序，供后续 `launch_editor` 使用。Windows CLI/headless 自动验证改用同版本的 `Godot_v4.7.1-stable_win64_console.exe`，资源导入使用官方 `--import`，不再使用 `--editor --quit-after 2`。受控 GUI 对照本次通过，但此前的 `0xC0000005` 访问冲突不能据此宣称已修复；完整矩阵见 `docs/runtime-evidence/crash-isolation/README.md`。

工具白名单精确限制为：

- `get_godot_version`
- `list_projects`
- `get_project_info`
- `launch_editor`
- `run_project`
- `get_debug_output`
- `stop_project`

场景创建和资源写入工具没有启用。当前会话不能从静态配置推断 MCP 已加载；实际 MCP 工具调用仍为 `Phase 2B=blocked_pending_restart`，需在 MCP 重载或新 Codex 任务中验收。
