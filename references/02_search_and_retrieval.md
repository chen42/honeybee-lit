# 02. Search design and retrieval

## Choose sources and tools

Read [Module 01](01_scope_and_protocol.md) before a new review and [Module 03](03_corpus_and_provenance.md) before retrieval. Use installed retrieval skills when suitable. Read their prerequisites, access conditions, and credential handling before live calls. If no suitable skill exists, use an authoritative database interface within the approved scope. Missing access is a reported constraint, not permission to install a connector or change platforms silently.

Potential sources depend on the question: PubMed or Europe PMC for biomedical records, appropriate disciplinary databases, scholarly metadata services, study registries, preprint servers, and citation chaining. These are options, not a checklist of promised integrations. No single database or fixed database count establishes complete coverage. For formal intervention reviews, consult the chosen methodological guidance and obtain information-specialist input where required or recommended.

Keep discovery sources distinct from retrieval routes. Fetching the full text of an already discovered report from another host does not mean that host was searched as a discovery database.

## Construct and calibrate queries

1. Verify entity identity, aliases, species, and ambiguous ordinary-word abbreviations. Do not infer orthology or silently add aliases.
2. Combine free text and controlled vocabulary where the database supports it. Translate strategy across databases; do not reuse syntax without checking its meaning.
3. Avoid overrestricting the search with every outcome, mechanism, or anatomical qualifier. Decide which concepts must be searched and which should be assessed during screening.
4. Keep retrieval terms separate from interpretation categories. A broad hit does not establish a specific assay, cell type, anatomical subregion, or mechanism merely because it appears in the rubric.
5. Pilot the query, inspect translations and warnings, and assess ambiguous matches and retrieval of agreed known relevant reports. Known-report recovery is useful but does not prove sensitivity or completeness.
6. Refine within the approved pilot scope, then freeze exact strategies for the main run. Record changes and the original strategies.

Do not discover only supporting studies. Use searches and supplementary methods that can capture null and contrary findings. Report date, language, publication-type, species, and other restrictions with their rationale. Do not add an open-access filter simply because full-text access is limited.

## Run lanes in parallel, fail fast

Independent query lanes (separate strategies, concepts, or databases) can run concurrently. Dependent steps cannot: fetch abstracts for the union of identifiers only after the lanes that produce it have finished.

1. **Preflight first.** Before launching lanes, run one cheap request with a short timeout, such as `curl -fsS --max-time 20 -o /dev/null "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json"`. Adapters with long retry budgets can spend many minutes on a single request when the network or proxy is down; a failed preflight stops the run in seconds. Report it as a blocked search, not zero hits.
2. **Bound every lane.** Give each lane its own timeout, shorter than the adapter's retry budget, so one hung lane cannot consume the whole tool call. A timed-out or failed lane is recorded as such and rerun alone later.
3. **Bound concurrency by the provider's limits.** Run lanes in parallel only when the retrieval tool enforces a rate limit shared across processes; the installed `polite_http` client used by the PubMed adapter does, through a per-host lock file. Otherwise run lanes one at a time. Three concurrent lanes is a sensible default; NCBI allows 10 requests per second with an API key and 3 without.
4. **Report as lanes finish** and keep credentials out of logs and status lines.

`scripts/run_lanes.py` does all four. Lanes come from a TSV with `lane` and `query` columns, which also serves as the record of exact query strings:

```bash
python3 <skill-dir>/scripts/run_lanes.py searches/lanes.tsv \
  --preflight "curl -fsS --max-time 20 -o /dev/null https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json" \
  --command "uv run <pubmed-adapter> {out} search_pubmed {query} --max_results 1000 --sort_by relevance" \
  --jobs 3 --timeout 120 --out-dir searches
```

It prints a status line per finished lane, writes per-lane logs with credential-like URL parameters redacted, kills a timed-out lane's whole process group, and saves `lanes_summary.json` with each lane's query, status, timestamps, and returned count. The returned count is the length of the returned identifier list, capped by `--max_results`; it is not the database's reported total unless the adapter supplies that total. Exit status is 0 when all lanes succeed, 1 when any lane fails, and 2 when the preflight fails. With a per-lane timeout of 120 seconds and three concurrent lanes, six lanes finish within about four minutes even in the worst case; for longer runs, start the runner in the background with its output redirected to a log, and read the log between status updates.

## Search record

Use [the search-record template](../templates/search-record.md) for each executed query or supplementary search. Record:

- Review, protocol, search, and run identifiers.
- Database, interface, query as run, translation, and all applied limits.
- Execution time with time zone, sorting, pagination, and request or export parameters.
- Reported total, enumerated identifiers, retrieved records, caps, and unresolved differences.
- Raw response or export references, identifiers and query membership, warnings, and errors.
- Tool and version where available, and any relevant changing database state.

For citation chasing, name the seed report, direction, service, date, and discovered records. For user-supplied papers, register the intake origin rather than claiming database discovery. Do not invent a query history for imported records.

## Enumerate separately from retrieval

Reconcile retrieved identifiers against reported totals within the documented database behavior. For large searches, use supported pagination or count-reconciled partitioning. Do not assume offset paging can enumerate arbitrarily large sets.

Preserve all discovered identifiers even when a bounded task retrieves only a subset. Record selection rules and sorting before applying a cap. Separate a scientific eligibility exclusion from a record omitted because of budget, ranking, or an API limit.

No default newest-first cap or fixed full-text quota applies. A bounded narrative task can use approved limits, but the limits must appear in the coverage statement. A formal review with outstanding records cannot be called fully screened. If a large query remains unreconciled, preserve the partial results and report its status as partial or blocked.

Run large retrievals as batched calls with a status line between them and incremental saves, as described in [Module 07](07_verification_and_delivery.md), Progress reporting. Retries must respect the provider's terms and rate limits, with bounded attempts and recorded outcomes. Stop and report persistent failures. Do not turn an HTTP error, timed-out request, or incomplete export into a zero-result search.

## Biomedical lanes and gray literature

Concrete lane options depend on the question, and any lane you do not run must be named as not run:

- **Bibliographic and abstract lanes:** PubMed and NCBI E-utilities, MEDLINE vendors, Europe PMC, Embase when a subscription exists, and disciplinary databases the question requires (PsycINFO, CINAHL, BIOSIS or equivalents).
- **Gray literature and reports:** Author preprints indexed in PubMed plus field-common repositories (bioRxiv, medRxiv, SSRN-health, PsyArXiv), conference abstracts, dataset and code releases (Zenodo, Dryad), trial registries (ClinicalTrials.gov, ISRCTN, ICTRP), regulatory documents, standards, and government reports. Register these as discovery records with their own report level, not as full-text supplements.
- **Entity vocabulary:** The synonym and controlled-vocabulary lane is curated for genes and clinical concepts. Apply the disambiguation rule in [Module 01](01_scope_and_protocol.md) before retrieval, and record the mapping in the same template.
- **Species and model filters:** Name any applied species, sex, age, disease, or model-organism filters and their approved rationale; do not infer a model from the journal.
- **Language coverage:** Keep the same date/language rules. Biomedical non-English publication is unevenly indexed across APIs; treat language coverage as its own bias dimension rather than as a database limit.

## Citation-count lane

Use this lane only when the question is bibliometric: which report has been cited most often, what is a paper's citation count, or what is the most-cited report within a defined topic. Stay inside biomedicine; use metadata services that index biomedical reports (OpenAlex, Crossref, Semantic Scholar), and skip non-biomedical field proxies entirely.

1. **Name the service and endpoint.** Counts differ by design: OpenAlex `cited_by_count`, Crossref `is-referenced-by-count`, and Semantic Scholar `citationCount` measure overlapping but different citation graphs. Never mix services inside one ranking, and record service, endpoint, query, and access date for every count.
2. **Verify identity before counting.** Resolve the candidate to a single canonical record first: same DOI, same title, same venue and version. A preprint and its published version share no automatic count; decide from the protocol which version to rank and record that decision.
3. **Deduplicate metadata records, not publications.** The ranking unit is a paper or report unless the user explicitly requests a study or project ranking. Merge duplicate records of the same report; keep distinct papers from one project distinct. Record the service's own version-grouping behavior rather than inventing a combined count.
4. **Build a bounded candidate set from a documented search** (same search-record template) and sort by one service's count. For a curated short list rather than a full topic review, ignore this step and assess each candidate record directly.
5. **Verify and report the number from the source, not from memory**, and re-fetch at the stated access time. State whether citations were counted excluding self-citations, whether patents or other non-article referrers were included, and that a count is not a quality or peer-review measure.
6. **Ranking caveats:** counts accumulate differently across fields, lag recent work, and can exceed real scholarly credit. Any claim about the most-cited paper is service-specific and date-specific, and does not establish a paper's scientific support. Claim support is a separate check, covered in [Module 07](07_verification_and_delivery.md).

Metrics service records and counts are treated the same way as any other lane in [the search-record template](../templates/search-record.md) or [the citation-count template](../templates/citation-count-record.md).

## Preserve complete sources

Save original responses or exports and complete abstracts, including structured section labels and punctuation. Parse into a separate structured representation; do not replace originals with summaries. If a tool truncates a source, read additional slices or use smaller packets. If the source itself is incomplete, record that state.

Sources and source manifests follow [Module 03](03_corpus_and_provenance.md). A saved search brief or model-generated answer is not an original article. Open the underlying record before using an empirical claim.

## Full-text access

After title/abstract screening where applicable, seek full text for reports requiring full-text eligibility assessment, extraction, or central claim verification. Select any budget-limited subset using an approved rule and retain pending candidates. Prioritize scientific need rather than convenient access; state remaining access bias.

Use legitimate open access, institutional access already available, or user-supplied documents. Verify document identity with authoritative identifiers and metadata. A repository link is not proof of successful retrieval or permission to redistribute.

Distinguish retrieved, not found through the attempted routes, access denied, transient failure, identity conflict, and not attempted. Do not call a paper paywalled merely because one endpoint failed. A confirmed unavailability outcome describes the checked routes, not universal impossibility of access.

Retain original PDFs or structured full texts where available and permitted. Label readable extracts as extracts. Record whether figures, tables, supplementary files, and corrections were actually retrieved and inspected. Missing full text leaves eligibility or detailed claims unresolved when they depend on it.
