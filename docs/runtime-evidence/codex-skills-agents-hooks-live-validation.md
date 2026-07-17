# Codex Skills、Agents、Router 与 Hooks 实时验收

日期：2026-07-17 至 2026-07-18

## 结论

Phase 2C 最终结论为 `passed_with_surface_limitations`。Skill、Router、Agent 的静态完整性与代表性只读调用均通过；用户已确认当前 Hook 配置哈希受信任，Hook 配置、处理器模拟和 Windows 配置命令直接调用验证通过。当前 Codex Desktop 表面不提供可观察的生命周期事件回执，因此不得把处理器单元测试、直接脚本调用、配置命令调用或配置存在性写成 Hook 运行时触发成功。

## 基线

- 仓库：`E:\Workspace\projects\game\project_004_godot_ai_demo`
- 分支：`main`
- 基线 HEAD：`d5ad4b691bb0a696e992ab3890ac0e46ebd495c6`
- 标题：`docs: close Godot MCP live validation`
- 初始工作树：按 Phase 2C 预期为 dirty；索引：clean
- 本地 `origin/main`：与基线 HEAD 相同
- 未执行 fetch、push、reset、clean、rebase 或 amend

## 运行时真实发现

- 当前会话的 Skill 注册上下文明确列出项目级 `game-studio-router`，证明 Router 已加载。
- 当前表面没有提供“列出全部项目 Skill”的独立运行时接口；73 个下游 Skill 的完整数量由静态验证器证明，不冒充逐项运行时发现。
- 当前子代理接口提供项目角色调用能力；实际调用了 `godot-specialist`、`qa-lead`、`producer` 三个职责不同的 Agent。

## Router 自然语言路由

| 任务 | Router 选择 | 合理性 | 结果摘要 |
| --- | --- | --- | --- |
| A：判断当前 Godot 项目处于哪个开发阶段 | `project-stage-detect` | yes | 当前仓库处于 Phase 2C 迁移运行验收，不是实际游戏产品制作阶段。 |
| B：给出接下来最合适的一个小型开发目标 | `help` | yes | 先关闭 Phase 2C 运行证据缺口；通过后才建议 Phase 3A。 |
| C：检查 Demo 的 Godot 结构或运行风险 | `code-review` | yes | Demo 资源链、节点路径和确定性日志标记完整；未发现阻断性结构风险。 |

三次任务均先由 `game-studio-router` 按索引定向选择，没有路由到无关平台、营销、音频或发行流程。

## 代表性下游 Skill 调用

当前表面没有单独的 Skill RPC；代表性调用采用“由 Router 或显式名称加载对应 `SKILL.md`，随后执行其只读工作流”的方式。静态目录存在性不计为调用。

| Skill | 触发方式 | 结果 |
| --- | --- | --- |
| `project-stage-detect` | Router 选择后显式执行 | 识别为 Phase 2C 迁移验收；未写阶段报告。 |
| `help` | Router 选择后显式执行 | 给出完成 Phase 2C 作为唯一下一目标；未自动进入下一阶段。 |
| `start` | 显式执行 | 识别为既有适配项目；只读返回阶段检测/接管建议，没有写 `production/`。 |
| `setup-engine` | 显式执行 | 确认 Demo 使用固定 Godot 4.7.1/GDScript；同时指出 Game Studio 模板技术偏好仍未配置，未做配置写入。 |
| `code-review` | Router 选择后显式执行 | Demo 结构无阻断问题；版本 UI 文本不能替代运行日志，技术偏好缺口为后续治理风险。 |

代表性调用数量为 5，全部只读，未修改 Demo 或启动大规模实现。

## 静态完整性证据

`python tools/verify_codex_migration.py` 的等效现有 Python 运行结果：

- 73 个下游 Skill
- 1 个 `game-studio-router`
- 74 个项目 Skill 目录均具有 `SKILL.md` 与 `agents/openai.yaml`
- 只有 `game-studio-router` 允许 implicit invocation
- Router 索引精确覆盖 73 个下游 Skill
- 49 个 `.codex/agents/*.toml` 可解析，名称唯一，`description` 与 `developer_instructions` 非空
- 12 个上游 Hook 映射存在，8 个目标事件集合完整

## 代表性 Agent 调用

| Agent | 只读任务 | 结果 |
| --- | --- | --- |
| `godot-specialist` | 检查最小 Demo 结构与 Godot 4.7.1 风险 | passed；资源链完整，无阻断性运行结构问题。 |
| `qa-lead` | 审阅验证器与安全覆盖 | passed with concerns；发现组合 Git 命令可绕过首个 Git 调用检查。 |
| `producer` | 审阅 Phase 2C 前置文档与更新范围 | passed；识别需更新的七份迁移文档及证据边界。 |

三个 Agent 都完成单一小型只读任务，没有递归创建子代理、跨仓库工作或修改文件。当前表面没有向调用方暴露可区分的 `SubagentStart.additionalContext` 元数据，因此三者均将 Hook 注入状态报告为 `unknown`。

## Hook 状态

| 事件 | 当前真实状态 |
| --- | --- |
| `SessionStart` | `not_exposed_by_current_desktop_surface`；当前任务没有带来源标识的启动 Hook 回执。 |
| `PreToolUse` | `not_exposed_by_current_desktop_surface`；安全只读 `git status --short --branch` 成功，但没有可观察 Hook 回执。 |
| `PostToolUse` | `not_exposed_by_current_desktop_surface`；当前表面没有可区分的 Hook 运行回执。 |
| `PreCompact` | `not_triggered_without_artificial_context_inflation`。 |
| `PostCompact` | `not_triggered_without_artificial_context_inflation`。 |
| `SubagentStart` | `not_exposed_by_current_desktop_surface`；本次 `qa-lead` 只读探针已启动，但 additionalContext 注入不可观察。 |
| `SubagentStop` | `not_exposed_by_current_desktop_surface`；该探针已完成，但事件执行不可观察。 |
| `Stop` | `not_observable_inside_active_task`；不在阶段报告完成前伪造。 |

项目 `.codex/config.toml` 声明 `features.hooks = true`，`.codex/hooks.json` 的 matcher 与当前官方 Codex Hook 文档一致。2026-07-18 续验发现 Windows `commandWindows` 仅调用 PATH 中的 `python`，而本机 PATH 没有 Python，因此原配置即使获得信任也无法启动处理器。已用失败测试复现，并把启动顺序修复为有效的 `CODEX_PYTHON`、Codex Desktop 现有捆绑 Python、PATH Python；不安装解释器。用 `.codex/hooks.json` 中的实际 `SessionStart` 命令直接执行，在没有 `CODEX_PYTHON` 和 PATH Python 的条件下成功返回合法 JSON。

用户已确认非托管项目 Hook 的当前配置哈希受信任，`hooks_enabled=yes`。直接运行处理器、配置命令、模拟 JSON 输入和单元测试证明处理器及启动链有效，但这些属于直接/模拟证据，不属于 Codex 生命周期事件触发证据。

`notify.sh=unsupported`：当前目标事件列表没有 Notification；未转换、未运行，也未启用 Windows toast。

## 安全修复

代表性 QA Agent 发现 `detect_forbidden_git_operation()` 只检查首个 Git 调用。已用回归测试证明直接串接、PowerShell/cmd 包装、未加引号及双引号内命令替换、Bash 反引号替换与括号分组中的 `push`、`reset`、`clean` 或 `rebase` 会漏检，并做最小修复：逐段检查未加引号的 shell 控制符，递归检查已知 shell 包装、可执行命令替换与未加引号的括号命令，同时保留单引号字面量及带控制符或示例文本的正常提交信息为允许项。生成器中的 `HOOK_SCRIPT` 已同步，新增一致性测试防止重新生成时回退。没有执行任何真实危险 Git 命令。

续验发现 Windows Hook 启动器依赖不存在的 PATH Python。新增的回归测试先在移除 PATH Python、仅提供已验证解释器入口时稳定失败，再修复生成器与 `.codex/hooks.json`；同时新增生成配置一致性测试，防止重新生成时退回不可执行命令。

## 验证与限制

- 迁移单元测试：18/18 passed
- Godot runtime 单元测试：27/27 passed
- 迁移验证器：passed
- Godot runtime 验证器：passed（当前沙箱子进程无法写 Godot 缓存时会误报；经批准在沙箱外运行同一既有验证器通过）
- `git diff --check`：passed
- 独立 `phase-review`：passed；无可操作 findings
- Godot MCP：未修改
- Demo 产品功能：未修改
- 上游快照：未修改
- 未记录 Token、Cookie、凭据或提示词正文

## 收敛与表面限制

- 用户已确认当前 Hook 哈希受信任，项目 Hook 已启用且配置可解析。
- 安全 Git 探针与一个 `qa-lead` 只读探针均成功；没有越权、跨项目访问或 Demo 产品范围修改。
- `SessionStart`、`PreToolUse`、`PostToolUse`、`SubagentStart`、`SubagentStop` 与 `Stop` 的真实回执未由当前 Desktop 表面暴露，记录为 `lifecycle_hook_runtime_observability=not_exposed_by_current_desktop_surface`，不再作为阻塞项。
- `PreCompact`/`PostCompact` 为 `not_triggered_without_artificial_context_inflation`；未人为触发。

因此 Phase 2C 以 `passed_with_surface_limitations` 关闭；下一阶段由用户另行决定。
