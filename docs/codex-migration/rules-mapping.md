# Rules 映射

| source_rule | source_paths | target_agents_md | status | behavior_differences |
| --- | --- | --- | --- | --- |
| .claude/rules/ai-code.md | src/ai/** | src/ai/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/data-files.md | assets/data/** | assets/data/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/design-docs.md | design/gdd/** | design/gdd/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/engine-code.md | src/core/** | src/core/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/gameplay-code.md | src/gameplay/** | src/gameplay/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/narrative.md | design/narrative/** | design/narrative/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/network-code.md | src/networking/** | src/networking/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/prototype-code.md | prototypes/** | prototypes/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/shader-code.md | assets/shaders/** | assets/shaders/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/test-standards.md | tests/** | tests/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |
| .claude/rules/ui-code.md | src/ui/** | src/ui/AGENTS.md | converted | 由 Claude 路径规则改为 Codex 最近层级 AGENTS.md。 |

Shell deny 配置另迁移为 `.codex/rules/game-studio-safety.rules`；共 1 个 command rules 文件。Rules 与 Hooks 都是辅助护栏，不能替代任务边界、Codex 沙箱、审批和权限系统。
