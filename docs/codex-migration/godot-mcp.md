
# Godot MCP

- npm package: `@coding-solo/godot-mcp@0.1.1`
- dist-tag `latest`: `0.1.1`（迁移日查询）
- repository: `https://github.com/Coding-Solo/godot-mcp.git`
- license: MIT
- project config: `.codex/config.toml`

本机缺少 Godot，因此服务器配置固定版本但 `enabled = false`，没有写入 `GODOT_PATH`，也未进行 MCP 启动或工具调用。安装 Godot 4.x stable 后设置项目可见的 `GODOT_PATH`，再人工启用服务器并按运行清单验收。运行状态：`deferred_missing_godot`。
