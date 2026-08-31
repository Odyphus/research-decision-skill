# Good interaction examples

These are synthetic demonstrations of the Preview contract, not evidence that the product improves research decisions. A real run must search and revalidate sources at use time. Full source metadata and Router records belong in the ledger or an on-request audit view, not in the ordinary answer.

## 1. Repeated patients and a tempting headline number

**Request:** “We have several visits per patient. A random visit split gives AUC 0.94, while a patient-held-out split gives 0.68. I planned to lead with 0.94. Is that reasonable?”

**验证后推进：如果你的主张是预测未见过的新患者，应以患者隔离结果为主要结果，不要用随机访视划分的 0.94 支撑该主张。**

**判断依据**

- 你现在的选择把“同一患者的新访视”和“全新的患者”当成了同一个问题；决定性线索是主张单位必须与数据划分单位一致。
- [scikit-learn 的数据泄漏与分组划分说明](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)和[相关同行评议研究](https://doi.org/10.1016/j.patter.2023.100804)都支持在训练与评估之间隔离会泄露目标信息的分组。它们支持这一评估原则，但不能替你决定最终部署人群。

**下一步**

先声明目标人群和预测时点，核验训练、调参与测试之间没有患者重叠，再重跑与该主张匹配的划分。如果目标确实是预测已知患者的后续访视，可以保留 0.94，但必须把主张缩小到这一情境；如果目标是新患者，则继续使用患者隔离或更合适的时间/外部验证，重叠无法排除时停止作泛化主张。

如果你想继续，我可以把患者级泄漏检查整理成一份短清单。

## 2. A paper is relevant but does not reveal a decision

**Request:** “I found one paper using a similar architecture, but I have not yet stated exactly what contribution our comparison should isolate. Tell me how experts would choose our baselines.”

**暂缓定论：先明确你要证明的贡献和成功标准，再冻结基线集合。**

**判断依据**

- “架构相似”只能说明论文相关，不能说明其作者面对的是同一个比较决策；基线必须能够排除对你的核心贡献最有威胁的替代解释。
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)要求主要结果包含合适基线并披露训练细节与不确定性，但不会替具体项目指定基线，因此不能把一篇相关论文写成专家共识。

**下一步**

先用一句话写出“新方法相对什么改变了什么”，再据此检查三类候选：简单 sanity baseline、可公平运行的最强同任务方法、移除核心贡献的消融。如果贡献或资源约束变化，就重选；如果找不到可比实现，不要用不对称比较支撑优越性主张。

如果你愿意，我可以根据你的贡献主张帮你压缩成最小基线表。

## 3. Current verification is unavailable

**Request:** “The network is unavailable. Based on last year's notes, should we claim that experts now agree with our benchmark design?”

**暂缓定论：现在不要写“专家已经达成共识”。**

**判断依据**

- 去年的笔记只能帮助恢复检索，不能证明来源现在仍有效，也不能证明多个独立专家对当前设计作出了同一判断。
- 当前无法核验来源身份、适用范围和反对意见，因此“专家共识”明显强于现有证据。

**下一步**

先把基准设计标为暂定，并列出尚未核验的假设。联网恢复后，至少核验一个权威方法来源和一个独立的任务相关来源，并主动查找分歧；只有它们直接支持同一情境下的判断时才重新考虑共识表述，否则继续使用更窄的措辞。

如果需要，我可以先把旧笔记整理成联网后的核验清单。

## 4. Correct negative non-trigger

**Request:** “Reformat these five already-approved citations as APA 7; do not evaluate the sources.”

**Response:** Perform the bounded formatting task. Do not initialize research state, route through D1–D29, or run expert-experience search. If useful, state once that formatting does not independently verify the sources.
