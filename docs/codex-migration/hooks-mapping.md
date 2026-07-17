# Hooks 映射

| source_hook | source_event | target_event | status | target_script | behavior_difference |
| --- | --- | --- | --- | --- | --- |
| detect-gaps.sh | SessionStart | SessionStart | adapted | .codex/hooks/game_studio_hook.py session-start | 只提供缺口提示，不写状态文件。 |
| log-agent-stop.sh | SubagentStop | SubagentStop | adapted | .codex/hooks/game_studio_hook.py subagent-stop | 不持久化会话日志，避免隐式仓库写入。 |
| log-agent.sh | SubagentStart | SubagentStart | adapted | .codex/hooks/game_studio_hook.py subagent-start | 改为注入单层委派边界。 |
| notify.sh | Notification | none | unsupported |  | 当前 Codex command Hook 事件列表无 Notification；不启用 Windows toast。 |
| post-compact.sh | PostCompact | PostCompact | adapted | .codex/hooks/game_studio_hook.py post-compact | 输出恢复提示，不依赖 Claude 状态文件。 |
| pre-compact.sh | PreCompact | PreCompact | adapted | .codex/hooks/game_studio_hook.py pre-compact | 只读汇总 git 状态，不写 production/session-state。 |
| session-start.sh | SessionStart | SessionStart | converted | .codex/hooks/game_studio_hook.py session-start | 使用 Codex additionalContext。 |
| session-stop.sh | Stop | Stop | adapted | .codex/hooks/game_studio_hook.py stop | 返回合法空 JSON，不自动写会话日志。 |
| validate-assets.sh | PostToolUse | PostToolUse | converted | .codex/hooks/game_studio_hook.py post-edit | Python 标准库验证变更 JSON。 |
| validate-commit.sh | PreToolUse | PreToolUse | converted | .codex/hooks/game_studio_hook.py pre-tool | 只在 git commit 时验证暂存 JSON。 |
| validate-push.sh | PreToolUse | PreToolUse | converted | .codex/hooks/game_studio_hook.py pre-tool | 使用 permissionDecision=deny 明确拒绝 push。 |
| validate-skill-change.sh | PostToolUse | PostToolUse | adapted | .codex/hooks/game_studio_hook.py post-edit | 校验 Codex SKILL.md frontmatter，不递归启动 Codex。 |

## Phase 2C 运行状态

- 配置：`features.hooks = true`，八个目标事件集合与官方 matcher 形态通过静态验证。
- 处理器：模拟输入与单元测试通过；组合 Git 命令绕过已补回归测试并修复。
- Windows 启动：已修复 PATH 无 `python` 时原 `commandWindows` 无法启动处理器的问题；依次使用有效的 `CODEX_PYTHON`、Codex Desktop 现有捆绑 Python、PATH Python。配置命令直接调用返回合法 `SessionStart` JSON，但不计为生命周期触发。
- `SessionStart`：用户已确认当前配置哈希受信任；当前 Desktop 表面为 `not_exposed_by_current_desktop_surface`，没有带来源标识的启动回执。
- `PreToolUse` / `PostToolUse`：安全 Git 探针成功，但当前表面没有可区分的 Hook 回执，状态为 `not_exposed_by_current_desktop_surface`，不写成已触发。
- `PreCompact` / `PostCompact`：`not_triggered_without_artificial_context_inflation`。
- `SubagentStart` / `SubagentStop`：`qa-lead` 只读探针已启动并完成，但 Hook additionalContext/事件执行为 `not_exposed_by_current_desktop_surface`。
- `Stop`：`not_observable_inside_active_task`。
- `notify.sh`：`unsupported`，未转换、未运行。

用户已确认当前非托管项目 Hook 的配置哈希受信任，`hooks_enabled=yes`。处理器模拟或配置命令直接调用不等同于 Codex 生命周期真实触发；由于当前 Desktop 表面未暴露回执，Phase 2C 以 `passed_with_surface_limitations` 收敛。证据见 `docs/runtime-evidence/codex-skills-agents-hooks-live-validation.md`。
