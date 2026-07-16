---
name: estimate
description: "Estimates task effort by analyzing complexity, dependencies, historical velocity, and risk factors. Produces a structured estimate with confidence levels. 当用户明确点名该流程或当前任务与其专业目标直接匹配时使用；不用于无关的一般开发任务。"
---

## Codex 适配约束

- 将本工作流视为项目级 Skill，而不是 Codex 内置斜杠命令。
- 仅在 description 的窄触发条件满足时隐式调用；不得自动启动完整制作流程或推进下一阶段。
- 用户保留产品与创意最终决策权；非关键实现细节采用合理默认并记录。
- 如需子代理，只允许单层、最多 3 个、互斥写入范围；不得多 Agent 修改同一文件。
- 使用当前 Codex 工具与沙箱；原工具许可、模型字段和权限语法已移除。

## Phase 1: Understand the Task

Read the task description from the argument. If the description is too vague to estimate meaningfully, ask for clarification before proceeding.

Read AGENTS.md for project context: tech stack, coding standards, architectural patterns, and any estimation guidelines.

Read relevant design documents from `design/gdd/` if the task relates to a documented feature or system.

---

## Phase 2: Scan Affected Code

Identify files and modules that would need to change:

- Assess complexity (size, dependency count, cyclomatic complexity)
- Identify integration points with other systems
- Check for existing test coverage in the affected areas
- Read past sprint data from `production/sprints/` for similar completed tasks and historical velocity

---

## Phase 3: Analyze Complexity Factors

**Code Complexity:**
- Lines of code in affected files
- Number of dependencies and coupling level
- Whether this touches core/engine code vs leaf/feature code
- Whether existing patterns can be followed or new patterns are needed

**Scope:**
- Number of systems touched
- New code vs modification of existing code
- Amount of new test coverage required
- Data migration or configuration changes needed

**Risk:**
- New technology or unfamiliar libraries
- Unclear or ambiguous requirements
- Dependencies on unfinished work
- Cross-system integration complexity
- Performance sensitivity

---

## Phase 4: Generate the Estimate

```markdown
## Task Estimate: [Task Name]
Generated: [Date]

### Task Description
[Restate the task clearly in 1-2 sentences]

### Complexity Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Systems affected | [List] | [Core, gameplay, UI, etc.] |
| Files likely modified | [Count] | [Key files listed below] |
| New code vs modification | [Ratio] | |
| Integration points | [Count] | [Which systems interact] |
| Test coverage needed | [Low / Medium / High] | |
| Existing patterns available | [Yes / Partial / No] | |

**Key files likely affected:**
- `[path/to/file1]` -- [what changes here]

### Effort Estimate

| Scenario | Days | Assumption |
|----------|------|------------|
| Optimistic | [X] | Everything goes right, no surprises |
| Expected | [Y] | Normal pace, minor issues, one round of review |
| Pessimistic | [Z] | Significant unknowns surface, blocked for a day |

**Recommended budget: [Y days]**

### Confidence: [High / Medium / Low]

[Explain which factors drive the confidence level for this specific task.]

### Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

### Dependencies

| Dependency | Status | Impact if Delayed |
|-----------|--------|-------------------|

### Suggested Breakdown

| # | Sub-task | Estimate | Notes |
|---|----------|----------|-------|
| 1 | [Research / spike] | [X days] | |
| 2 | [Core implementation] | [X days] | |
| 3 | [Testing and validation] | [X days] | |
| | **Total** | **[Y days]** | |

### Notes and Assumptions
- [Key assumption that affects the estimate]
- [Any caveats about scope boundaries]
```

Output the estimate with a brief summary: recommended budget, confidence level, and the single biggest risk factor.

This skill is read-only — no files are written. Verdict: **COMPLETE** — estimate generated.

---

## Phase 5: Next Steps

- If confidence is Low: recommend a time-boxed spike (`$prototype`) before committing.
- If the task is > 10 days: recommend breaking it into smaller stories via `$create-stories`.
- To schedule the task: run `$sprint-plan update` to add it to the next sprint.

### Guidelines

- Always give a range (optimistic / expected / pessimistic), never a single number
- The recommended budget should be the expected estimate, not the optimistic one
- Round to half-day increments — estimating in hours implies false precision for tasks longer than a day
- Do not pad estimates silently — call out risk explicitly so the team can decide
