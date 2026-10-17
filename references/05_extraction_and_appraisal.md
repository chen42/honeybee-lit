# 05. Extraction, study relationships, and appraisal

## Pilot a question-specific form

Start from [the extraction template](../templates/extraction-record.md), selecting fields needed to answer the approved question. Use design-specific fields rather than forcing every paper into an intervention-trial form.

Pilot the form on a bounded and varied set. Record definitions, controlled values where useful, missing-value conventions, and source precedence. If the form changes, version it and identify earlier records requiring re-extraction. Do not overwrite the original extractions.

Separate source transcription, methodological appraisal, and synthesis interpretation. An explicit null result differs from a missing result; not reported differs from a procedure known not to have been performed.

## Extract the evidence actually inspected

For each relevant experiment, outcome, comparison, and time point, record as applicable:

- Design, population or biological model, species, sex, age, recruitment, setting, and inclusion/exclusion rules.
- Biological, experimental, observational, and analysis units; independent sample sizes, repeated measurements, clustering, attrition, and exclusions.
- Exposure or intervention, comparator, dose, route, schedule, timing, duration, and relevant controls.
- Outcome definition, assay, tissue or cell type, measurement scale, and analysis.
- Reported effect estimate, uncertainty and interval type, units, denominators, test details, and multiplicity handling where supplied.
- Outcome-specific direction and target, explicit null findings, conflicting outcomes, and source limitations.
- Source identifier/hash, exact passage or table/figure locator, inspected evidence level, extractor/process, form version, and date.

Add domain fields when justified. For operant behavior, preserve reinforcement schedule, manipulandum, drug-delivery parameters, timeout, session structure, and the actual endpoint measured where reported. Intake, motivation, locomotion, withdrawal, and reinstatement are not interchangeable. For genetic evidence, distinguish locus association, gene assignment, expression, functional perturbation, and molecular mechanism; do not infer a causal gene from positional mapping alone.

Copy numbers and units faithfully. Do not fill absent methods, sample sizes, species, or cell types from memory. An abstract and full text can support different levels of detail. Keep their extraction records distinct and reconcile differences explicitly.

For missing values, use an explicit status such as `not_reported`, `not_applicable`, `not_checked`, `unavailable_source`, or `conflicting`, with a note where needed. Do not put a guessed value into a numeric field or silently treat unknown as zero.

Full-text extraction does not imply figures or supplements were inspected. Record needed material that was missing. If a claim depends on that material, keep it unresolved.

## Preserve outcome-level distinctions

Record direction against the specific measured variable and comparison. An increase in gene expression does not mean increased behavior. A partial pharmacological reduction does not establish necessity, specificity, or complete prevention.

One report may contain several experiments and opposing findings. Use separate finding records rather than a single positive/negative label. Multiple endpoints, time points, and analyses from one sample are not independent replications. Preserve the protocol's rules for selecting or grouping outcomes; do not choose the strongest result after inspection.

## Reconcile multiple reports

Use [Module 03](03_corpus_and_provenance.md) to link reports and studies. Retain secondary reports, abstracts, registry entries, supplements, and notices that add information. Preserve provenance for each extracted field.

When sources conflict, record both values and their locations. Apply the protocol's reconciliation rule or seek a methodological decision. Prefer a corrected value only after verifying the correction and its applicability. Do not silently choose the newest report, the largest estimate, or the most convenient source.

Flag overlapping cohorts and reused samples even when reports are not identical. Retain uncertainty about relationships. Study linkage is a scientific judgment, not a side effect of deduplication.

## Appraise at the appropriate level

Use [the appraisal template](../templates/appraisal-record.md). Select and verify an applicable tool and version, its instructions, target unit, and required reviewer process. Some judgments concern an outcome or result, not an entire study. Do not apply one paper-wide label to all findings without justification.

Keep these distinct:

- Risk of bias in the relevant result.
- Reporting completeness and unresolved information.
- Directness and applicability to the review question.
- Consistency, precision, and other body-of-evidence considerations where assessed.

Give domain-level judgments with rationale and supporting source locations. Follow a selected tool's own judgment rules rather than inventing a numerical aggregate. If no suitable tool is selected, provide a transparent methodological critique and label it as such, not a validated risk-of-bias score.

For a scoping review, follow the protocol's decision on whether appraisal is needed. Mapping unappraised evidence does not establish effectiveness or certainty. For narrative synthesis, a reasoned design critique is preferable to a fabricated universal quality score. If formal body-of-evidence grading is required, verify its framework separately; do not assign certainty from publication counts or average appraisal scores.

## Numerical and reviewer boundaries

Source transcription and bookkeeping counts can be performed within the review. New effect-size derivation, variance reconstruction, figure digitization, inferential calculations, or pooling require an explicitly authorized analysis task and reproducible methods, normally through `beaver-data`. Keep derived quantities separate from reported quantities.

Follow the approved reviewer arrangement. Where the chosen method requires independent human outcome extraction, retain that requirement and report gaps. Optional independent model checks are assistance, not a replacement for people required by the method. Preserve first extractions before reconciliation, as described in [Module 07](07_verification_and_delivery.md).
