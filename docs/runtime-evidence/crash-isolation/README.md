# Godot Windows headless crash isolation

## 后续沙箱修复结果

项目级 `.codex/config.toml` 现仅允许 `E:\Workspace\tools\Godot\4.7.1\editor_data` 写入。审批后执行 `tools/verify_godot_runtime.py`：console 版本检查、官方 `--import` 和 headless runtime 均退出 0，两个确定性运行标记存在，输出无 Godot `ERROR`。下列四份小型日志保留为修复前的根因证据；它们已通过敏感信息扫描，不代表本次通过运行。

验证日期：2026-07-17（Asia/Shanghai）

## 边界与结论

- Windows MCP launcher 修复保持为 `E:\Program Files\nodejs\npx.cmd`，包版本仍为 `@coding-solo/godot-mcp@0.1.1`。
- MCP `GODOT_PATH` 仍指向 GUI EXE；CLI/headless 自动验证改用 console EXE。
- 官方资源导入入口为 `--import`，已停止使用 `--editor --quit-after 2`。
- 先前 GUI headless 运行曾返回 `3221225477` / `0xC0000005`，并出现“内存不能为 read”对话框。本次受控 GUI 对照未复现，因此不能宣称 Godot 引擎访问冲突已修复。
- Phase 2B 尚未执行；当前会话未重载 MCP。

## 二进制证据

| 项目 | 结果 |
| --- | --- |
| ZIP SHA-256（既有安装证据） | `c7a289051eaefb460b0106b60e9cd5bee0ef55fd102dcb2bed1eb356cf3d90a1` |
| GUI EXE SHA-256 | `323f9c4cc5db674e98815cdd8e69da007d5efc779abedc8c0e42883b7fdea12a` |
| Console EXE SHA-256 | `35dab11e04ece16a2b93035e65204f4a944a3e00b020d43e54409193379d5eef` |
| GUI Authenticode（当前沙箱） | `UnknownError: A certificate chain could not be built to a trusted root authority` |
| Console Authenticode（当前沙箱） | `UnknownError: A certificate chain could not be built to a trusted root authority` |
| 既有安装证据中的 Authenticode | `Valid`；见 `docs/runtime-evidence/godot-installation.md` |
| Self-contained 标记 | `_sc_` 存在；`._sc_` 不存在 |

`c7a...` 是 Release ZIP 哈希，不是解压后 GUI EXE 哈希。

## 原生命令矩阵

| 二进制与命令 | PID | 十进制退出码 | 十六进制退出码 | 结果 |
| --- | ---: | ---: | --- | --- |
| console `--version` | 37112 | 0 | `0x00000000` | `4.7.1.stable.official.a13da4feb` |
| console `--help` | 7712 | 0 | `0x00000000` | 确认 `--headless`、`--path`、`--import`、`--verbose`、`--log-file` |
| console `--headless --path <demo> --import --verbose --log-file ...` | 16940 | 0 | `0x00000000` | 命令完成；日志包含受限写入错误 |
| console `--headless --path <demo> --import --verbose` | 7836 | 0 | `0x00000000` | 与验证器一致；stderr 捕获到 3 条 `ERROR`，验证必须失败 |
| console `--headless --path <demo> --quit-after 300 --verbose --log-file ...` | 22736 | 0 | `0x00000000` | 两个 runtime 标记均存在，无脚本、解析或资源加载错误 |
| GUI `--headless --path <demo> --import --verbose --log-file ...` | 39548 | 0 | `0x00000000` | 本次通过；日志包含受限写入错误 |
| GUI `--headless --path <demo> --quit-after 300 --verbose --log-file ...` | 39200 | 0 | `0x00000000` | 本次通过；两个 runtime 标记均存在 |

`console-import.log` 与 `gui-import.log` 中的错误来自修复前的 self-contained 模式写入限制。该失败建立了可复现信号，并推动配置收敛为唯一精确 `editor_data` 可写根；未修改 ACL、PATH、注册表或 PowerShell Execution Policy，也未关闭沙箱。验证器继续把任何 Godot `ERROR` 作为硬失败，不通过忽略错误来获得成功结果。

修复前使用 Codex 附带 Python 执行 `tools/verify_godot_runtime.py` 的结果为退出码 1：`Godot import output contains errors: ['^ERROR:']`。修复后在获批的精确边界内重跑为退出码 0，且 import 与 runtime 均通过。

最近 30 分钟的 Application 事件日志查询没有匹配 Godot 的 ID 1000/1001 记录，故 `faulting_module` 与 `fault_offset` 无可用事件证据。
