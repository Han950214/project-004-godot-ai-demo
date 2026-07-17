# Agents 映射

## Phase 2C 运行证据

静态验证确认 49 个 `.codex/agents/*.toml` 可解析、名称唯一，且 `description` 与 `developer_instructions` 非空。当前子代理接口已代表性调用 `godot-specialist`、`qa-lead`、`producer`，三个只读任务均完成；本次另以一个只读 `qa-lead` 探针确认没有 Demo 产品范围改动。这不等于逐个运行 49 个 Agent。`SubagentStart`/`SubagentStop` 的项目 Hook 注入在当前表面不可观察，状态为 `not_exposed_by_current_desktop_surface`。完整证据见 `docs/runtime-evidence/codex-skills-agents-hooks-live-validation.md`。

| source_agent | target_toml | status | claude_specific_fields_removed | behavior_differences |
| --- | --- | --- | --- | --- |
| .claude/agents/accessibility-specialist.md | .codex/agents/accessibility-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ai-programmer.md | .codex/agents/ai-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/analytics-engineer.md | .codex/agents/analytics-engineer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/art-director.md | .codex/agents/art-director.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/audio-director.md | .codex/agents/audio-director.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/community-manager.md | .codex/agents/community-manager.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/creative-director.md | .codex/agents/creative-director.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/devops-engineer.md | .codex/agents/devops-engineer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/economy-designer.md | .codex/agents/economy-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/engine-programmer.md | .codex/agents/engine-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/game-designer.md | .codex/agents/game-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/gameplay-programmer.md | .codex/agents/gameplay-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/godot-csharp-specialist.md | .codex/agents/godot-csharp-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/godot-gdextension-specialist.md | .codex/agents/godot-gdextension-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/godot-gdscript-specialist.md | .codex/agents/godot-gdscript-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/godot-shader-specialist.md | .codex/agents/godot-shader-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/godot-specialist.md | .codex/agents/godot-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/lead-programmer.md | .codex/agents/lead-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/level-designer.md | .codex/agents/level-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/live-ops-designer.md | .codex/agents/live-ops-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/localization-lead.md | .codex/agents/localization-lead.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/narrative-director.md | .codex/agents/narrative-director.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/network-programmer.md | .codex/agents/network-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/performance-analyst.md | .codex/agents/performance-analyst.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/producer.md | .codex/agents/producer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/prototyper.md | .codex/agents/prototyper.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/qa-lead.md | .codex/agents/qa-lead.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/qa-tester.md | .codex/agents/qa-tester.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/release-manager.md | .codex/agents/release-manager.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/security-engineer.md | .codex/agents/security-engineer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/sound-designer.md | .codex/agents/sound-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/systems-designer.md | .codex/agents/systems-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/technical-artist.md | .codex/agents/technical-artist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/technical-director.md | .codex/agents/technical-director.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/tools-programmer.md | .codex/agents/tools-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ue-blueprint-specialist.md | .codex/agents/ue-blueprint-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ue-gas-specialist.md | .codex/agents/ue-gas-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ue-replication-specialist.md | .codex/agents/ue-replication-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ue-umg-specialist.md | .codex/agents/ue-umg-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ui-programmer.md | .codex/agents/ui-programmer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unity-addressables-specialist.md | .codex/agents/unity-addressables-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unity-dots-specialist.md | .codex/agents/unity-dots-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unity-shader-specialist.md | .codex/agents/unity-shader-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unity-specialist.md | .codex/agents/unity-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unity-ui-specialist.md | .codex/agents/unity-ui-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/unreal-specialist.md | .codex/agents/unreal-specialist.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/ux-designer.md | .codex/agents/ux-designer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/world-builder.md | .codex/agents/world-builder.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
| .claude/agents/writer.md | .codex/agents/writer.toml | converted | tools, model, maxTurns | 继承当前 Codex 会话权限；关键产品决策才询问；禁止递归委派和自主 push。 |
