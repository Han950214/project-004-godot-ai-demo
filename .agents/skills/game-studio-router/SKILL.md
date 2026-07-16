---
name: game-studio-router
description: "在用户提出游戏策划、原型、系统设计、开发、测试、发布或明确团队协作任务，但未点名具体 Game Studio Skill 时自动路由。普通非游戏任务、已显式调用下游 $skill 或仅需简单问答时不触发。"
---

# Game Studio Router

## 目标

把用户的游戏开发请求路由到最窄、最合适的项目 Skill。用户不需要预先知道 Skill 名称。

## 路由流程

1. 只读取识别当前制作阶段和任务类别所需的最小上下文；不扫描全部历史。
2. 读取 `references/skill-index.md`，按 `stage`、`category`、`use_when` 和 `do_not_use_when` 筛选。
3. 默认只选择一个下游 Skill，并读取该 Skill 的 `SKILL.md` 后执行其流程。
4. 仅当任务确实存在两个或三个互斥且可独立并行的工作面时，才增加第二或第三个下游 Skill；写入范围必须互斥。
5. 不一次加载全部 73 个下游 Skill，不一次召集全部 Agent，不允许子代理递归委派。
6. 不自动进入下一制作阶段；阶段转换、产品方向和创意取舍仍由用户决定。
7. 如果用户已显式调用 `$skill-name`，直接遵循该 Skill，不再二次路由。

## 输出

内部记录选择的阶段、类别、下游 Skill 和原因；只向用户呈现完成任务所需的信息，不要求用户学习路由表。
