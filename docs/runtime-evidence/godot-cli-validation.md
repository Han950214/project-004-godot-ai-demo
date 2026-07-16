# Godot CLI 运行验收

验证日期：2026-07-16（Asia/Shanghai）

## 当前可执行文件确认的参数

从 Godot 4.7.1 的 `--help` 实际输出确认本阶段使用：

- `--editor`：以编辑器模式启动。
- `--headless`：使用 headless 显示与 dummy 音频驱动。
- `--path <directory>`：指定包含 `project.godot` 的项目目录。
- `--quit`：首轮迭代后退出。
- `--quit-after <int>`：指定迭代次数后退出。

## 验证结果

| 验证项 | 状态 | 证据 |
| --- | --- | --- |
| 主程序版本 | passed | `4.7.1.stable.official.a13da4feb` |
| Console 版本 | passed | `4.7.1.stable.official.a13da4feb` |
| 项目识别 | passed | `demo/project.godot` |
| 编辑器 headless 导入/解析 | passed | 退出码 `0` |
| 主场景 headless 运行 | passed | 退出码 `0` |
| 启动标记 | passed | `CODEX_GODOT_RUNTIME_START` |
| 就绪标记 | passed | `CODEX_GODOT_RUNTIME_READY` |
| parser/script/missing resource 错误 | passed | 未发现 |
| 受控退出 | passed | GDScript 在 headless 验证完成后主动退出，CLI 另有超时保护 |

可复用入口为 `python tools/verify_godot_runtime.py`。Godot MCP 配置已解析并通过静态验证，但当前 Codex 会话没有重新加载项目级 MCP，七项实际 MCP 调用均为 `deferred_restart_required`，不是 `passed`。
