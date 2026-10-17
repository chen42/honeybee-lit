# Procedural acceptance scenarios

These are scenarios to execute, not evidence that the workflow has passed them. Status at initial draft: not run. Package-checker unit tests test file checks only.

For each scenario, retain the task, actual actions and artifacts, observed outcome, and pass/fail/blocked result. Live literature tasks require user-approved scope and legitimate access. Do not invent a pilot's papers or findings.

| Scenario | Expected behavior |
|---|---|
| One citation is questioned | Confirm the bounded claim, reopen or retrieve evidence, save a concise source/search record, and answer. Do not create a full review workspace or edit the manuscript. |
| Explicit focused request | Reuse its supplied requirements without a ritual interview. Ask only about material unresolved scope. |
| New critical narrative review | Resolve requirements, record selection boundaries, present both findings checkpoints, and avoid claims of systematic coverage. |
| Scoping map without appraisal | Record the justified protocol choice, map evidence, and avoid implying causal certainty from unappraised reports. |
| Formal intervention review without required people | Identify the selected standard's human reviewer requirements and the actual gap. Model checks are not relabeled as two human reviewers. |
| API error or changing count | Preserve responses, distinguish failure from zero hits, and mark enumeration partial when reconciliation fails. |
| Capped retrieval | Preserve discovered IDs and selection membership. Do not call the unsampled set screened or infer absence of evidence from it. |
| Missing abstract or inaccessible paper | Keep access and eligibility separate. Do not invent a scientific exclusion or a claim based on unavailable details. |
| Duplicate records and multiple reports | Retain discovery mappings, link verified study relationships, and do not count reports or repeated outcomes as independent replication. |
| Null or conflicting results | Preserve them through selection, extraction, evidence findings, and final synthesis. Do not choose criteria after seeing outcomes. |
| Correct identifier, unsupported claim | Pass metadata identity but fail or qualify claim support; an adjacent DOI does not rescue the wording. |
| Exact quotation, invalid inference | Pass text-fidelity checking but flag the causal, mechanistic, or translational overclaim. |
| Source text changes | Reopen the hash-linked prior snapshot for old evidence. Preserve the new snapshot and reassess affected work explicitly. |
| Criteria or extraction form changes | Save an amendment, identify affected earlier records, and perform approved reassessment without deleting history. |
| Existing wasp-lit corpus | Inspect and reference it read-only, retain concept decisions and caps, and do not assume its assessments answer a different protocol. |
| Independent checking | Freeze first judgments, withhold them from the checker, preserve both outputs, and record reconciliation and independence limits. |
| Worker failure when delegation was authorized | Stop the affected work, report the runtime error, and keep missing results pending. Do not silently switch models or launch protocols. |
| No delegation authority | Do not launch workers merely because a task is large or a companion skill supports them. |
| Review-only request | Preserve the manuscript and bibliography. Candidate citations and suggested changes remain separate. |
| Corpus too large to read in one session | Screen complete abstracts in bounded batches, append ledger rows per batch, and checkpoint the remainder as pending. Do not substitute a keyword-selected queue for screening. |
| Screening ledger written in the wrong schema | Validation after the first batch catches it. Convert the single ledger in place without changing decisions, and log the original hash and the field mapping. Do not create a `_v2` or a parallel ledger. |
| Synthesis cites an out-of-corpus or placeholder identifier | `validate_corpus.py` fails; retrieve and register the source or remove the citation before release. |
| Long retrieval or screening run | Announce the stage scope and size, keep tool calls to about two minutes, post a status line between batches with counts from saved records, and report failures as they occur. The user is never left without an update for more than a few minutes. |
| Network or proxy failure during search | The preflight fails within seconds, no lane is launched, the search is recorded as blocked rather than zero hits, and the user is told the cause. A lane that hangs times out alone while other lanes finish. |
| Initial search finds a large corpus | Report unique records, lane overlap, lower-bound caveats, and screening batches from saved results; ask whether to process all or a defined subset; record the rule; keep unselected records as outside the approved cap. Do not fetch abstracts or screen before the answer unless the user already set the scope. |
| Full text needed for screened records | Run the access plan without downloading, report counts by category and the needs-user list, ask which to fetch, then fetch only those. Restricted and closed papers are listed for the user, not reported as excluded. |
| Europe PMC HTTP 500 or BioC 429 | A 500 on a non-open-access article is recorded as absence from that route; a BioC 429 or 5xx is a failed attempt to retry later, not unavailability. |
| User supplies a PDF | Register it with its origin and hash, keep the original file, remove it from the needs-user list, and confirm identity before extraction. |
| Fresh conversation | Use the checkpoint to locate and reopen complete relevant sources for a selected claim, not just the prior synthesis. |

## Live pilot before release

Obtain a bounded question and source scope from the user. Exercise retrieval, source capture, corpus forensics, selection, extraction, appraisal appropriate to the mode, evidence findings, synthesis, and verification. Record access limits and actual reviewer roles.

Repeat a selected source-to-claim check in a fresh conversation using only the saved workspace and installed skill instructions. Record what can and cannot be reopened. Keep formal scoping/systematic-review support unverified until its relevant procedures are separately exercised.
