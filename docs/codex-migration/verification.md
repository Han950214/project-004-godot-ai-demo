
# 静态验证

先以 `python tools/build_codex_adaptation.py --verified-source <checkout>` 从固定、clean 的上游 checkout 生成 `SOURCE-MANIFEST.json` 并双向验证快照。再运行 `python tools/verify_codex_migration.py`（Windows 也可使用可用的 Python 3.12 可执行文件）验证来源清单、固定数量、Router/Skill 结构、TOML/JSON、路径规则、Hooks、安全边界、跨项目引用，以及 Godot MCP 固定版本、固定路径和精确工具白名单。

Godot 运行验收使用：

```powershell
python -m unittest tests/test_verify_codex_migration.py
python -m unittest tests/test_verify_godot_runtime.py
python tools/verify_codex_migration.py
python tools/verify_godot_runtime.py
git diff --check
```

`verify_godot_runtime.py` 只使用 Python 标准库，验证便携程序与 `_sc_` 标记、版本、Demo 引用、headless 导入和运行、成功日志、Godot 错误输出、MCP 配置，以及 Git 未跟踪 Godot ZIP/EXE。超时只终止验证器直接启动的 Godot 主进程。

Codex CLI、Hook 实际加载、Skill/Agent 实际发现和 Godot MCP 工具调用仍需独立运行验收；不得从静态配置或 Godot CLI 结果推断 MCP 已被当前会话加载。
