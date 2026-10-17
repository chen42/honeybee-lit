<p align="center"><img src="assets/honeybee-lib.jpg" alt="honeybee-lit badge" width="200"></p>

# honeybee-lit

General literature reviews, from focused citation checks to critical narrative, scoping, and systematic reviews, built on documented searches, an auditable evidence corpus, and source-linked synthesis. Searches use biomedical databases (PubMed, Europe PMC, GWAS Catalog); non-biomedical topics are out of scope. For evaluating candidate genes from a GWAS, use `wasp-lit`.

Part of a four-skill research suite: `beaver-data` (analysis), `weaver-text` (editing support for author-written text), `honeybee-lit` (general literature reviews), and `wasp-lit` (post-GWAS candidate gene-phenotype literature analysis).

## Why a honeybee?

A forager visits many flowers and reports each source's location precisely enough for others to find it, then stores what it gathers in identical cells. `honeybee-lit` aims for the same: searches others can rerun, and evidence stored in uniform, checkable records.

## Reproducibility and standardization

- **Protocol first.** The question, eligibility criteria, and search plan are confirmed before retrieval.
- **Rerunnable searches.** Exact search strings, databases, dates, and counts are saved. PubMed/Europe PMC and GWAS Catalog lanes run through `scripts/run_lanes.py` with a JSON run summary.
- **Preserved sources.** Retrieved records are kept with a SHA-256 manifest, so the corpus can be verified later.
- **Append-only screening ledger.** Every decision is a row with a fixed schema (`record_id`, `stage`, `decision`, `reviewer_id`, `timestamp`, and `primary_reason_id` for exclusions). Records without a decision stay pending; a ranked queue is never a screened set.
- **Standard templates.** Protocol, search record, source manifest, screening, extraction, appraisal, claim-evidence map, verification, and checkpoint use the same templates in every review.
- **Automated integrity checks.** `scripts/validate_corpus.py` checks manifest hashes, citations outside the corpus, ledger schema and counts, and excluded records cited as evidence.
- **Reopenable evidence.** Enough context is saved to reopen the original sources for any claim in a later conversation. Checks are recorded literally as passed, failed, blocked, or not run.

## What it does

1. Confirm the question and protocol.
2. Design, run, and document searches; preserve retrieved sources.
3. Report corpus problems before screening.
4. Screen complete abstracts in bounded batches; extract and appraise evidence.
5. Report evidence findings before full synthesis.
6. Synthesize, validate the workspace, and verify claim support.
7. Save context for later reopening.

A focused citation check uses only the relevant steps. Narrative, scoping, and systematic reviews keep their methodological differences. Model assistance is never reported as independent human review. Statistical pooling requires a separate `beaver-data` task.

## Package contents

```text
honeybee-lit/
├── SKILL.md              # Task selection, rules, stage gates, module routing
├── README.md
├── LICENSE
├── SUGGESTIONS.md        # Improvement candidates (not working instructions)
├── assets/honeybee-lib.jpg
├── references/           # Eight workflow modules and the methodology register
├── templates/            # Standard review records
├── scripts/
│   ├── check_skill.py    # Package structure and link checker
│   ├── validate_corpus.py# Read-only workspace validator
│   └── run_lanes.py      # Parallel search-lane runner
└── tests/                # Unit tests and procedural acceptance scenarios
```

All scripts use only the Python standard library.

## Project workspace

Research workspaces live outside the skill. A new project places its corpus under `references/literature-review/` (`sources/` for retrieved records and manifests, `records/` for the screening ledger) and its notes, reviews, and logs in existing project folders. Validate before releasing any synthesis:

```bash
python3 <skill-dir>/scripts/validate_corpus.py \
  --manifest references/literature-review/sources/manifest.json \
  --corpus references/literature-review/sources/abstracts.json \
  --screening references/literature-review/records/screening.tsv \
  --claims notes/claim-evidence-map.md --check notes/synthesis.md
```

A passing run establishes corpus membership and integrity, not that a passage supports a claim. Options are described in [Module 07](references/07_verification_and_delivery.md); lane runs in [Module 02](references/02_search_and_retrieval.md).

## Companion skills

| Skill | Role |
|---|---|
| [`beaver-data`](https://github.com/chen42/beaver-data) | Approved statistical analysis, including quantitative evidence synthesis. |
| [`weaver-text`](https://github.com/chen42/weaver-text) | AI editing, review, and submission help for author-written manuscripts and grant proposals. |
| [`honeybee-lit`](https://github.com/chen42/honeybee-lit) | General literature reviews, from citation checks to narrative, scoping, and systematic reviews. |
| [`wasp-lit`](https://github.com/chen42/wasp-lit) | Post-GWAS literature analysis of candidate gene-phenotype relationships. |

`honeybee-lit` can reuse a `wasp-lit` corpus read-only through an explicit mapping. It does not modify companion skills or require them for focused questions.

## Installation

Clone the repository, unchanged, into a skills location your agent scans:

```bash
# Pi
git clone https://github.com/chen42/honeybee-lit.git ~/.pi/agent/skills/honeybee-lit
# Claude Code (user or project scope)
git clone https://github.com/chen42/honeybee-lit.git ~/.claude/skills/honeybee-lit
```

In Pi, run `/reload` after cloning. Live retrieval needs a PubMed/Europe PMC tool and network access. Offline package checks:

```bash
python3 scripts/check_skill.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## License

[MIT](LICENSE)
