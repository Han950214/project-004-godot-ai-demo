---
name: onboard
description: "Generates a contextual onboarding document for a new contributor or agent joining the project. Summarizes project state, architecture, conventions, and current priorities relevant to the specified role or area. 当用户明确点名该流程或当前任务与其专业目标直接匹配时使用；不用于无关的一般开发任务。"
---

## Codex 适配约束

- 将本工作流视为项目级 Skill，而不是 Codex 内置斜杠命令。
- 仅在 description 的窄触发条件满足时隐式调用；不得自动启动完整制作流程或推进下一阶段。
- 用户保留产品与创意最终决策权；非关键实现细节采用合理默认并记录。
- 如需子代理，只允许单层、最多 3 个、互斥写入范围；不得多 Agent 修改同一文件。
- 使用当前 Codex 工具与沙箱；原工具许可、模型字段和权限语法已移除。

## Phase 1: Load Project Context

Read AGENTS.md for project overview and standards.

Read the relevant agent definition from `.codex/agents/` if a specific role is specified.

---

## Phase 2: Scan Relevant Area

- For programmers: scan `src/` for architecture, patterns, key files
- For designers: scan `design/` for existing design documents
- For narrative: scan `design/narrative/` for world-building and story docs
- For QA: scan `tests/` for existing test coverage
- For production: scan `production/` for current sprint and milestone

Read recent changes (git log if available) to understand current momentum.

---

## Phase 3: Generate Onboarding Document

```markdown
# Onboarding: [Role/Area]

## Project Summary
[2-3 sentence summary of what this game is and its current state]

## Your Role
[What this role does on this project, key responsibilities, who you report to]

## Project Architecture
[Relevant architectural overview for this role]

### Key Directories
| Directory | Contents | Your Interaction |
|-----------|----------|-----------------|

### Key Files
| File | Purpose | Read Priority |
|------|---------|--------------|

## Current Standards and Conventions
[Summary of conventions relevant to this role from AGENTS.md and agent definition]

## Current State of Your Area
[What has been built, what is in progress, what is planned next]

## Current Sprint Context
[What the team is working on now and what is expected of this role]

## Key Dependencies
[What other roles/systems this role interacts with most]

## Common Pitfalls
[Things that trip up new contributors in this area]

## First Tasks
[Suggested first tasks to get oriented and productive]

1. [Read these documents first]
2. [Review this code/content]
3. [Start with this small task]

## Questions to Ask
[Questions the new contributor should ask to get fully oriented]
```

---

## Phase 4: Save Document

Present the onboarding document to the user.

Ask: "Confirm the requested destination when it is ambiguous: `production/onboarding/onboard-[role]-[date].md`?"

If yes, write the file, creating the directory if needed.

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — onboarding document generated.

- Share the onboarding doc with the new contributor before their first session.
- Run `$sprint-status` to show the new contributor current progress.
- Run `$help` if the contributor needs guidance on what to work on next.
