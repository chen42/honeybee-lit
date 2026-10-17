# 04. Eligibility screening and optional workers

## Prepare the screening process

Read the approved protocol and corpus-forensics report. Resolve material identity and retrieval defects before relying on affected records. Use [the screening template](../templates/screening-record.md), with stable criterion identifiers and a defined reason hierarchy.

Pilot the criteria on a bounded mix of apparently eligible, ineligible, and uncertain reports. Clarify ambiguous criteria before the main screening run. If a pilot changes eligibility, record the amendment and reassess affected earlier decisions. Do not tune criteria to retain only studies with preferred outcomes.

Set reviewer roles and adjudication before screening. Follow the chosen design-appropriate conduct guidance. Where independent human reviewers are required, model calls cannot substitute for them. If the arrangement is unavailable, label model screening as preliminary or assisted and report the unmet requirement.

## Title and abstract stage

Read the complete available abstract, not just a title, search snippet, lexical match, or previous summary. If tool output truncated the abstract, read the rest before deciding. Use these stage-specific decisions:

- `advance`: Potentially eligible; needs the next selection stage.
- `exclude`: Fails a specified approved criterion on the available evidence.
- `uncertain`: Identity or eligibility cannot yet be resolved.

A missing abstract is not automatically an exclusion. Advance to another legitimate source or retain the unresolved state. Do not infer species from a gene identifier, model from the journal, or mechanism from the search vocabulary.

For a focused or explicitly abstract-bounded narrative task, the protocol may omit full-text selection. State that inclusion is limited to that task and evidence level; it does not establish full-text eligibility or appraisal.

## Full-text stage

Retrieve and inspect the relevant report and linked supporting reports, including methods, results, tables, and supplements needed to assess eligibility. Record what was actually available. Use `include`, `exclude`, or `uncertain` for the specified unit and criterion set.

Keep a report not retrieved separate from a full-text eligibility exclusion. Unknown eligibility remains unresolved or awaiting classification. Failure to extract a usable effect estimate does not itself make an otherwise eligible study ineligible. Distinguish an outcome not measured from a measured outcome whose results were not reported.

An exclusion must name the approved criterion and source basis. For inclusion, record the passages establishing relevant eligibility. If an exclusion depends on absent reporting, identify the sections checked and what remains unknown; do not invent a quotation proving an absence. Preserve exact text when quoting, including punctuation and scientific notation.

Separate scientific eligibility from whether a report is useful for background, methods, or a comparison. Background sources may inform context but must not appear as included primary experiments. Retain excluded records for audit, not as hidden support for the review's empirical conclusions. A criterion or purpose change needs explicit reclassification with history preserved.

## Decision ledger

Record every title/abstract and full-text decision as one appended row in `records/screening.tsv` (or `screening.jsonl`). Required fields: `record_id`, `stage` (`title_abstract`, `full_text`, or `abstract_bounded`), `decision` (`advance`, `include`, `exclude`, `uncertain`), `reviewer_id`, and `timestamp`. Also record `primary_reason_id` for every exclusion and a `passage_locator` where practical; add `source_id`, `source_hash`, `rubric_version`, and `note` columns as needed. Never edit or delete earlier rows; a later row for the same record and stage supersedes the earlier one.

Screen in bounded batches of about 20 to 30 complete abstracts, appending each batch's rows and posting a status line (records done/total, decisions so far, next batch) before reading the next. When a corpus is too large to read in the available session, stop at a batch boundary, record the remaining records as pending in the checkpoint, and continue later or ask for a scope decision. Do not substitute ranking, keyword matching, or snippets for the remaining decisions.

Generate screening counts from the ledger, for example with `scripts/validate_corpus.py --screening`, never from memory or prose. A record with no row is pending, not excluded. Use [the screening template](../templates/screening-record.md) for adjudicated, contested, or full-text decisions that need a longer rationale, and reference it from the ledger row.

## Decisions and adjudication

Record report and study identifiers where established, stage, criterion/rubric version, reviewer or model process, source/hash, decision, criterion, rationale, passage or locator, date, and unresolved items. For exclusions, choose one primary reason using the approved hierarchy; retain additional reasons as notes rather than double-counting exclusions.

Freeze independent judgments before reconciliation. Compare disagreements against the source and protocol. Record original decisions, adjudicator or resolution process, final outcome, and rationale. Do not erase disagreement or treat majority model agreement as ground truth.

A null result, unfavorable direction, small effect, poor reporting, or publication notice is not an improvised exclusion rule. Apply pre-agreed criteria and appraisal procedures, and record any necessary amendment. Preserve scientifically relevant contrary findings.

## Automation boundaries

Ranking and lexical annotation can prioritize reading within the approved workflow. They cannot silently exclude records or turn a cap into scientific screening. A keyword-selected queue is a prioritization output, not an included set; label it as such in file names and reports. Do not claim that records were screened or read when only titles, snippets, or truncated output were inspected. If a formal protocol proposes automated exclusion or a stopping rule, verify its methodological basis and authorization first, and report validation and records affected. This draft supplies no validated automatic-exclusion method.

## Optional authorized workers

Use workers only when the user or an applicable instruction authorizes delegation. This skill is not such authorization. Consult the runtime's current worker instructions before launch; do not assume an installed agent or model is available.

The coordinator owns planning, retrieval, corpus writes, scientific reconciliation, and synthesis. Workers read bounded local source packets and return structured screening or extraction results. They do not retrieve, edit the corpus, launch children, or make unapproved methodological changes.

Each packet identifies the question, protocol and rubric, assigned report/source identifiers and hashes, complete source text or accessible source paths, and output contract. Bound packets by context size without truncating sources. Do not attach prior judgments to a task intended as an independent model check.

Before import, check assigned versus returned identifiers, duplicates, omissions, schema and allowed decisions, counts, source versions, passage fidelity, and actual runtime provenance. Mechanical checks do not establish scientific support; the coordinator must review interpretation. A missing or failed result remains pending, never excluded.

On launch or execution failure, stop the affected work, preserve completed outputs and pending assignments, and report the error and runtime identifier. Do not silently change models, execution protocols, or permissions. Keep completion, provider availability, and model verification distinct.
