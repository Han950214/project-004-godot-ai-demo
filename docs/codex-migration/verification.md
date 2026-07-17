
# 静态验证

两个验证器都要求项目配置精确使用 `sandbox_mode = "workspace-write"`，且 `writable_roots` 只能包含 `E:\Workspace\tools\Godot\4.7.1\editor_data`。缺失该根、放宽到 Godot 安装目录、增加第二个根、使用 `danger-full-access` 或启用 `network_access = true` 都会失败。该检查与固定 `npx.cmd`、MCP 0.1.1、GUI `GODOT_PATH` 和七项工具白名单同时执行，不能相互替代。

先以 `python tools/build_codex_adaptation.py --verified-source <checkout>` 从固定、clean 的上游 checkout 生成 `SOURCE-MANIFEST.json` 并双向验证快照。再运行 `python tools/verify_codex_migration.py`（Windows 也可使用可用的 Python 3.12 可执行文件）验证来源清单、固定数量、Router/Skill 结构、TOML/JSON、路径规则、Hooks、安全边界、跨项目引用，以及 Godot MCP 固定版本、固定路径和精确工具白名单。

Godot 运行验收使用：

```powershell
python -m unittest tests/test_verify_codex_migration.py
python -m unittest tests/test_verify_godot_runtime.py
python tools/verify_codex_migration.py
python tools/verify_godot_runtime.py
git diff --check
```

`verify_godot_runtime.py` 只使用 Python 标准库，分别验证 GUI 与 console 二进制、`_sc_` 标记、版本、Demo 引用、headless 导入和运行、成功日志、Godot 错误输出、MCP 配置，以及 Git 未跟踪 Godot ZIP/EXE。MCP `GODOT_PATH` 必须保持 GUI EXE；CLI/headless 默认入口必须为 console EXE。导入命令固定为 `--headless --path <demo> --import --verbose`，运行命令固定为 `--headless --path <demo> --quit-after 300 --verbose`。非零退出码同时报告十进制值和 32 位十六进制值，import 失败或出现 Godot 错误时不会继续运行项目。

MCP 配置必须使用固定 `E:\Program Files\nodejs\npx.cmd`，且拒绝 `npx`、`npx.ps1`、PowerShell 启动器和 ExecutionPolicy/Bypass 参数。超时只终止验证器直接启动的 Godot 主进程。FakeRunner 单元测试只验证命令和判定逻辑，不代替真实 Godot 原生命令矩阵。

Codex CLI、Hook 实际加载、Skill/Agent 实际发现和 Godot MCP 工具调用仍需独立运行验收；不得从静态配置或 Godot CLI 结果推断 MCP 已被当前会话加载。
