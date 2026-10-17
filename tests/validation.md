# Draft validation record

Date: 2026-10-16

Scope: local instruction-package structure and synthetic package-checker behavior. These checks do not validate a literature corpus or establish scientific method compliance.

## Executed checks

| Check | Actual command or procedure | Result |
|---|---|---|
| Package structure and selected frontmatter constraints | python3 honeybee-lit/scripts/check_skill.py | Passed |
| Local Markdown targets, code fences, and selected editable-prose punctuation | Same package checker | Passed |
| Synthetic checker tests | PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s honeybee-lit/tests -p 'test_*.py' -v | 12 tests passed |
| Location-independent checker invocation | Unit test invokes the script from another directory with an explicit fixture path | Passed |
| Methodological-source inspection | Official PRISMA overview pages and selected Cochrane sections, as recorded in the methodology register | Performed within the stated reading limits, not a full checklist audit |

The checker tests cover valid and broken links, escaping paths, frontmatter names and descriptions, duplicate fields, unclosed fences, protected source text, prose punctuation, and command-line execution. They use synthetic files rather than scientific evidence.

## Not executed

- Live scientific-literature search or end-to-end review pilot.
- Retrieval connector testing or research-corpus validation.
- Human eligibility screening, extraction, or adjudication.
- Formal scoping-review or systematic-review acceptance testing.
- Optional worker launch or model verification.
- Fresh-conversation reopening of a scientific source-to-claim chain.
- Pi skill discovery or installation.
- A full external-URL or official-checklist item audit.

## Follow-up checks, 2026-10-17

| Check | Actual command or procedure | Result |
|---|---|---|
| Package checker after revisions | python3 scripts/check_skill.py | Passed |
| Unit tests for both checkers | python3 -m unittest discover -s tests -p 'test_*.py' | 27 tests passed (14 package checker, 13 corpus validator); 34 after the lane runner was added |
| Corpus validator on the zebrafish pilot, read-only | validate_corpus.py with its manifest, abstracts_primary.json, and both notes | 7 failures: manifest lists itself; placeholders `42036732-like`, `??`, `26993913 (?)`; PMIDs 22419037, 42036732, 26993913 not in the corpus. Matches the manual findings in SUGGESTIONS.md item 1 and 4. |
| Corpus validator on the CACNA1C pilot, read-only | Same procedure with its abstracts files and notes | 1 failure: manifest lists itself |
| Corpus validator on the CACNA1D pilot, read-only | Same procedure with its abstracts files and notes | 1 failure: PMID 30555482 cited in the evidence note but absent from every saved source file. Not found by the manual review. |

| Lane-runner unit tests | python3 -m unittest tests.test_run_lanes | 7 tests passed: isolation of failures, credential redaction, API error objects, per-lane timeout, concurrency, failed and hung preflight |
| Live lane run, scratchpad only | run_lanes.py with a curl preflight and the installed PubMed adapter, 3 zebrafish lanes, --jobs 3 | Preflight ok; 3 lanes ok (12, 71, and 193 PMIDs returned) in about 1 second; no unredacted key in outputs. Returned counts are list lengths, not ESearch totals. |

The pilots were not modified. These results show that the validator detects the known defect classes in real files; they do not validate the pilots' science or the screening-ledger workflow, which has no live run yet.

The procedural scenarios in acceptance.md remain to be exercised. The package remains an instruction-and-template draft, not a released or scientifically validated review system.

Existing wasp-lit, weaver-text, and beaver-data installations were not modified. No Git repository was initialized and no installation or configuration change was performed.
