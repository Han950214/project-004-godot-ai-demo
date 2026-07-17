
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

Codex CLI、Hook 实际加载、Skill/Agent 实际发现和 Godot MCP 工具调用均须独立运行验收；不得从静态配置或 Godot CLI 结果推断 MCP 已被当前会话加载。

## Phase 2B 实时 MCP 验证

2026-07-17 的当前 Codex 会话已完成 Godot MCP 七项工具的独立实际调用。`get_debug_output` 提供本轮运行实例的 `CODEX_GODOT_RUNTIME_START`、`CODEX_GODOT_RUNTIME_READY` 和空错误列表；随后 `stop_project` 仅停止该实例。详见 `docs/runtime-evidence/godot-mcp-live-validation.md`。该结果不替代后续 Phase 2C 的 Skills、Agents 和 Hooks 实时发现验收。

## Phase 2C Skills、Agents 与 Hooks 验证

2026-07-17 当前会话已观察到 `game-studio-router` 加载，完成三次自然语言路由、五个代表性 Skill 工作流与三个代表性 Agent 只读调用。静态验证器确认 73 个下游 Skill、1 个 Router、49 个 Agent 和八个 Hook 目标事件的完整性。QA 代表调用发现组合、包装与命令替换中的危险 Git 子命令可绕过首个 Git 操作检查，已补回归测试、同步生成器模板并最小修复。2026-07-18 续验又确认 Windows PATH 无 `python` 时原 Hook 启动命令必然失败；现已加入现有解释器回退并以真实配置命令直接调用验证，但该结果不冒充 Codex 生命周期事件。

当前任务中，用户已确认 Windows 启动修复后的 Hook 配置哈希受信任，Hooks 已启用。安全 Git 与 `qa-lead` 只读探针均未暴露可归因的生命周期回执；实际 shell、写入与子代理调用不能在当前表面证明对应 Hook 已运行。处理器模拟、单元测试和配置命令直接调用不得替代事件触发证据。满足配置、信任、安全与回归门禁后，Phase 2C 以 `passed_with_surface_limitations` 收敛。完整证据见 `docs/runtime-evidence/codex-skills-agents-hooks-live-validation.md`。
