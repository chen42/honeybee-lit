# 07. Verification, validation, and delivery

## Three separate citation checks

Use [the verification template](../templates/verification.md). For each added, central, or otherwise audited citation, record these checks separately:

1. **Identity:** Verify title, authors, publication venue, year, identifiers, and version against an appropriate authoritative database or publisher. Metadata agreement establishes identity, not support.
2. **Claim support:** Inspect the specific passage, result, table, or figure. Check design, population or model, exposure or intervention, comparator, outcome, timing, direction, and limitations against the statement being made.
3. **Publication status:** Check available publisher and bibliographic notices for corrections, retractions, withdrawals, or expressions of concern. Record the checked services, date, relevant notice identifiers, and limits of the check.

Use explicit results such as verified, unsupported, partially supported, not checked, or blocked, as appropriate to each check. Do not collapse them into a single verified flag. A notice search that finds nothing supports only that no relevant notice was found through those checked routes at that time.

If a notice changes an interpretation, preserve the original report and the notice, document the effect on claims and extractions, and apply the approved protocol. Do not silently replace sources or discard contradictory results. Verify a preprint's published counterpart and its claim support before substituting citations; publication can change results.

## Mechanical integrity and scientific support

Check that source files exist and hashes match; cited source versions resolve; quoted strings match the inspected source text; evidence and claim identifiers are valid; and imported decisions are complete for their assigned set. If the source was a PDF, link a quotation to its original page and the hashed text extraction used for matching. Parsing differences must remain visible.

Then assess whether the passage actually supports the finding and whether the design supports the interpretation. These are scientific checks, not consequences of a matching string or a valid schema.

Run `scripts/validate_corpus.py` from the workspace root before releasing a synthesis, for example:

```bash
python3 <skill-dir>/scripts/validate_corpus.py \
  --manifest references/literature-review/sources/manifest.json \
  --corpus references/literature-review/sources/abstracts.json \
  --screening references/literature-review/records/screening.tsv \
  --claims notes/claim-evidence-map.md --check notes/synthesis.md
```

It verifies manifest hashes and self-listing, flags cited identifiers absent from the registered corpus, fails unresolved placeholders such as `12345678-like` or `(?)`, validates the screening ledger, reports counts from explicit decisions, and flags excluded records cited as evidence. Register sources consulted outside the main corpus with an extra `--corpus` file rather than suppressing failures. Record the command and its output in the verification record. Fix or explicitly qualify every failure before delivery; a passing run establishes membership and integrity only. The bundled `scripts/check_skill.py` checks the skill package, not a review corpus.

Release condition: every empirical citation resolves to an inspected source in the review or an explicitly registered supporting source, each central claim has a saved supporting passage or table/figure location, and no unresolved placeholder appears as evidence. Details absent from the inspected source remain not established; retrieve the needed full text or narrow the claim.

## Reconcile the review flow

Maintain counts from saved records rather than reconstructing them from prose. Keep discovery records, deduplicated reports, study links, and query memberships distinct. An unresolved study relationship must not become a fabricated study count.

For each stage, account for the latest state of every unit under the applicable protocol. Count exclusions once using the primary reason. Keep pending, uncertain, access-blocked, and outside-cap records visible. Preserve original events but do not add superseded decisions into current counts.

Reconcile, as applicable:

- Reported search totals, enumerated identifiers, exports, caps, and retrieval discrepancies.
- Duplicate records and other removals before screening, with their reasons and mappings.
- Title/abstract screening, exclusions, advancement, uncertainty, and work not yet screened.
- Reports sought for full text, retrieved, not retrieved through checked routes, and still pending.
- Full-text assessments, inclusions, exclusions with reasons, and unresolved eligibility.
- Included reports, studies, overlapping samples, extractions, and appraisals.

Use the official flow diagram and definitions appropriate to a formal review. Keep database/register discovery and supplementary discovery traceable. A checklist or correctly balanced diagram does not by itself establish search completeness or valid selection.

## Independent checking

Implement the reviewer arrangement in the protocol. Distinguish required human reviewer work from optional model-assisted checks. Model-generated perspectives are not external peer review. Independent searches are not automatically required merely because independent screening or extraction is required.

For an authorized independent extraction or screening check:

1. Freeze first judgments and their source versions before comparison.
2. Give the checker the question, neutral criteria or form, exact sources, and required output, without the first judgments or target answers.
3. Record who or what performed the check, model/runtime if relevant, source access, rubric version, and actual independence limits.
4. Preserve both outputs, compare discrepancies, then adjudicate with the source and record the rationale.
5. Report unresolvable differences and the consequences for synthesis.

A second interface to the same source, repeated calls to the same model, and agreement among models cannot certify independent human review or exhaustive coverage. If agreement statistics or other inferential validation are requested, handle them as an approved analysis task rather than calculating them ad hoc.

## Method and reporting review

For a full review, assess the work against the chosen current conduct and reporting guidance. Record each governing source and version, required versus recommended items, evidence location, and pass, fail, blocked, or not-checked state. Do not call a package compliant when required reviewer roles, source access, or checks are missing.

Reporting guidance and conduct guidance have different purposes. Consult [the methodology register](methodology.md) and capture official sources for the actual task. The draft's notes are not an audit of a future review.

## Progress reporting

The user sees text only between tool calls. A single long command, such as one script that fetches hundreds of abstracts, leaves them without any update until it ends. Report progress as follows:

- **Announce each stage.** Before starting, give the stage, the unit and total (for example, 553 PMIDs in 6 batches of 100), the approximate duration if it can be estimated, and what will be saved where.
- **Bound each tool call.** Keep calls to about two minutes or less. Split retrieval into request batches, screening into ledger batches of 20 to 30 records, and extraction into a few reports per call. If a job must run longer and the runtime supports background execution, run it in the background with a log file, and read the log between status updates.
- **Post a status line between calls.** Use a fixed form: `[stage] done/total units; failures; elapsed; next step`, for example `[screening] 60/154 abstracts, ledger rows appended; 0 failures; 9 min; next batch 61-90`. Report failures and retries as they occur, not only at the end.
- **Run independent lanes in parallel.** Use `scripts/run_lanes.py` with a preflight check and per-lane timeouts ([Module 02](02_search_and_retrieval.md), Run lanes in parallel, fail fast) instead of a sequential loop inside one long command.
- **Make scripts report and persist.** Retrieval and processing scripts print one line per batch with counts and errors (flush output immediately), and write each completed batch to disk before starting the next. An interrupted run then loses at most one batch and its progress can be reconstructed from saved files.
- **Report stops accurately.** When pausing at a batch boundary, give the completed count, the pending count, where the checkpoint is saved, and the next permitted action.

A status line is navigation, not a completion claim. Counts in status lines come from saved records, using the same units as the coverage dimensions in [Module 03](03_corpus_and_provenance.md).

## Delivery and issue handling

Deliver only requested outputs: a bounded answer, synthesis, evidence table, methods/search record, verified candidate bibliography or export, review-flow record, and unresolved items as appropriate. Use Markdown unless another format is requested. Preserve an existing manuscript and reference library unless editing them is authorized.

State the deliverable's status: draft, checked within the stated scope, or incomplete/blocked. Name the source level and work not performed. Do not imply submission readiness from a literature answer or a successful file check.

For actionable review defects, provide location, scientific or procedural basis, severity, and a concrete correction or next check. Mark suggested wording or actions as suggestions until implemented. Escalate material methodological changes through a protocol amendment, not an unrecorded edit.

Before returning prose, check for unsupported facts, inflated claims, and artificial phrasing. Preserve unresolved queries rather than deleting uncertainty to make the output appear complete. If a continuing project is paused, use [the checkpoint template](../templates/checkpoint.md).
