---
name: honeybee-lit
description: Plan and conduct biomedical literature reviews, from focused evidence questions and citation checks to critical narrative, scoping, and systematic reviews. Use for protocol design, reproducible PubMed and Europe PMC searches, GWAS Catalog association lanes, persistent abstract/full-text corpora, eligibility screening, evidence extraction and appraisal, source-linked synthesis, or review updates. Complements wasp-lit, beaver-data, and weaver-text without replacing their specialized workflows.
metadata:
  version: "0.1.0-draft"
---

# Honeybee lit

Answer scientific questions by collecting, appraising, and synthesizing literature. Preserve the evidence behind the answer so another conversation can reopen it. A synthesis is a derived interpretation, never a replacement for an abstract, paper, or extraction record.

## Select the task

Scope: biomedical literature only, including clinical, translational, behavioral-neuroscience, and human-genetic evidence. A non-biomedical question (materials, physical chemistry, computing, astronomy, or a social-science topic unrelated to health) is out of scope; state the boundary and offer to hand off or defer rather than stretching the vocabulary lanes.

Choose the smallest scope that meets the request:

- **Focused question or citation check:** Resolve a bounded question or assess a specified claim. Save consulted evidence and a brief search record; do not scaffold a full review.
- **Critical narrative review:** Document the question, search boundaries, selection approach, extraction, and appraisal. Synthesize critically without claiming systematic coverage.
- **Scoping review:** Map the types, characteristics, and distribution of evidence using an approved protocol. Decide whether critical appraisal is appropriate to its objectives; do not require it merely because this skill also supports systematic reviews.
- **Systematic review:** Use an approved protocol, design-appropriate conduct methods, and the applicable reporting guidance. Identify required human review roles and unmet methodological requirements before substantive work.
- **Follow-up or update:** Reopen the approved context and relevant original sources. Distinguish an in-scope question from new retrieval or a protocol amendment.

Do not relabel a capped, selectively retrieved, or incompletely screened corpus as a completed systematic review. A review may be systematically conducted but lack eligible studies or data for meta-analysis; meta-analysis is not a prerequisite for systematic review.

This draft provides instructions and templates, not a retrieval application or validated corpus engine. Formal review procedures require task-specific verification and actual execution; loading this skill certifies neither method compliance nor scientific completeness.

## Essential rules

- Never invent references, search results, source passages, methods, sample sizes, estimates, or review decisions. Verify citation identity through appropriate authoritative records. Use `[REVIEW QUERY: ...]` for unresolved information.
- Inspect the existing workspace first. Keep research artifacts outside this skill directory, preserve the existing library and document formats, and create only needed folders.
- For a new review or material amendment, resolve active requirements and obtain confirmation before the main search or new selection rules. Ask at most five independent questions per round and recommend justified options. A sufficiently explicit focused request can supply the scope and authority; do not repeat settled questions.
- Preserve retrieved sources unchanged, including complete abstracts, structured sections, source responses, and accessible full texts. Record provenance, access level, and checksums. Retain retrieved excluded records and their decisions for audit. Known but unretrieved records remain explicitly unretrieved.
- Keep discovery, enumeration, retrieval, abstract availability, screening, full-text access, extraction, and appraisal as separate coverage dimensions. Failed requests are not zero hits; missing sources are not scientific exclusions.
- Distinguish discovery records, bibliographic reports, studies, and source versions. Multiple queries, papers from one study, and an abstract plus its full text are not independent replication.
- Apply approved eligibility criteria consistently. Keep uncertain, null, and conflicting findings. Keyword matches and machine rankings may prioritize work but must not silently become exclusion rules or a screened set. Record decisions in an append-only ledger, in bounded batches of complete abstracts; unread records stay pending.
- Tie findings to the inspected source version and an exact passage or table/figure location. Preserve quotations verbatim. A matching quotation establishes fidelity, not scientific support.
- Present a corpus-forensics report before substantive screening, then an evidence-findings report before full synthesis. For focused tasks, perform and report the relevant checks briefly rather than creating separate reports.
- Match interpretation to design, measured outcomes, model, and controls. Distinguish observation, association, perturbation, prediction, mechanism, and inference. Do not rank evidence by publication counts or vote-count statistical significance.
- Verify citation identity, claim support, and publication notices separately. Record the scope, source, and date of each check; an incomplete check cannot establish the absence of notices.
- Keep the user informed during long work. Before a stage, state its scope and expected size. Split retrieval, screening, and extraction into tool calls of about two minutes or less, and post a one-line status between them, so the user is never left without an update for more than a few minutes. Long-running scripts print per-batch progress and save results incrementally. Run independent search lanes in parallel with `scripts/run_lanes.py`, after a fast connectivity preflight and with a timeout per lane. See [Module 07](references/07_verification_and_delivery.md), Progress reporting.
- Use legitimate access and respect rate limits. Retain authorized local copies for the user's use, with restrictions recorded. Do not bypass access controls, expose credentials, redistribute sources, or upload protected material without permission and suitable rights.
- Review does not authorize edits to an existing manuscript or bibliography. Obtain permission before installations, environment changes, Git mutations, project reorganization, or out-of-scope scientific changes. This skill does not independently authorize subagent delegation.

## Workflow and decision gates

| Stage | Required action | Proceed when |
|---|---|---|
| Scope | Confirm question, review type, criteria, authority, and outputs. | Material requirements are settled; a full review has a confirmed protocol. |
| Search | Calibrate queries, save exact strategies, retrieve sources, and record coverage. | Main-search methods are approved; failures and limits are visible. |
| Corpus forensics | Report duplicates, missing sources, identity conflicts, and retrieval defects. | Material repairs or an explicitly bounded continuation are agreed. |
| Screening | Apply the frozen criteria; record decisions and unresolved cases. | The applicable selection stage is settled or remaining work is explicitly incomplete. |
| Extraction and appraisal | Pilot forms; preserve source-linked findings and design-appropriate judgments. | Evidence needed for the proposed synthesis is available, with missing work identified. |
| Evidence findings | Present the evidence matrix, conflicts, null findings, appraisal concerns, and answerable scope. | The synthesis scope is confirmed for full reviews; empirical findings are not subject to user preference. |
| Synthesis and verification | Write by scientific question, audit claims, and reconcile the review flow. | The requested checks are done or outstanding checks are explicitly reported. |
| Handoff | Deliver requested outputs and save a checkpoint for continuing work. | Status, provenance, and unresolved items are clear. |

Do not create unnecessary approval loops. Continuing an approved batch, reopening a source, and applying frozen criteria need no new confirmation. A consequential change requires an amendment, not silent drift.

## References by task

Resolve bundled paths relative to this skill directory. Load only the relevant modules; module numbers are not a mandatory sequence for small tasks.

| Task | Reference |
|---|---|
| Requirements, task modes, protocols, permissions | [01: Scope and protocol](references/01_scope_and_protocol.md) |
| Search strategy, pilots, retrieval tools, full-text access | [02: Search and retrieval](references/02_search_and_retrieval.md) |
| Source capture, records, deduplication, coverage, forensics | [03: Corpus and provenance](references/03_corpus_and_provenance.md) |
| Eligibility, decision ledger, adjudication, optional authorized workers | [04: Screening](references/04_screening.md) |
| Extraction, study relationships, appraisal | [05: Extraction and appraisal](references/05_extraction_and_appraisal.md) |
| Evidence-findings report, synthesis, scientific prose | [06: Synthesis and claims](references/06_synthesis_and_claims.md) |
| Citation checks, validation, review flow, deliverables | [07: Verification and delivery](references/07_verification_and_delivery.md) |
| Resume, updates, amendments, wasp-lit corpus reuse | [08: Resume and updates](references/08_resume_and_updates.md) |
| Methodological sources and limits of the draft's verification | [Methodology register](references/methodology.md) |

Use the linked templates in each module. Leave fields explicitly unresolved rather than filling them from inference or an example.

## Companion boundaries

- Use an installed retrieval skill or an authoritative interface for live access. Confirm availability and read its instructions; do not assume optional connectors are installed.
- Keep `wasp-lit` as the specialized gene-to-phenotype workflow. Reuse its saved corpus read-only through an explicit mapping. Its concept caps and full-text quotas do not establish systematic coverage.
- Hand approved effect-size derivation, quantitative synthesis, meta-analysis, and statistical diagnostics to `beaver-data`, with a separate analysis plan. Copy reported estimates faithfully; do not reconstruct missing results during prose synthesis.
- Use `weaver-text` for requested manuscript or grant integration, editing, review, and submission production; for those deliverables, read its scientific-prose module before drafting or revising. Do not convert formats or alter an existing document just to deliver a literature answer.

## Completion check

Before releasing a synthesis or note that cites sources, run `scripts/validate_corpus.py` on the workspace and fix or explicitly report every failure; it checks membership and integrity, not support. Verify that empirical claims resolve to inspected sources, evidence level is stated, conflicting findings are represented, and conclusions fit the review's scope. Check editable prose for unsupported additions and artificial phrasing. Report what was not retrieved, screened, extracted, appraised, or checked. Do not describe an instruction-only draft, a model-generated review, or a completed reporting checklist as independent expert validation.
