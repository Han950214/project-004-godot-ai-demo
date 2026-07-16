
# 迁移架构

固定上游 `v1.0.0` / `984023ddac0d5e27624f2baacde6105e45de375f` / tree `45e93bee12c3f1d80052f7406f0180e9bece8382` 以未修改快照保存在 `upstream/`。`SOURCE-MANIFEST.json` 只能从经过 Git commit、tree、origin 和 clean 状态验证的源 checkout 生成，再与目标快照双向比对。活动适配层与快照分离：根 `AGENTS.md` 负责总则，`.codex/agents/` 承载 49 个独立 Agent，`.agents/skills/` 承载 73 个关闭隐式调用的下游 Skill 和唯一隐式 `game-studio-router`，路径规则落到最近层级 `AGENTS.md`，生命周期行为由 `.codex/hooks.json` 和 Python command Hook 实现。

状态词严格区分 `preserved`、`converted`、`adapted`、`deferred`、`unsupported`。Godot 与 MCP 运行验证为 `deferred_missing_godot`，不影响静态迁移验收。
