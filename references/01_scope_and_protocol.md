# 01. Scope, requirements, and protocol

## Choose a bounded task

This skill is scoped to biomedical literature (clinical, translational, behavioral-neuroscience, human-genetic, and molecular-biology questions). State the scope limit when a request falls outside it rather than improvising a domain lane.

Inspect existing plans, files, and reference libraries. Infer the intended mode when it is clear and ask only about material uncertainty. A request to assess one citation does not authorize a review article, a new search platform, or changes to a manuscript.

For a focused task, confirm the claim or question, relevant model or population, search versus saved-source scope, and desired output. The user's explicit request can settle these decisions. Save consulted sources and a concise search or source-check record without building an entire project.

For narrative, scoping, and systematic reviews, establish a protocol proportionate to the requested method. For follow-ups, use [Module 08](08_resume_and_updates.md) before asking settled questions again.

## Requirements questioning

For a new review or material change, work through the unresolved decision frontier. Ask at most five independent questions per round, or one at a time when answers determine later choices. For each question, explain the methodological consequence, provide bounded options, and recommend one with a rationale.

Resolve these dimensions:

1. Scientific question, intended use, audience, and review type.
2. Biological entities, population or model, exposure or intervention, comparator if applicable, outcomes, and context. Use a question framework that fits; do not impose PICO on all mechanistic or exploratory questions.
3. Eligible designs, species, dates, languages, publication types, preprints, and source types. Distinguish gene-reference organism from the species providing evidence where relevant.
4. Databases and supplementary routes, subscriptions, available retrieval tools, retrieval budget, permitted local storage, and external-service constraints.
5. Screening and extraction roles, independent checking, automation authority, appraisal approach, synthesis outputs, and completion criteria.

Do not ask the user to supply facts that can be inspected locally or verified from official guidance. If a decision depends on unknown search behavior, propose a bounded pilot and obtain permission before carrying it out.

Use [the decision record](../templates/decision-record.md). Record a recommendation as proposed until the user confirms it. Approval governs methods and scope, not which empirical findings are acceptable.

## Protocol gate

Use [the protocol template](../templates/protocol.md). Before the main search for a full review, confirm:

- The question, scope, eligibility criteria, and exclusion-reason hierarchy.
- Search sources, supplementary discovery, restrictions, query-calibration plan, and stopping rules.
- Deduplication and study/report linkage rules.
- Screening stages, treatment of uncertain cases, reviewer roles, and adjudication.
- Extraction fields, pilot procedure, source-conflict rules, and appraisal methods.
- Synthesis groupings, handling of heterogeneous and overlapping studies, and analysis boundaries.
- Reporting guidance, registration requirements if applicable, deliverables, and definition of done.
- Permissions and known unresolved constraints.

A pilot can precede the final protocol only within an expressly approved scope. Label pilot discoveries and any later use in the main corpus. After calibration, freeze the confirmed protocol and exact search strategies. Do not describe a post-hoc protocol as prospectively specified.

A locally saved protocol is not registration. Obtain separate authority before contacting investigators, submitting registrations, creating accounts, accepting terms on the user's behalf, or transmitting material to external services.

## Review-type distinctions

A critical narrative review may use purposive selection, but must say how sources were found and selected. State its boundaries without implying full ascertainment.

A scoping review maps evidence according to an approved question and charting plan. Decide whether critical appraisal serves the objective, and report whether it was performed. Do not imply that unappraised studies establish treatment effectiveness or causal certainty.

A systematic review uses predefined eligibility and systematic identification and selection methods appropriate to its question. Choose conduct guidance separately from reporting guidance. Inspect the current official requirements instead of treating one default protocol as valid for every design. Document deviations rather than concealing them behind a completed checklist.

Where Cochrane intervention-review conduct is selected, the inspected guidance requires at least two people independently making final eligibility decisions and independently extracting outcome data. A model is not an additional human reviewer. If the required people or access are unavailable, report the unmet method and agree on a preliminary or explicitly modified workflow, without claiming full compliance. See [the methodology register](methodology.md).

## Workspace and permissions

Preserve an existing layout and reference manager. New research artifacts may use `references/literature-review/` for corpus materials and existing plan, notes, review, and log directories for outputs. Create only directories needed by the task. Do not store research corpora inside the installed skill.

Read-only Git inspection is permitted. Before any Git mutation, detect the repository root, inspect task-related status, and obtain approval. Do not demand a globally clean tree or include unrelated files. Versioned protocol and run manifests can preserve lineage when Git changes are not authorized.

Ask before software or skill installation, environment changes, project reorganization, external uploads, or out-of-scope edits. An existing manuscript or bibliography stays unchanged during review-only work. Preserve originals and write requested exports separately.

## Amendments and continuing work

Proceed within approved criteria without requesting confirmation for every paper or batch. Reopening a source requires no new protocol. A new question, eligibility restriction, database, sampling rule, or consequential change to extraction or appraisal needs a dated amendment with its rationale and affected records. Follow [Module 08](08_resume_and_updates.md).
