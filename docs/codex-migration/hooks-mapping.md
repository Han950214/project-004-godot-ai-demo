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

运行加载验证：`deferred_codex_cli`。
