# 08. Resume, updates, amendments, and corpus reuse

## Checkpoint

Use [the checkpoint template](../templates/checkpoint.md) when pausing a continuing review. Record the review question and mode, approved protocol/version, active run, corpus and source locations, accepted outputs, coverage, unresolved decisions, blockers, and next permitted action.

A checkpoint is a navigation aid. It does not replace a source record, full abstract, or evidence table. Store it in the project's existing logs or notes, outside the skill installation. Do not promise that a future conversation will remember the chat automatically.

## Reopen a review

1. Read the context, latest checkpoint, confirmed decisions, protocol, and amendments.
2. Inspect coverage and unresolved work before answering a new question.
3. Identify the reports and evidence records relevant to that question.
4. Reopen complete relevant abstracts and the full-text passages, tables, figures, or supplements needed for the claim.
5. Verify hashes and source versions against the assessment being reused. If they fail, recover the original or mark dependent work unresolved.
6. Save the dated answer or synthesis with source/evidence references and the scope of new checks.

Use bounded packets when the corpus exceeds context limits. A packet contains the question, protocol, report and study links, complete relevant abstracts, exact source references and hashes, relevant assessments, and coverage limitations. Bound the number of records rather than silently truncating each source. Read additional slices or smaller packets when tool limits intervene.

A previous synthesis can guide navigation but is not evidence. Do not cite an earlier assistant answer as if it were a primary study. A source update does not retroactively alter the text that supported an old assessment.

## Distinguish follow-up from amendment

An in-scope question that reuses existing sources and approved criteria can proceed without a new interview or search. State any source limitations relevant to the new question.

A new outcome, population, eligibility rule, database, search cap, exclusion strategy, extraction field affecting interpretation, or appraisal method can change the evidence base. Record a dated amendment using [the decision record](../templates/decision-record.md), with:

- Prior and proposed scope or method.
- Scientific rationale and when the need was identified.
- Options and trade-offs, including the recommended choice.
- Actual user confirmation or unresolved decision.
- Affected searches, reports, screening decisions, extractions, appraisals, and claims.
- Rework needed and which previous outputs are superseded or still usable.

Keep old protocol and evidence versions. Mark exploratory additions honestly; do not rewrite them as prospective decisions. A substantial new question may need its own linked review context rather than an increasingly ambiguous corpus.

## Update searches

Use a new run identifier for an update. Specify databases, exact strategies, search interval, date-field interpretation, indexing-lag considerations, overlap with the earlier search, and any changed tools or methods. Record the rationale for the overlap; there is no universally correct fixed interval.

Retain all discovery memberships and use approved deduplication to identify genuinely new reports. Reassess changed abstracts or corrected full texts against their new snapshots. Search changes need a recorded amendment; fresh retrieval under unchanged methods still needs its own provenance.

Report additions, corrections, newly available full texts, changed eligibility, altered extraction or appraisal, and consequences for earlier claims. Do not silently replace an earlier synthesis. Dynamic databases can change counts or indexing; saved methods and snapshots support reproducibility, not identical future results.

## Reuse a wasp-lit corpus without changing it

If the user supplies a `wasp-lit` workspace, inspect its manifest, context, run records, membership, articles, source responses, assessments, full texts, and coverage views before use. Read the installed wasp-lit instructions and relevant resume guidance. Do not assume every workspace uses the same schema version or that a CLI command is available.

Keep the wasp-lit corpus read-only unless modification is separately requested. Honeybee can reference it directly or create a derived manifest in its own workspace, recording the source corpus path/version, source identifiers/hashes, mappings, and limitations. Any copied source must retain provenance and access restrictions.

Preserve gene/concept membership, rubric context, phenotype relevance, evidence-species scope, null and conflicting findings, and the exact source version behind each assessment. A concept-level decision is not automatically a global eligibility decision for a different review question. Previously excluded or unresolved records require explicit reassessment if the new protocol makes them relevant.

Preserve abstract-selection caps, complete versus partial enumeration, unassessed concepts, missing sources, and the full-text quota. Full PMID enumeration does not mean all abstracts were read, and screening one concept does not complete all others. Wasp's specialized association lane is not a generic requirement for every Honeybee question.

Do not launch workers, refresh sources, migrate schemas, or write to Wasp merely to inspect it. A new retrieval or re-screening request follows the applicable skill's authorization and workflow.

## Recovery after interruption

Verify the latest durable source and event records before resuming. Preserve successful work and identify unfinished writes or batches. Do not assume transactional or locking guarantees that the chosen storage tools do not provide. One coordinator writes the corpus at a time.

Resume only the pending work under the approved scope, with a new event or run where appropriate. Report corrupt or inconsistent records and obtain a decision before destructive repair. Never discard a failed run merely to make the coverage summary look complete.
