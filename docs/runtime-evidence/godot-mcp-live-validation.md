# Godot MCP 实时验收证据

日期：2026-07-17
阶段：Phase 2B — Codex Godot MCP Live Validation
仓库：`E:\Workspace\projects\game\project_004_godot_ai_demo`

## 会话与权限边界

- Godot MCP server 已在当前 Codex 会话中加载；七项受限工具均可调用。
- 固定包：`@coding-solo/godot-mcp@0.1.1`。
- 工具白名单未变更：`get_godot_version`、`list_projects`、`get_project_info`、`launch_editor`、`run_project`、`get_debug_output`、`stop_project`。
- 未修改 `.codex/config.toml`；额外可写根仍仅为 `E:\Workspace\tools\Godot\4.7.1\editor_data`，未启用网络访问。

## 实际 MCP 调用

| 顺序 | 工具 | 实际结果 |
| --- | --- | --- |
| 1 | `get_godot_version` | 返回 `4.7.1.stable.official.a13da4feb`。 |
| 2 | `list_projects` | 在当前仓库范围发现 `E:\Workspace\projects\game\project_004_godot_ai_demo\demo`，其项目文件为 `demo\project.godot`。 |
| 3 | `get_project_info` | 成功返回 Demo 路径、Godot `4.7.1.stable.official.a13da4feb` 与项目结构。该 MCP 版本将显示名返回为目录名 `demo`；`demo\project.godot` 的实际声明确认 `config/name="Codex Godot Runtime Validation"` 和 `run/main_scene="res://scenes/main.tscn"`。 |
| 4 | `launch_editor` | 仅为当前 `demo` 启动 Godot 编辑器，成功。 |
| 5 | `run_project` | 当前 Demo 已在 debug mode 启动。 |
| 6 | `get_debug_output` | 本轮 MCP 输出包含 `CODEX_GODOT_RUNTIME_START` 与 `CODEX_GODOT_RUNTIME_READY`；`errors` 为 `[]`，未发现脚本、解析或资源加载错误。 |
| 7 | `stop_project` | MCP 报告 `Godot project stopped`，并返回同一运行实例的最终输出和空错误列表；未使用全局进程终止，编辑器保持打开。 |

## 结论

Phase 2B 的实时 Godot MCP 调用链已完成。此证据来自本轮 MCP 工具输出，不以既有 CLI 日志替代。
