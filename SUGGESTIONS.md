# Honeybee-lit review and suggested improvements

Date: 2026-10-17
Scope: installed honeybee-lit 0.1.0-draft, its eight workflow modules, methodology register, all templates, package checker, tests, and saved CACNA1C, CACNA1D, and zebrafish pilot artifacts. The installed package and workspace draft were identical at the initial inspection.

Follow-up inspection: both package checks pass, but the copies now differ. The installed copy passes 12 unit tests; the workspace copy passes 14 and includes the inline-code-link checker fix described in item 12. The original inspection results below remain historical. Follow-up additions document missing recommendations and implementation status, not acceptance of the scientific workflow.

This was a single-assistant review, not independent external peer review. No skill files or research records were changed. This report is the only new review artifact. No new literature searches or citation-count requests were made.

## Overall assessment

Retain the modular structure, biomedical-only scope, separation of discovery from interpretation, two findings checkpoints, source retention, explicit access limits, and boundaries with Weaver, Beaver, and Wasp.

The principal weakness is execution assurance. Several recent outputs violated rules the skill already contains: no invented citations, complete-abstract reading, source-linked findings, and separate eligibility and access states. These failures should not be attributed solely to missing instructions. My earlier execution and reporting were deficient. Adding more prose alone is unlikely to correct them.

The package checker passes and all 12 unit tests pass. They test package structure and checker behavior, not the validity of a research corpus or synthesis. The saved pilot syntheses should be re-audited before reuse as scientific evidence summaries.

## Findings and proposed revisions

Locations in the skill are relative to `/home/hao/.agents/skills/honeybee-lit/`. Pilot paths are relative to `/home/hao/temp/refsearch/`.

### 1. Critical: unsupported findings and placeholder citations reached saved syntheses

Locations: SKILL.md, Essential rules and Completion check; references/06_synthesis_and_claims.md, Claim-to-evidence map; references/07_verification_and_delivery.md, Mechanical integrity and scientific support.

Observed evidence:

- `zebrafish-drug-self-admin/notes/2026-10-16_zebrafish-drug-self-admin-evidence-note.md:22-23` includes PMID 22419037 from another corpus and the placeholder `42036732-like`. Neither identifier is in the retrieved zebrafish abstract corpus. Other entries contain unresolved fragments such as `26993913 (?)`.
- The saved synthesis lists PMID 11553778 under direct contingent self-administration, although its retained abstract explicitly reports "cocaine-induced conditioned place preference".
- The synthesis adds a "lid-based" apparatus to PMID 28811180 and a "disulfiram-like" agent to PMID 35229935. Those details are not established by the inspected abstracts. The latter abstract reports an approved alcohol deterrent but does not name it.

Why it matters: storing a claim beside a real PMID does not make it source-supported. The skill already prohibits these errors, but no release condition prevented them.

Recommended revision:

> Before releasing a synthesis, every empirical citation must resolve to an inspected source in the review or an explicitly registered supporting source. Each central claim must have a saved supporting passage or table/figure location. Unresolved citation placeholders cannot appear as evidence. Details absent from the inspected source remain not established; retrieve the necessary full text or narrow the claim.

Suggested correction to the example classification:

> PMID 11553778: cocaine-induced CPP in zebrafish; a drug-associated place-conditioning study, not contingent drug self-administration.

Add a mechanical check for unresolved or out-of-corpus identifiers, followed by an explicit scientific support review. Neither identifier validation nor quotation matching can replace the latter.

### 2. Critical: retrieval and prioritization were reported as completed screening

Locations: references/04_screening.md:13-21; references/03_corpus_and_provenance.md, Coverage dimensions; templates/screening-record.md; tests/acceptance.md.

Observed evidence:

- The zebrafish workspace contains 553 discovered identifiers, 154 selected records, and 154 nonempty saved abstracts.
- The saved 72-record focused subset was produced in the visible execution using keyword matches on titles or the first 600 abstract characters. That is a prioritization operation, not a scientific inclusion decision.
- Execution displayed abbreviated abstracts, including 420-character and 1,200-character prefixes, yet the saved records and final answers asserted full screening or reading. There is no complete per-record scientific decision ledger supporting that assertion.
- The zebrafish search record falsely credits a "zebrafish QA rule" in the package checker for detecting a cap. The checker contains no such rule.

Why it matters: saving complete text, displaying a snippet, reading a complete source, and scientifically assessing it are different actions. An audit trail must not convert one into another.

Recommended revision:

> Track retrieval, prioritization, source inspection, eligibility assessment, extraction, and appraisal separately. A keyword-selected queue is not an included set. A record without a completed scientific assessment remains pending, not excluded. Generate completed-screening counts from explicit decisions, and do not claim complete reading when only snippets or truncated tool output were inspected.

A decision ledger documents the declared assessment process; it cannot prove that a model understood a source. Add adversarial tests for this distinction.

### 3. Major: the PubMed adapter cannot satisfy the advertised retrieval contract

Locations: references/02_search_and_retrieval.md:23-43; templates/search-record.md. Upstream implementation: `/home/hao/.agents/skills/pubmed_database/scripts/pubmed_api.py:135-170` and `:268-275`.

Observed evidence:

- The installed search function defaults to ten PMIDs and returns only the identifier list. It discards the ESearch count, query translation, and warnings.
- Consequently, a ten-record response is not a ten-hit total, and a response shorter than a large requested cap is not independent count reconciliation.
- Article titles are extracted with `findtext("ArticleTitle")`, which loses text after nested XML tags. A synthetic nested-title probe returned `Ca` instead of `Cav1.3 channels`; the saved zebrafish record for PMID 40992927 has an empty title.

Recommended revision:

> Before live retrieval, verify that the selected adapter returns explicit request limits and sorting, total count when available, returned IDs, query translation and warnings when available, errors, and source-response provenance. If required metadata are unavailable, mark coverage unverified rather than reconstructing it from list length.

Require explicit limits and sorting on every search. Use a compatible metadata-preserving adapter or propose an authorized upstream fix; do not bypass the installed rate limiter or silently modify another skill. For XML titles, preserve nested text with an itertext-equivalent parser and test superscripts, subscripts, and structured abstracts. Test provider errors separately from successful empty results.

### 4. Major: checksum manifests are not reliably constructed or verified

Locations: references/03_corpus_and_provenance.md, Source manifest; references/07_verification_and_delivery.md, Mechanical integrity; templates/source-manifest.md.

Observed evidence:

- The CACNA1C and zebrafish manifests contain an entry for their own manifest file. That entry fails its checksum because it records an earlier version of the manifest before replacement.
- Other listed files matched their recorded hashes in this inspection. The CACNA1D manifest had no mismatches.
- None of the three manifests covers the saved notes or synthesis outputs, despite earlier conversational wording implying broad saved-result verification.

Recommended revision:

> Exclude a manifest from its own contents. Record a checksum for the finalized manifest separately if needed. Distinguish immutable source inventories from versioned output inventories. Verify every listed file before reporting integrity success, and state which files the manifest covers.

Provide a small manifest builder/verifier with explicit schemas and regression tests. Preserve old source snapshots and prior manifest versions. Do not overwrite a failing manifest to conceal a mismatch.

### 5. Major: the evidence model needs explicit assay and outcome classifications

Locations: references/05_extraction_and_appraisal.md:13-35; templates/extraction-record.md; references/06_synthesis_and_claims.md.

Observed evidence: the zebrafish synthesis groups conditioned place preference, a nicotine concentration-gradient preference assay, and response-contingent drug delivery under direct self-administration. The CACNA1D note labels the method in PMID 24470632 as qPCR although its retained abstract specifies quantitative in situ hybridization.

Recommended revision:

> For each central finding, extract the actual model, manipulation or exposure, outcome, comparator, and study method from the source. Keep the authors' assay name separate from the reviewer's operational classification. Record not established when the source lacks the information needed to classify it.

For behavioral-model reviews, add fields for the response, consequence, contingency, delivery route, active/inactive or yoked control where reported, schedule, and measured endpoint. Distinguish CPP, voluntary spatial exposure, operant self-administration, reinstatement, withdrawal, and food-maintained responding. A common label does not establish a common procedure. Use appropriate biomedical equivalents in clinical, biomarker, and genetic reviews.

### 6. Major: scope selection and work limits need clearer operational rules

Locations: SKILL.md, Select the task and Workflow; references/01_scope_and_protocol.md, Protocol gate; references/08_resume_and_updates.md, Amendments.

Observed evidence: the short topic request "zebrafish drug self-administration models" was immediately treated as a critical narrative review without the protocol confirmation required for that mode. The run expanded to 553 discovered identifiers before narrowing its assessed subset. A limitation statement written afterward does not replace prospective scope decisions.

Recommended revision:

> For a short topic prompt, default to a focused overview with a stated provisional scope, or ask one scope-setting question if the intended depth materially changes the work. Use a full narrative, scoping, or systematic-review workflow only when requested or confirmed. Approve the databases, retrieval bounds, full-text effort, and deliverable before expanding the search.

This should reduce unnecessary interviews for small tasks while retaining confirmation for consequential changes. Record amendments when a search expansion or later restriction changes the evidence base.

### 7. Major: non-gene biomedical questions need their own search-planning patterns

Locations: references/02_search_and_retrieval.md, Construct and calibrate queries and Biomedical lanes; templates/protocol.md; SKILL.md description and README.md:3.

Why it matters: the skill is correctly biomedical-only, but source menus are not a substitute for a question-specific retrieval plan. The statement that entity vocabulary "is curated" does not identify an actual vocabulary resource or verification step. The README can also be read as promising PubMed, Europe PMC, and a GWAS lane for every question.

Recommended addition:

| Biomedical question | Planning dimensions |
|---|---|
| Gene and phenotype | Verified identity and aliases, phenotype definitions, species, evidence type; a human association lane when relevant. |
| Drug and behavior | Drug and chemical names, behavior and assay terms, delivery/exposure, and direct versus adjacent endpoints. |
| Model or method | Species/system, operational assay, comparator, validation target, and performance limits. |
| Disease and intervention | Population, intervention/exposure, comparator where relevant, outcomes, and eligible designs. |
| Biomarker or mechanism | Biological material, measurement, timing, exposure, outcome, and whether evidence concerns cause, consequence, or association. |

Suggested wording:

> Select and verify terminology for the biomedical question; do not assume a curated vocabulary exists. Run only relevant, approved lanes. GWAS Catalog is optional for appropriate human genetic questions, not a requirement for all biomedical reviews.

Module 02 does not provide the GWAS Catalog workflow advertised in the skill description. Add a bounded, optional workflow with query, trait-selection, retrieval, provenance, and coverage requirements, or narrow the description to match the documented capabilities.

Replace "any lane you do not run must be named as not run" with a requirement to report omitted planned or relevant lanes and their consequences. Do not require an inventory of every unused database option for a focused question.

For genetic lanes, resolve eligible traits and preserve their identifiers, exact outcome definitions, and mapping uncertainty. A pulmonary study conducted in never-smokers is not a smoking-behavior association merely because a reported-trait string contains "smokers". Do not count association rows as independent studies or assign target activation/inhibition from a locus association.

### 8. Major: citation ranking confuses reports with projects and needs a defined candidate universe

Locations: references/02_search_and_retrieval.md:55-67; templates/citation-count-record.md; CACNA1C citation-count worked example.

Why it matters:

- "Choose one canonical record per project" is appropriate neither as a general paper-ranking rule nor as a substitute for duplicate-record resolution. Distinct papers from one project remain distinct papers.
- Ranking ten selected PMIDs cannot establish the most-cited paper across an entire topic.
- The worked example retains a table, but not the original OpenAlex responses or exact per-call timestamps. A service's version grouping and self-citation coverage must not be guessed.

Recommended revision:

> Define the ranking unit as a paper/report, unless the user explicitly requests a study or project ranking. Deduplicate duplicate metadata records, not distinct publications. Record the service's version-grouping behavior without inventing a combined count. Save original metric responses and timestamps. Report "highest cited among the retrieved eligible candidates in [service] on [date]" unless the documented candidate search supports a broader claim.

Keep biomedical relevance and primary-study/review status visible. If requested, present primary studies and reviews separately. Never treat a citation count as evidence quality or support for a claim.

### 9. Major: central method-dependent claims need a full-text trigger

Locations: references/02_search_and_retrieval.md, Full-text access; references/06_synthesis_and_claims.md, Claim-to-evidence map; references/07_verification_and_delivery.md.

Why it matters: the existing instructions allow abstract-bounded tasks, which is useful, but the pilot answers made apparatus, dosing, control, and causal-specificity claims not supported by the inspected material. Merely labeling an answer abstract-level does not make those details acceptable.

Recommended revision:

> If a central claim depends on methods, controls, effect estimates, intervention identity, or outcome definitions absent from the abstract, retrieve and inspect the necessary full text or supplement. If this cannot be done within scope or access limits, narrow the claim and report the specific uncertainty. Do not supply a likely detail from memory or another paper.

Keep publication-notice checks separate, with their source, date, and actual result. Do not add a fixed full-text quota unrelated to the question.

### 10. Major: separate package tests from corpus checks and scientific acceptance tests

Locations: scripts/check_skill.py; tests/test_check_skill.py; tests/acceptance.md; references/07_verification_and_delivery.md:21.

Observed evidence: all 12 current unit tests pass. A disposable fixture containing an unsupported citation and a false screening-completeness assertion also passes the package checker, as expected from its documented scope. That is not a bug in a package-only checker, but it cannot be used as evidence that review safeguards work.

Recommended validation layers:

1. Package checks: frontmatter, local links, fences, and protected-text behavior.
2. Corpus checks: identifier membership, unique keys, counts, retrieval caps, source hashes, exact quotations, unresolved items, and output provenance.
3. Scientific regression cases: CPP must not become self-administration; expression must not become behavior; a mapped locus must not become a causal gene; a smoking-exposure marker must not become dependence susceptibility; an incomplete search must not become an absence claim.

Use fixed synthetic fixtures for deterministic tests and source-linked real examples for semantic review. Mechanical checks cannot prove scientific correctness or replace the human reviewers required by a selected formal method. Record observed pass/fail/blocked/not-run results, not hypothetical acceptance.

Reconcile README.md and tests/validation.md with the existing pilot artifacts. Distinguish a workflow that was executed from one that passed its acceptance criteria; the presence of saved searches or syntheses establishes neither source support nor successful end-to-end validation. Record what was exercised, what failed, and what remains untested, including fresh-conversation reopening. Preserve the original validation history rather than replacing it with an unsupported success claim.

### 11. Minor: writing handoff and response-size rules are inconsistent or underspecified

Locations: SKILL.md:82; references/06_synthesis_and_claims.md:49-61; references/07_verification_and_delivery.md, Delivery.

Why it matters: the entry point mentions Weaver for integrated manuscript/grant work, while Module 06 also invokes it for long stand-alone syntheses. Short answers still need the user's scientific prose standards. Prior answers were much longer than the topic prompts required, and one synthesis was not saved until the user asked.

Recommended revision:

> Before drafting scientific synthesis prose, read the relevant shared guidance in the installed Weaver Scientific prose module, resolving it through Weaver's entry point. Apply only the relevant craft checks for a short answer; do not import manuscript scaffolding or submission requirements. If Weaver is unavailable, use Honeybee's concise fallback and report the dependency only if it blocks the requested task.

> Match answer length to the request. For a focused topic overview, provide a concise answer and a small set of central sources, with detailed extraction and methods in saved notes. Save the final synthesis and link it in the handoff before declaring the task complete.

Retain short Honeybee-specific evidence rules rather than duplicating the full Weaver module. Add a defined fallback, not a new mandatory full-production dependency.

### 12. Minor: several templates and package checks need cleanup

Locations: templates/citation-count-record.md:11-22; scripts/check_skill.py:107-127; README.md:29 and Offline checks.

Observed defects:

- Citation-template options include "included / included", "not effected by service", and "11 caveat".
- The checker parses local links before protecting inline code, so a literal `[example](missing.md)` inside backticks is falsely reported as a missing link. This was reproduced in a disposable fixture.
- Documentation calls tests optional in some installations while retaining mandatory links to them. The currently installed copy includes tests and passes; the earlier missing-tests problem is not a current defect.

Suggested revisions:

> Self-citations: included / excluded / not reported by service. Other citing document types: included / excluded / not reported by service. Ranking caveat: service-specific, date-specific, and not a quality measure.

Protect inline code before local-link extraction and add a regression test. Follow-up status: this fix and two regression tests are present in the workspace copy, whose 14 tests pass, but not in the installed copy, whose 12 tests pass. The fix is not missing from both copies. Compare copies before recommending further changes and synchronize only approved revisions.

Either distribute the linked test artifacts with the standard package or document an explicit runtime-only distribution without broken links. Do not silently skip missing required test files and report a full-package pass.

### 13. Major: re-center skill identity as a preclinical literature review workflow rather than a clinical systematic review tool

Locations: SKILL.md:2-27; references/01_scope_and_protocol.md; references/methodology.md.

Observed misalignment:
The draft currently imposes Cochrane intervention review procedures, citing Cochrane Handbook chapters 4 and 5, requiring dual human reviewer quotas, and expecting clinical trial PICO frameworks. In practice, honeybee-lit is primarily a literature review skill for evidence synthesis, critical narrative review, and topic mapping. It is not an exhaustive clinical systematic review engine.

Why it matters:
Burdening basic and preclinical literature reviews with clinical systematic review mandates creates unnecessary friction and misrepresents the nature of laboratory evidence synthesis. Preclinical rodent experiments and molecular genetic studies cannot be evaluated using human clinical trial rubrics.

Recommended revision:

> Honeybee-lit is primarily a literature review skill for preclinical biomedical research. Its purpose is structured, reproducible evidence synthesis, critical narrative review, and topic mapping. It is not a clinical systematic review tool.

De-emphasize Cochrane intervention systematic review standards. Retain core scientific integrity principles (unbiased search, immutable source retention, transparent eligibility decisions, explicit tracking of null and conflicting results, and audit trails) without imposing clinical intervention review quotas or clinical risk of bias frameworks (such as RoB 2).

For preclinical intervention studies in animals, reference SYRCLE's risk of bias tool (Hooijmans et al., 2014) and ARRIVE 2.0 reporting guidelines (Percie du Sert et al., 2020) rather than clinical Cochrane standards.

### 14. Major: establish PubMed E-utilities and bioRxiv as core preclinical discovery lanes

Locations: references/02_search_and_retrieval.md:45-54; templates/search-record.md; templates/protocol.md.

Why it matters:
Preclinical research in neuroscience, genetics, and behavioral pharmacology moves rapidly. Relying solely on MEDLINE indexing causes significant lag, while abstracting over retrieval through uninspected wrappers discards essential metadata. bioRxiv preprints represent a primary medium for current preclinical experimental findings and must be included alongside PubMed.

Recommended revision:

> Establish PubMed via direct NCBI E-utilities and bioRxiv as the primary discovery lanes for preclinical literature reviews.

1. PubMed E-utilities lane:
- Query NCBI E-utilities directly (`esearch.fcgi`, `esummary.fcgi`, `efetch.fcgi`).
- Capture `WebEnv` and `query_key` for reproducible count reconciliation and server-side pagination.
- For full-text XML extraction from PubMed Central, use the BioC API or PMC Open Access web service.
- Use XML itertext parsing to preserve nested tags in article titles and abstracts (such as gene symbols, subscripts, and chemical formulas). Discarding nested XML tags causes silent data corruption.

2. bioRxiv preprint lane:
- Integrate the bioRxiv REST API for preprint discovery in preclinical categories (neuroscience, pharmacology and toxicology, genetics, genomics, and animal behavior).
- Parameterize searches by date interval, subject category, and title/abstract keywords.
- Track preprint versions explicitly using DOI version suffixes.
- Cross-reference preprints against PubMed and Crossref to determine whether a peer-reviewed version exists, recording any changes in reported results or conclusions.

### 15. Major: add domain-specific parameters for operant behavior and genetics

Locations: references/05_extraction_and_appraisal.md:13-35; templates/extraction-record.md; templates/appraisal-record.md.

Why it matters:
Generic extraction templates fail to capture the experimental variables that determine whether behavioral pharmacology and genetic findings are comparable or valid.

Recommended additions to extraction and appraisal templates:

1. Operant behavioral pharmacology parameters:
- Reinforcement schedule: Fixed Ratio (FR), Variable Ratio (VR), Progressive Ratio (PR; with explicit breakpoint definition and session duration criteria), Fixed Interval (FI), or second-order schedules.
- Operant contingency and manipulandum: Active versus inactive manipulandum (lever press, nosepoke), discriminative stimuli (S^D), conditioned cues, timeout periods, and shock or infusion titration parameters.
- Behavioral phase: Acquisition, maintenance, dose-response design (ascending, descending, or randomized), extinction, and reinstatement (distinguishing cue-induced, drug-primed, and stress-induced reinstatement via footshock or pharmacological agents such as yohimbine).
- Pharmacological parameters: Compound, salt form, vehicle, administration route (systemic IV, IP, SC versus central ICV or intracranial microinjection with stereotaxic target), pretreatment interval, and dose range.
- Subject biological variables: Species, strain, substrain (e.g., C57BL/6J versus C57BL/6N, Sprague-Dawley versus Wistar), sex, age, weight, housing conditions (single versus group), circadian testing phase (light versus dark cycle), and feeding regimen (ad libitum versus percentage food restriction).
- Behavioral distinctions: Differentiate contingent operant self-administration from Pavlovian conditioned place preference (CPP), non-contingent drug administration, locomotor activity, or food-maintained control behavior.

2. Genetics and functional genomics parameters:
- Locus versus causal gene: Differentiate genomic locus or QTL association from verified causal gene attribution. Evaluate linkage disequilibrium (LD) blocks and multiple testing correction (standard genome-wide threshold of p < 5e-8).
- Functional genomics: Record eQTL tissue and cell-type specificity, fine-mapping resolution, and experimental perturbation methods (knockout, knock-in, conditional Cre/loxP, CRISPR-Cas9, viral vector serotype, promoter, and titering).

### 16. Major: adopt a two-tier persistence model for high-throughput screening and detailed extraction

Locations: references/03_corpus_and_provenance.md:9-24; references/04_screening.md; templates/screening-record.md.

Why it matters:
The current templates require repeating a 30-line Markdown form for every decision. In a review with 500 to 2,000 records, generating hundreds of individual Markdown files or one massive file quickly exhausts context windows, causing output truncation or fabricated screening counts.

Recommended revision:

> Implement a two-tier persistence model that separates high-throughput bulk tracking from granular evidence dossiers.

1. Tier 1: High-throughput structured records (TSV or JSONL):
- Use `references/literature-review/records/screening.tsv` (or `screening.jsonl`) for bulk title and abstract screening.
- Enforce a fixed schema:
  `record_id`, `source_id`, `stage` (title_abstract / full_text), `decision` (advance / include / exclude / uncertain), `primary_reason_id`, `passage_locator`, `reviewer_id`, `timestamp`.
- Batch screening decisions in bounded packets of 20 to 30 records to prevent criterion drift and context exhaustion.

2. Tier 2: Detailed Markdown dossiers:
- Reserve granular Markdown records (`templates/extraction-record.md`, `templates/appraisal-record.md`, `templates/claim-evidence-map.md`) for included studies, in-depth quantitative extractions, complex study linkages, and contested claim verifications.

### 17. Major: integrate GWAS Catalog MCP tool and automated corpus validation

Locations: references/02_search_and_retrieval.md; references/07_verification_and_delivery.md:21; scripts/.

Why it matters:
The skill description advertises a GWAS Catalog association lane, but the reference modules provide no workflow for it. Additionally, the existing checker (`scripts/check_skill.py`) verifies only skill package syntax, leaving research corpora without automated verification.

Recommended additions:

1. GWAS Catalog MCP / API workflow:
- Define an operational workflow using the GWAS Catalog MCP tool or REST API (`/associations`, `/studies`, `/traits`).
- Query by gene symbol, trait (using Experimental Factor Ontology [EFO] terms), or variant (rsID).
- Extract lead variant, p-value, odds ratio or beta coefficient with confidence intervals, risk allele, mapped genes, and study ancestry.
- Distinguish direct phenotype associations from secondary pleiotropic signals.

2. Automated corpus validation script:
- Provide an executable validation script (`scripts/validate_corpus.py` or `scripts/validate_corpus.R`) that inspects `references/literature-review/` and checks:
  1. Source file existence and SHA-256 hash match against `source-manifest.tsv`.
  2. Review flow count arithmetic reconciliation (Total Identified - Duplicates = Screened; Screened - Excluded = Full Text Sought; Sought - Unretrieved = Assessed; Assessed - Excluded = Included).
  3. Claim-to-exclusion cross-checking: ensure no record marked as `exclude` in `screening.tsv` is cited as empirical evidence in `claim-evidence-map.md`.

## Recommended sequence

1. Re-audit the existing pilot syntheses and correct template typographical errors (such as in `citation-count-record.md`).
2. Implement the two-tier data persistence model (TSV/JSONL for bulk screening, Markdown for detailed extraction) and add the corpus validation script (`scripts/validate_corpus.py`).
3. Re-center skill identity as a preclinical literature review workflow, incorporating SYRCLE and ARRIVE 2.0 standards while de-emphasizing clinical systematic review overhead.
4. Integrate preclinical discovery lanes: PubMed NCBI E-utilities with XML `itertext()` parsing and bioRxiv REST API with category filtering.
5. Add domain-specific extraction parameters for operant behavioral pharmacology and functional genetics.
6. Formalize the GWAS Catalog API/MCP query workflow and citation ranking rules.
7. Run an end-to-end preclinical review pilot across PubMed and bioRxiv to validate the updated pipeline.

The next version should prioritize fewer unsupported claims and honest completion states, not more databases or a larger instruction file.

## Checks performed for this review

- Read the installed skill and all bundled modules, templates, checker, and tests.
- Compared installed and draft directories: identical, excluding bytecode caches.
- Ran the package checker: passed.
- Ran all 12 unit tests: passed.
- Verified existing manifests against files: CACNA1C and zebrafish self-entries failed; CACNA1D passed; other listed files matched.
- Reconciled zebrafish saved identifiers and abstract records: 553 discovered, 154 selected, 154 retrieved nonempty abstracts, 72 in the keyword-selected focused subset.
- Reopened selected complete saved abstracts to check exemplar claims. This was not a full scientific re-review of all pilot records.
- Inspected the installed PubMed adapter and demonstrated nested-title loss with a synthetic XML example; no live API call was needed.
- Demonstrated the package checker's unsupported-evidence scope and inline-code-link false positive using temporary fixtures.
- Read Weaver's shared scientific prose guidance to assess the existing writing handoff.

No source facts were refreshed from external databases. The observed integrity and consistency defects are local reproducible findings; claims about the entire underlying literature would require a separate scientific review.

## Implementation status (2026-10-17, second session)

Adopted in the workspace copy (`/home/hao/temp/refsearch/honeybee-lit/`); the installed copy is unchanged:

- Item 1 (release condition): stated in Module 07 and the SKILL.md completion check, enforced mechanically by `scripts/validate_corpus.py` (out-of-corpus identifiers and placeholders fail).
- Item 2 (prioritization is not screening): Module 04 Automation boundaries and the new Decision ledger section; counts come from the ledger, unread records stay pending.
- Item 4 (manifests): Module 03 and the source-manifest template forbid self-listing and require a machine-readable manifest; the validator verifies hashes and detects self-listing.
- Item 8, partly: Module 02 ranking unit is the paper/report, not one record per project; the citation-count template records service version grouping, saved responses, and the bounded claim wording.
- Item 12 (template typos): citation-count template corrected. The inline-code checker fix was already present.
- Item 16 (two-tier persistence): ledger schema and batch rule in Module 04, two-tier policy in Module 03.
- Item 17, partly: corpus validator added with 13 unit tests. The GWAS Catalog workflow is not added.

Run against the three pilots (read-only), the validator reproduced the item 1 and 4 findings and found one more: PMID 30555482 is cited in the CACNA1D evidence note but absent from every saved source in that workspace. Details are in tests/validation.md.

Deferred pending a user decision: items 13 to 15 and the GWAS part of item 17. They grow the instruction set and re-scope the skill toward preclinical work on the basis of three preclinical pilots; confirm that this matches intended use first. Items 3, 5 to 7, and 9 to 11 remain open as smaller module revisions. The pilot syntheses have not been corrected or re-audited.
