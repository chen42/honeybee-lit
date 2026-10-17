# Methodological-source register

## Scope of these notes

Official pages were retrieved on 2026-10-16. The inspected material supports the distinctions below; it is not a full audit of every linked checklist, appraisal instrument, or review method. For an actual review, retrieve and retain the governing documents, confirm their current versions and applicability, and distinguish required conduct from recommended practice and reporting guidance.

Readable captures were retained in the drafting workspace's `design-sources/` directory, outside this skill package, with a checksum manifest. They are text extractions rather than original HTML or PDF snapshots. The skill does not depend on those local captures being distributed.

## Official sources inspected

| Source | Material inspected and use | Verification limit |
|---|---|---|
| [PRISMA 2020](https://www.prisma-statement.org/prisma-2020) | Official overview describing the statement, checklists, explanation and elaboration, and flow diagrams for original and updated reviews. Routes systematic-review reporting. | The landing page was inspected; a complete item-by-item checklist audit was not performed. PRISMA reporting does not itself establish valid review conduct. |
| [PRISMA-ScR](https://www.prisma-statement.org/scoping) | Official scoping-review extension overview and links to its checklist and explanatory paper. Supports a distinct scoping-review reporting route. | The overview was inspected, not every linked tip sheet or the full explanatory paper. Select conduct methods separately. |
| [PRISMA-S](https://www.prisma-statement.org/prisma-search) | Official search-reporting extension overview and links to its checklist, explanatory paper, and record-tracking FAQ. Routes detailed search reporting. | The overview was inspected; the extension's entire item set was not audited in this draft. |
| [Cochrane Handbook, Chapter 4](https://training.cochrane.org/handbook/current/chapter-04) | Key points and sections 4.2.2, 4.2.3, and 4.6.1 through 4.6.4: search planning, studies versus reports, linkage, eligibility, incomplete results, independent selection, and decision records. | This is intervention-review guidance, not a universal rule for every literature question. The captured chapter labels itself version 6.5.1 and last updated March 2025; the entire chapter and its technical supplement were not audited. |
| [Cochrane Handbook, Chapter 5](https://training.cochrane.org/handbook/current/chapter-05) | Key points and sections 5.5.1 through 5.5.5: reading reports, independent extraction, piloting/training, multiple reports, discrepancy resolution, and preservation of original extractions. | The captured chapter's citation labels the Handbook version 6.5 and the chapter last updated October 2019. Do not silently assign it Chapter 4's version/date. Only the stated sections were substantively inspected. |

The Cochrane guidance inspected requires independent human final eligibility decisions and independent human outcome extraction for Cochrane intervention reviews. Honeybee must identify these roles when that conduct standard is selected. Model-assisted checks must not be presented as satisfying a requirement for two people.

## Select additional guidance for the actual question

Verify current official methods and reporting guidance suited to the chosen review type and evidence designs. A diagnostic, prognostic, qualitative, animal, mechanistic, or mixed-evidence review may need different methods from an intervention review. Consult a suitable methodological handbook or specialist rather than extending intervention rules by analogy.

Choose appraisal tools by their actual target and instructions. A reporting checklist is not a risk-of-bias tool. A study-level judgment is not automatically a result-level judgment, and formal body-of-evidence grading is not an average of paper scores. No appraisal tool or universal quality score is bundled or certified here.

Where search-strategy peer review or methodological expertise is needed, identify the appropriate human role and access arrangements. A model's simulated critique cannot be reported as review by an information specialist or an independent expert.

## Local workflow policies, not external methodological claims

The following are adopted from the user's companion-skill approach:

- A short requirements interview with at most five independent questions per round.
- A corpus-forensics report before substantive screening and an evidence-findings report before full synthesis.
- Immutable local sources, retained exclusion history, source hashes, and recoverable evidence versions.
- Approval before consequential scope changes, installations, Git mutations, uploads, or out-of-scope document edits.
- Neutral scientific prose, preservation of acronyms and source content, and avoidance of rhetorical em dashes and en dashes.
- Small-task routing rather than full scaffolding for every question.

These are skill policies. Do not attribute the interview limit, report names, folder layout, punctuation policy, or every provenance field to PRISMA or Cochrane.

## Companion sources

The design studied the installed `beaver-data` entry point and five reference modules, `weaver-text` and its eight numbered reference modules, and `wasp-lit` with its workflow, search, screening/synthesis, full-text, corpus/resume, and worker references. These informed the architecture and permissions, not the verification of biomedical claims. Their installed paths are environment-specific and are not hard-coded dependencies of this package.
