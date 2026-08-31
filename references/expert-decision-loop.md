# Expert decision loop

This is a mandatory cross-cutting stage for every substantive decision inside a supported STEM domain. It is not an eighth method adapter and must not be skipped because a D ID or method module already looks obvious. Load the selected [domain pack](domain-scope.md) before forming search terms or judging source authority.

The purpose is to recover decision-relevant public experience for the user's actual situation, not to collect impressive citations. Search and feedback happen inside one decision cycle: locate the decision, find and verify relevant judgment, compare it with the user's current judgment, revise the decision, and record what should transfer to the next case.

## 1. Decide whether the stage is required

Run this stage when the answer can change a research question, hypothesis, theoretical commitment, dataset, split, baseline, experiment, analysis, interpretation, claim, resource commitment, or continue/pivot/stop choice.

Do not run it for a genuinely mechanical lookup, formatting operation, translation, or implementation task whose research assumptions and acceptance criteria are already settled. If wording changes the question, claim, scope, estimand, interpretation, or treatment of a failure, the task is substantive.

An immediate authority, ethics, safety, privacy, license, or data-rights gate may stop the restricted action before browsing. If a scientific recommendation is still requested, complete the search only within that gate and do not use it to bypass the restriction.

## 2. Capture the user's current judgment

Before evaluative feedback, ask the user to make an observable choice and give a concise reason whenever the interaction permits it. Accept an already stated choice and reason; do not ask again.

- Ask at most one question that would materially change the search or choice.
- When the user is stuck, offer two or three concrete alternatives and ask which signal matters most.
- When the user explicitly asks for a direct answer, or when a safety boundary requires immediate direction, provide a source-grounded provisional recommendation first. Still show the decisive cues and invite the user to confirm or revise it.
- Never infer ability, seniority, or lack of experience from silence.

Record the initial judgment if state is writable. Do not invent one when it was not provided.

## 3. Turn the decision into a search brief

State a compact brief containing:

- the live decision and the alternatives it must distinguish;
- domain and subfield, task, relevant system/model/observable, data or proof regime, evaluation setting, and research context;
- user constraints that can reverse the recommendation;
- decision-changing claims and the expected counterevidence;
- date sensitivity and the retrieval time;
- inclusion, exclusion, coverage, and stopping rules.

Search terms should target public judgment, not just topic similarity. Combine the technical object with terms such as protocol, checklist, reporting guidance, ablation, failure analysis, benchmark practice, lessons learned, position, recommendation, or decision criteria as appropriate.

## 4. Search live and build enough coverage

Use whichever current web or academic search capabilities are available. Do not depend on a named plugin, database, or MCP server. Historical ledger entries may seed queries, but they never replace a new live identity, access, applicability, and recency check.

Prefer, in order appropriate to the claim:

1. authoritative standards, formal guidance, reporting checklists, benchmark or dataset documentation, and reproducible protocols;
2. primary papers and supplements that explicitly expose decision criteria, design rationale, failure conditions, or lessons from practice;
3. materials from identifiable research teams, formal expert reports, and well-scoped technical retrospectives;
4. reliable technical writing or recorded talks by people whose relevant role and expertise can be verified.

Social posts, aggregators, mirrors, snippets, and AI summaries are discovery aids, not judgment anchors.

For a decision-changing claim, normally seek at least two genuinely independent qualified anchors. A single source may suffice only when it is the controlling authoritative standard and its scope clearly matches the case. Otherwise a single-source result cannot be `可直接推进`.

Coverage is adequate only when it includes the strongest accessible support, a plausible counterposition or boundary case, and the source types most authoritative for the decision. Stop when additional qualified independent sources no longer change the option set, decisive cues, applicability boundary, or disagreement map—or when the user's declared budget ends. A budget stop with material gaps must remain visible.

## 5. Verify before extracting judgment

For every candidate source, verify:

- identity: author or issuing body, title, date, stable locator, and source type;
- relevant expertise: the source author's or body's role is connected to this exact decision, not merely general prominence;
- professional relevance: the source addresses the same or a transferable task and decision;
- applicability: population, data regime, model class, scale, resources, assumptions, and intended use;
- timeliness: current enough for claims that can drift, or explicitly historical where appropriate;
- independence: canonical work, artifact, study, dataset, team, and shared pipeline are not being double-counted;
- claim support: the cited passage or artifact actually supports the extracted judgment.

For each decision-changing passage, inspect the sentence or result together with its limiting sentence, uncertainty statement, and scope. Preserve “insufficient to determine” and equivalent caveats; do not promote a tentative signal into a confirmed bias, mechanism, effect, or consensus.

An ordinary research paper is technical evidence, not automatically a record of expert judgment. Treat it as expert-experience-bearing only when it makes observable decision criteria, rationale, predictions, tradeoffs, failure signals, or practice recommendations available. Never manufacture a personal view from authorship alone.

## 6. Extract observable judgment, not private reasoning

For each qualified anchor, record only what can be audited:

- cue or situation noticed;
- options considered or implied;
- recommendation or choice;
- stated public rationale;
- prediction or expected observation;
- tradeoff and cost;
- failure, stop, or reversal signal;
- applicability and exclusions;
- agreement or conflict with other qualified sources.

Paraphrase concisely and cite a precise locator. Do not claim access to hidden deliberation or expose hidden chain-of-thought. Separate direct source statements from the Skill's synthesis and inference.

## 7. Compare, give feedback, and revise

Compare the user's initial judgment with the verified source-grounded judgment on the decisive cues, not on status or authority.

- Name what the user's judgment already handles well.
- Identify the most consequential omitted cue, unsupported assumption, or mismatched condition.
- Preserve legitimate alternatives and disagreements.
- Recommend one decision only within the conditions actually supported.
- Ask the user to confirm or revise when the interaction permits; record the revised decision or `[UNKNOWN]`.
- Extract one or two transferable principles stated as conditional rules, not slogans.

On later similar cases, reduce scaffolding only when earlier records show that the user is already applying the relevant cues. Continue to expose sources, disagreement, conditions, and reversal signals. Fading removes prompts, not evidence standards.

## 8. Assign the action status

Use exactly one user-visible status:

- `可直接推进`: the applicable evidence and public expert judgment are sufficiently convergent, no critical gate remains, and the proposed action is bounded and reversible where needed;
- `验证后推进`: the direction is supportable, but one or more named uncertainties can change the choice and must be checked first;
- `暂缓定论`: live verification cannot currently support a domain judgment, critical sources conflict without a defensible condition split, or a gate or missing premise prevents a responsible choice.

These statuses describe what the user can responsibly do next. They do not certify that a scientific claim is true or that the product has been validated by human experts.

If live access is unavailable, say that current source verification could not be completed and limit the output to a decision frame and retrieval plan. Do not imply that the absence of verified material proves novelty, consensus, or lack of expertise.

## 9. Persist and return

When valid schema-v3 state is writable, append the search run and expert judgment records, record explanation support when it is shown, then commit the decision cycle. The expert-experience ledger records retrieval time, verified locators, source identity, extracted judgment, applicability, independence, and conflicts. The learning ledger records observed understanding and transfer without inferring either from silence. Evidence used in the seven-field Router object still contains only valid Evidence Ledger IDs.

If search reveals route-changing evidence, return to the Router before recommending. If state is absent, legacy, corrupt, concurrently changed, or read-only, provide the same bounded assistance in read-only form and report the project-level write blocker.

Only persisted schema-v3 records have stable `search_run_ids`, `expert_judgment_ids`, or `learning_record_ids`. When no validated append succeeded, use `[UNKNOWN]` in prose and do not invent IDs; author names, paper titles, URLs, and ad hoc labels are never record IDs.
