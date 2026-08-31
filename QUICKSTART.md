# 快速开始 / Quick Start

## 直接提问

```text
$research-decision-skill

我正在研究：……
我已经做了：……
现在的结果：……
我犹豫的决定：……
现实限制：……
请先给我一个默认建议和下一步；如果我需要，再继续展开依据或讲解。
```

不需要提供 D 编号。最好给出已经观察到的结果、可选方向、你目前倾向的选择和可能改变选择的现实限制。

## 只要建议

```text
$research-decision-skill 请先给我当前最关键的科研决定、建议行动和改变决定的条件；解释保持简短。
```

默认回答后可以直接继续说：

```text
我没听懂，请把这个判断讲懂。
请展开专家依据。
请比较另外两个方案。
请显示这次决策记录。
```

## 要求完整讲解

```text
$research-decision-skill 请分两层解释：先用生活化语言和当前问题的具体例子讲懂，再用准确术语说明机制、边界和常见误解；最后给术语映射、3 个理解问题和 1 个迁移题。
```

## 状态初始化

仅在研究项目可写、且 `.research-decision/` 与旧版 `.research-exploration/` 都不存在时初始化：

```text
python -X utf8 <skill-root>/scripts/research_state.py init <project-root> --domain engineering --support-status public_source_decision_support_preview
```

用 `validate` 只读检查。schema v1/v2 不自动迁移。

---

## English

Describe the research goal, what you tried, the observed result, the decision you cannot make, and practical constraints. Add `$research-decision-skill` explicitly when you want guaranteed routing. Ask for a full two-layer explanation when teaching depth matters. You never need to supply a D number.
