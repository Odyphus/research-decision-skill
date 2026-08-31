# Changelog

## 0.5.0-preview — 2026-08-31

- 对外名称、Skill 技术名称、调用名和仓库名统一为 `research-decision-skill`。
- 新建研究记录目录改为 `.research-decision/`；仅存在旧版 `.research-exploration/` 时原地兼容，两个目录并存时停止写入。
- 重写中文 GitHub README，优先说明产品价值、安装、真实提问方式、示例、支持领域、验证边界和隐私提醒。
- 更新 schema 标识、引用信息、快速开始与安装文档，并完成公开包重新验证。
- 继续标记为 Preview；真人领域专家评审和真实学习迁移效果仍为 `not_run`。

## 0.4.0-preview — 2026-08-29

- 产品展示名改为“科研决策 / Research Decision”；为兼容既有安装，技术标识仍为 `$research-exploration`。
- 默认回答改为自适应决策卡：一个条件化默认建议、关键依据、一个下一步行动及直接相连的继续/转向/停止/重访条件。
- 默认回答末尾提示可继续获得讲解、专家依据、方案比较或审计记录，不再强制展示六段报告和完整 Router。
- 信息不足时只问一个最高信息量问题；只有多个方案确实都可行时才展示方案对照。
- schema 保持 v3，新建状态使用 v0.4 标识，并兼容读取和更新同结构的 v0.3 状态。
- 私人真实案例仅用于本地内部开发验证；原始问题、输出、路径、未公开指标和私人文件不得进入可分发运行时或公开报告。
- 真人领域专家评审和真实学习迁移效果继续为 `not_run`。

## 0.3.0-preview — 2026-08-29

- 将公开来源支持的决策辅助从 AI/ML 扩展到数学与统计、计算机科学、物理与天文、化学与材料、工程、生命科学研究、地球与环境科学和理工科交叉研究。
- 为各领域增加真实任务、专家身份、来源层级、证据规则、失败模式、搜索模板和暂缓边界。
- 增加自适应解释层：`full`、`guided`、`faded`、`verification_only`。
- 完整解释增加小白版、当前案例、专业版、术语映射、易错点、3 个理解问题和 1 个迁移题。
- schema 升级为 3，新增 Learning Ledger、学习记录和决策解释摘要；v1/v2 保持只读且不自动迁移。
- 保持 D1–D29、Router 七字段和三种用户行动状态不变。
- 审计 Scientific Agent Skills、PaperQA2、Systematic Literature Review Skill、LLMTutor、Upstack 和本机相关 Skills，只借鉴产品机制并原创实现。
- 真人领域专家评审与真实学习迁移效果为 `not_run`。
- 本阶段允许验收后本地安装；不创建 GitHub 仓库或 Release。

## 0.2.0-preview — 2026-08-28

- 增加 AI/ML 实时专家经验检索、来源核验、用户初判对照和条件化行动状态。
- 将 29D 明确为非线性决策地图，而不是固定流程或静态答案库。

## 0.1.0 — 2026-08-25

- 首次实现 D1–D29 Router、状态、Trace、证据账本和七个方法适配器。

---

## English summary

Version 0.4 introduces the Research Decision display name and an adaptive decision card with optional evidence, explanation, alternative comparison, and audit layers. The technical slug remains `$research-exploration`. Human expert review and learning-transfer effectiveness remain `not_run`.
