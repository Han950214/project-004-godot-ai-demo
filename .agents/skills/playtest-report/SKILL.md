---
name: playtest-report
description: "Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis. 当用户明确点名该流程或当前任务与其专业目标直接匹配时使用；不用于无关的一般开发任务。"
---

## Codex 适配约束

- 将本工作流视为项目级 Skill，而不是 Codex 内置斜杠命令。
- 本下游 Skill 默认不隐式调用；仅由用户显式 `$skill-name` 或 `game-studio-router` 定向选择。不得自动启动完整制作流程或推进下一阶段。
- 用户保留产品与创意最终决策权；非关键实现细节采用合理默认并记录。
- 如需子代理，只允许单层、最多 3 个、互斥写入范围；不得多 Agent 修改同一文件。
- 使用当前 Codex 工具与沙箱；原工具许可、模型字段和权限语法已移除。

## Phase 1: Parse Arguments

Resolve the review mode (once, store for all gate spawns this run):
1. If `--review [full|lean|solo]` was passed → use that
2. Else read `production/review-mode.txt` → use that value
3. Else → default to `lean`

See `docs/game-studio-reference/director-gates.md` for the full check pattern.

Determine the mode:

- `new` → generate a blank playtest report template
- `analyze [path]` → read raw notes and fill in the template with structured findings

---

## Phase 2A: New Template Mode

Generate this template and output it to the user:

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
[What specific features or flows were being tested]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible |
|---|-------------|----------|-------------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

---

## Phase 2B: Analyze Mode

Read the raw notes at the provided path. Cross-reference with existing design documents. Fill in the template above with structured findings. Flag any playtest observations that conflict with design intent.

---

## Phase 3: Action Routing

Categorize all findings into four buckets:

- **Design changes needed** — fun issues, player confusion, broken mechanics, observations that conflict with the GDD's intended experience
- **Balance adjustments** — numbers feel wrong, difficulty too spiked or too flat
- **Bug reports** — clear implementation defects that are reproducible
- **Polish items** — not blocking progress, but friction or feel issues for later

Present the categorized list, then route:

- **Design changes:** "Run `$propagate-design-change [path]` on the affected design document to find downstream impacts before making changes."
- **Balance adjustments:** "Run `$balance-check [system]` to verify the full balance picture before tuning values."
- **Bugs:** "Use `$bug-report` to formally track these."
- **Polish items:** "Add to the polish backlog in `production/` when the team reaches that phase."

---

## Phase 3b: Creative Director Player Experience Review

**Review mode check** — apply before spawning CD-PLAYTEST:
- `solo` → skip. Note: "CD-PLAYTEST skipped — Solo mode." Proceed to Phase 4 (save the report).
- `lean` → skip (not a PHASE-GATE). Note: "CD-PLAYTEST skipped — Lean mode." Proceed to Phase 4 (save the report).
- `full` → spawn as normal.

After categorising findings, spawn `creative-director` through an optional Codex subagent using gate **CD-PLAYTEST** (`docs/game-studio-reference/director-gates.md`).

Pass: the structured report content, game pillars and core fantasy (from `design/gdd/game-concept.md`), the specific hypothesis being tested.

Present the creative director's assessment before saving the report. If CONCERNS or REJECT, add a `## Creative Director Assessment` section to the report capturing the verdict and feedback. If APPROVE, note the approval in the report.

---

## Phase 4: Save Report

Ask: "May I write this playtest report to `production/qa/playtests/playtest-[date]-[tester].md`?"

If yes, write the file, creating the directory if needed.

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — playtest report generated.

- Act on the highest-priority finding category first.
- After addressing design changes: re-run `$design-review` on the updated GDD.
- After fixing bugs: re-run `$bug-triage` to update priorities.
