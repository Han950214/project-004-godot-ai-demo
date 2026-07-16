
# Codex Game Studio 项目规则

## 定位与技术栈

- 本项目是 Claude Code Game Studios v1.0.0 的 Codex 静态适配层；上游只读快照不得修改。
- 默认目标引擎为 Godot 4.x stable，默认语言为 GDScript。Unity 与 Unreal 角色仅为完整迁移保留，除非用户明确改变引擎，不得主动路由给它们。
- 用户拥有产品、创意、范围与取舍的最终决策权；Agent 负责分析、实现和验证。非关键实现细节采用合理默认并记录，只有会改变产品方向或超出授权范围时才询问。

## 路由与层级

- 制作与总监层负责方向、跨部门冲突和质量门禁：art-director, audio-director, creative-director, narrative-director, technical-director, producer。
- 部门负责人负责拆解、验收和升级：lead-programmer, localization-lead, producer, qa-lead, release-manager。
- 专家只在各自领域内工作；跨领域改动先报告给对应负责人或主 Agent，不得擅自扩大范围。
- 自定义 Agent 位于 `.codex/agents/`，Skill 位于 `.agents/skills/`。未显式点名 Skill 时由 `game-studio-router` 从索引选择最窄流程；只按任务需要选择角色，不得一次加载全部 Skill 或召集全部角色。
- 子代理最多 4 个线程、深度 1；只读且互斥的分析可并行，写入默认由主 Agent 单线程完成。子代理不得继续创建子代理。

## 工作流

1. 先确认当前制作阶段、输入文档和验收标准；可使用 `$start`、`$project-stage-detect`、`$help` 等对应 Skill。
2. 设计决策先给出选项、取舍和推荐；产品方向由用户决定。
3. 实现遵守最近的嵌套 `AGENTS.md`。Godot API 以项目声明版本为准，不凭记忆臆测。
4. 每个实现阶段提供与风险相称的自动测试、静态检查或试玩证据；无法运行的验证必须明确标为 deferred。
5. 不得自动进入下一制作阶段。

## Git 与安全

- 禁止自动 `git push`、`git reset`、`git clean`、`git rebase`、`git commit --amend` 和强制推送。
- 不读取或提交 `.env`、密钥、Token、Cookie 或凭据；不修改用户级 Codex 配置、系统设置或仓库外文件。
- 创建 commit 必须由当前任务明确授权；禁止 push。
- 不运行上游 Claude 脚本或安装脚本。所有上游材料仅用于审计和升级。

## 目录边界

- `upstream/`：不可编辑的来源快照与校验清单。
- `.agents/skills/`：Codex Skill；每项含 `SKILL.md`、`agents/openai.yaml`、`UPSTREAM.md`。
- `.codex/agents/`：项目级自定义 Agent。
- `.codex/hooks/`、`.codex/hooks.json`：经适配的 Codex command Hooks。
- `docs/game-studio-reference/`：由上游文档派生并转换路径/术语的活动参考。
- `docs/codex-migration/`：架构、映射、兼容性与验收证据。
- `src/`、`assets/`、`design/`、`tests/`、`prototypes/`：对应嵌套规则只影响各自子树。
