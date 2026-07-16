
# 静态验证

运行 `python tools/verify_codex_migration.py`（Windows 也可使用可用的 Python 3.12 可执行文件）验证快照哈希、Agent/Skill 数量与结构、TOML/JSON、路径规则、Hooks、安全边界和跨项目引用。另运行 `python -m unittest tests/test_verify_codex_migration.py` 与 `git diff --check`。

Codex CLI、Hook 实际加载、Skill/Agent 实际发现、Godot 编辑器和 MCP 工具调用属于后续运行验收，不得从静态结果推断成功。
