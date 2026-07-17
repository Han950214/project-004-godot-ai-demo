
# 运行验收清单

- [x] 部署并确认 Godot 4.7.1 Stable x86_64 标准版：主程序与 console 程序的 `--version` 均返回 `4.7.1.stable.official.a13da4feb`。
- [x] 校验官方 Release ZIP 的 SHA-256 与主程序 Authenticode 签名，并启用 `_sc_` 自包含模式。
- [x] 完成 `demo/` 项目识别、编辑器解析、headless 主场景运行和确定性日志验证。
- [x] 设置不含凭据的固定 `GODOT_PATH`，在 `.codex/config.toml` 启用固定版本 Godot MCP。
- [x] 将 MCP 白名单限制为七个读取、启动、调试和停止工具；未启用场景或资源写入工具。
- [x] Windows MCP 启动命令固定为 `E:\Program Files\nodejs\npx.cmd`，以避免 `command = "npx"` 解析为 `npx.ps1`；未修改 PowerShell Execution Policy。
- [x] console EXE 的 `--version`、官方 `--import` 和 headless runtime 命令均退出 0；runtime 日志包含两个确定性标记。
- [x] 自动验证器改用 console EXE，导入入口改为 `--import`，并保留非零退出码、Godot 错误和缺失标记的硬失败门禁。
- [x] 项目级沙箱仅允许 self-contained `editor_data/` 写入；console `--version`、`--import` 与 headless runtime 均退出 0，两个运行标记存在且输出无 Godot `ERROR`。
- [x] 当前 Codex 任务已实际加载固定包版本 Godot MCP；七项受限工具均可调用。证据：`docs/runtime-evidence/godot-mcp-live-validation.md`。
- [x] 已实际调用 get Godot version、list projects、project info；版本为 `4.7.1.stable.official.a13da4feb`，发现 `demo/project.godot`，并核对项目声明名称与主场景。
- [x] 已实际调用 launch editor、run project、get debug output、stop project；本轮 MCP 输出含两个运行标记且无错误，停止动作仅作用于本轮运行实例。
- [ ] 在新的 Codex App 任务中确认 73 个下游 Skill、`game-studio-router` 与 49 个自定义 Agent 可发现。
- [ ] 在受信任项目中审阅并信任 Hooks，逐项触发 SessionStart、PreToolUse、PostToolUse、Pre/PostCompact、SubagentStart/Stop、Stop。
- [ ] 确认 `notify.sh` 仍为 unsupported，未误报为已转换。
