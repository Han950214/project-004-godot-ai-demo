# Game Studio Skill Index

本索引只供 `game-studio-router` 定向选择下游 Skill；73 个下游 Skill 均关闭隐式调用，但仍支持显式 `$skill-name`。

## concept-and-design

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `architecture-decision` | concept/pre-production | Creates an Architecture Decision Record (ADR) documenting a significant technical decision, its context, alternatives considered, and consequences | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `art-bible` | concept/pre-production | Guided, section-by-section Art Bible authoring | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `art-director` |
| `asset-spec` | concept/pre-production | Generate per-asset visual specifications and AI generation prompts from GDDs, level docs, or character profiles | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `art-director` |
| `brainstorm` | concept/pre-production | Guided game concept ideation — from zero idea to a structured game concept document | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `create-architecture` | concept/pre-production | Guided, section-by-section authoring of the master architecture document for the game | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `create-control-manifest` | concept/pre-production | After architecture is complete, produces a flat actionable rules sheet for programmers — what you must do, what you must never do, per system and per layer | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `design-system` | concept/pre-production | Guided, section-by-section GDD authoring for a single game system | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `game-designer` |
| `map-systems` | concept/pre-production | Decompose a game concept into individual systems, map dependencies, prioritize design order, and create the systems index | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `game-designer` |
| `quick-design` | concept/pre-production | Lightweight design spec for small changes — tuning adjustments, minor mechanics, balance tweaks | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `ux-designer` |
| `ux-design` | concept/pre-production | Guided, section-by-section UX spec authoring for a screen, flow, or HUD | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `ux-designer` |

## onboarding

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `adopt` | discovery/setup | Brownfield onboarding — audits existing project artifacts for template format compliance (not just existence), classifies gaps by impact, and produces a numbered migration plan | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `help` | discovery/setup | Analyzes what is done and the users query and offers advice on what to do next | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `onboard` | discovery/setup | Generates a contextual onboarding document for a new contributor or agent joining the project | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `project-stage-detect` | discovery/setup | Automatically analyze project state, detect stage, identify gaps, and recommend next steps based on existing artifacts | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `setup-engine` | discovery/setup | Configure the project's game engine and version | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `start` | discovery/setup | First-time onboarding — asks where you are, then guides you to the right workflow | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `art-director` |

## production

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `create-epics` | pre-production/production | Translate approved GDDs + architecture into epics — one epic per architectural module | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `create-stories` | pre-production/production | Break a single epic into implementable story files | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `dev-story` | pre-production/production | Read a story file and implement it | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `lead-programmer` |
| `milestone-review` | pre-production/production | Generates a comprehensive milestone progress review including feature completeness, quality metrics, risk assessment, and go/no-go recommendation | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `propagate-design-change` | pre-production/production | When a GDD is revised, scans all ADRs and the traceability index to identify which architectural decisions are now potentially stale | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `game-designer` |
| `retrospective` | pre-production/production | Generates a sprint or milestone retrospective by analyzing completed work, velocity, blockers, and patterns | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `sprint-plan` | pre-production/production | Generates a new sprint plan or updates an existing one based on the current milestone, completed work, and available capacity | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `sprint-status` | pre-production/production | Fast sprint status check | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `story-done` | pre-production/production | End-of-story completion review | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `story-readiness` | pre-production/production | Validate that a story file is implementation-ready | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |

## prototyping

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `prototype` | concept/pre-production | Concept prototype — validate the core idea is worth designing before writing GDDs | 目标是直接交付正式生产实现且无需验证假设时不要使用。 | `lead-programmer` |
| `vertical-slice` | concept/pre-production | Pre-Production validation — build a production-quality end-to-end build to confirm the full game loop is achievable before committing to Production | 目标是直接交付正式生产实现且无需验证假设时不要使用。 | `lead-programmer` |

## quality

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `bug-report` | testing/acceptance | Creates a structured bug report from a description, or analyzes code to identify potential bugs | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `bug-triage` | testing/acceptance | Read all open bugs in production/qa/bugs/, re-evaluate priority vs | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `code-review` | testing/acceptance | Performs an architectural and quality code review on a specified file or set of files | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `lead-programmer` |
| `playtest-report` | testing/acceptance | Generates a structured playtest report template or analyzes existing playtest notes into a structured format | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `qa-plan` | testing/acceptance | Generate a QA test plan for a sprint or feature | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `regression-suite` | testing/acceptance | Map test coverage to GDD critical paths, identify fixed bugs without regression tests, flag coverage drift from new features, and maintain tests/regression-suite.md | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `ux-designer` |
| `smoke-check` | testing/acceptance | Run the critical path smoke test gate before QA hand-off | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `soak-test` | testing/acceptance | Generate a soak test protocol for extended play sessions | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `test-evidence-review` | testing/acceptance | Quality review of test files and manual evidence documents | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `test-flakiness` | testing/acceptance | Detect non-deterministic (flaky) tests by reading CI run logs or test result history | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `test-helpers` | testing/acceptance | Generate engine-specific test helper libraries for the project's test suite | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |
| `test-setup` | testing/acceptance | Scaffold the test framework and CI/CD pipeline for the project's engine | 没有可检查实现、构建、缺陷或验收输入时不要使用。 | `qa-lead` |

## release-and-operations

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `changelog` | release/live operations | Auto-generates a changelog from git commits, sprint data, and design documents | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |
| `day-one-patch` | release/live operations | Prepare a day-one patch for a game launch | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |
| `hotfix` | release/live operations | Emergency fix workflow that bypasses normal sprint processes with a full audit trail | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |
| `launch-checklist` | release/live operations | Complete launch readiness validation covering every department: code, content, store, marketing, community, infrastructure, legal, and go/no-go sign-offs | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |
| `localize` | release/live operations | Full localization pipeline: scan for hardcoded strings, extract and manage string tables, validate translations, generate translator briefings, run cultural/sensitivity review,... | 尚未进入发布或线上运维阶段时不要使用。 | `localization-lead` |
| `patch-notes` | release/live operations | Generate player-facing patch notes from git history, sprint data, and internal changelogs | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |
| `release-checklist` | release/live operations | Generates a comprehensive pre-release validation checklist covering build verification, certification requirements, store metadata, and launch readiness | 尚未进入发布或线上运维阶段时不要使用。 | `release-manager` |

## review-and-analysis

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `architecture-review` | current-stage review | Validates completeness and consistency of the project architecture against all GDDs | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `asset-audit` | current-stage review | Audits game assets for compliance with naming conventions, file size budgets, format standards, and pipeline requirements | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `art-director` |
| `balance-check` | current-stage review | Analyzes game balance data files, formulas, and configuration to identify outliers, broken progressions, degenerate strategies, and economy imbalances | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `game-designer` |
| `consistency-check` | current-stage review | Scan all GDDs against the entity registry to detect cross-document inconsistencies: same entity with different stats, same item with different values, same formula with differen... | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `content-audit` | current-stage review | Audit GDD-specified content counts against implemented content | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `design-review` | current-stage review | Reviews a game design document for completeness, internal consistency, implementability, and adherence to project design standards | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `game-designer` |
| `estimate` | current-stage review | Estimates task effort by analyzing complexity, dependencies, historical velocity, and risk factors | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `perf-profile` | current-stage review | Structured performance profiling workflow | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `reverse-document` | current-stage review | Generate design or architecture documents from existing implementation | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `review-all-gdds` | current-stage review | Holistic cross-GDD consistency and game design review | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `scope-check` | current-stage review | Analyze a feature or sprint for scope creep by comparing current scope against the original plan | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `security-audit` | current-stage review | Audit the game for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure, and input validation gaps | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `security-engineer` |
| `tech-debt` | current-stage review | Track, categorize, and prioritize technical debt across the codebase | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `technical-director` |
| `ux-review` | current-stage review | Validates a UX spec, HUD design, or interaction pattern library for completeness, accessibility compliance, GDD alignment, and implementation readiness | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `ux-designer` |

## studio-meta

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `gate-check` | any stage | Validate readiness to advance between development phases | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `skill-improve` | any stage | Improve a skill using a test-fix-retest loop | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `producer` |
| `skill-test` | any stage | Validate skill files for structural compliance and behavioral correctness | 任务不属于该专业流程，或会自动推进下一制作阶段时不要使用。 | `qa-lead` |

## team-collaboration

| name | stage | use_when | do_not_use_when | likely_agent |
| --- | --- | --- | --- | --- |
| `team-audio` | current-stage collaboration | Orchestrate audio team: audio-director + sound-designer + technical-artist + gameplay-programmer for full audio pipeline from direction to implementation | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `audio-director` |
| `team-combat` | current-stage collaboration | Orchestrate the combat team: coordinates game-designer, gameplay-programmer, ai-programmer, technical-artist, sound-designer, and qa-tester to design, implement, and validate a... | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `game-designer` |
| `team-level` | current-stage collaboration | Orchestrate level design team: level-designer + narrative-director + world-builder + art-director + systems-designer + qa-tester for complete area/level creation | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `producer` |
| `team-live-ops` | current-stage collaboration | Orchestrate the live-ops team for post-launch content planning: coordinates live-ops-designer, economy-designer, analytics-engineer, community-manager, writer, and narrative-dir... | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `producer` |
| `team-narrative` | current-stage collaboration | Orchestrate the narrative team: coordinates narrative-director, writer, world-builder, and level-designer to create cohesive story content, world lore, and narrative-driven leve... | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `narrative-director` |
| `team-polish` | current-stage collaboration | Orchestrate the polish team: coordinates performance-analyst, technical-artist, sound-designer, and qa-tester to optimize, polish, and harden a feature or area for release quality | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `producer` |
| `team-qa` | current-stage collaboration | Orchestrate the QA team through a full testing cycle | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `qa-lead` |
| `team-release` | current-stage collaboration | Orchestrate the release team: coordinates release-manager, qa-lead, devops-engineer, and producer to execute a release from candidate to deployment | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `release-manager` |
| `team-ui` | current-stage collaboration | Orchestrate the UI team through the full UX pipeline: from UX spec authoring through visual design, implementation, review, and polish | 普通单文件任务、无互斥并行工作面或未要求团队协作时不要使用。 | `ux-designer` |
