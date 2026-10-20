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

## Initial probe summary

After the initial probe searches, briefly tell the user how many potentially relevant hits were found in each lane, using the saved search results. Based on a quick inspection, say whether the hits address the question and whether any obvious gap calls for adjusting the search. Search matches are not screened inclusions. Give this summary even when the search scope is already approved. A short message is enough; no detailed table or additional approval step is required.

## Run lanes in parallel, fail fast

Independent query lanes (separate strategies, concepts, or databases) can run concurrently. Dependent steps cannot: fetch abstracts for the union of identifiers only after the lanes that produce it have finished.

1. **Preflight first.** Before launching lanes, run one cheap request with a short timeout, such as `curl -fsS --max-time 20 -o /dev/null "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&retmode=json"`. Adapters with long retry budgets can spend many minutes on a single request when the network or proxy is down; a failed preflight stops the run in seconds. Report it as a blocked search, not zero hits.
2. **Bound every lane.** Give each lane its own timeout, shorter than the adapter's retry budget, so one hung lane cannot consume the whole tool call. A timed-out or failed lane is recorded as such and rerun alone later.
3. **Bound concurrency by the provider's limits.** Run lanes in parallel only when the retrieval tool enforces a rate limit shared across processes; the installed `polite_http` client used by the PubMed adapter does, through a per-host lock file. Otherwise run lanes one at a time. Three concurrent lanes is a sensible default; NCBI allows 10 requests per second with an API key and 3 without.
4. **Report as lanes finish** and keep credentials out of logs and status lines.

`scripts/run_lanes.py` does all four. Lanes come from a TSV with `lane` and `query` columns (lane identifiers `lane-1`, `lane-2`, and so on; an optional `label` column gives each lane's short keyword, which status lines print beside the identifier, and an optional `purpose` column describes it), which also serves as the record of exact query strings:

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

## Corpus-size gate

After the initial search lanes finish and before retrieving abstracts or screening, estimate the corpus size and ask the user whether to process all records or a defined subset. Do this for every review and for focused tasks, unless the user has already specified the scope (for example, "screen everything" or "only the last five years"). Do not proceed past the gate on your own.

Base the estimate on saved results, not memory. `scripts/run_lanes.py` prints and saves it in `lanes_summary.json` (`size_estimate`), with `union_ids.json` and `membership.json`. Report:

- Unique records after deduplicating identifiers across lanes, and the number returned before deduplication.
- Records found by only one lane, which shows what each lane adds.
- Whether the estimate is a lower bound: lanes that failed, timed out, or returned exactly their result cap (pass `--cap`). Where the database's reported total is available, give it as well.
- The expected screening workload in batches of 20 to 30 abstracts, and whether full-text work is planned.

Then ask one question with bounded options, a recommendation, and its rationale. Typical options:

1. **All records.** State the number of batches. Recommend when the corpus fits the requested review type and the session or a planned series of sessions.
2. **A subset by lane or concept.** For example, the core lanes only, with their unique count. Name what the excluded lanes would have added.
3. **A subset by metadata rule**, such as date range, publication type, or species, with the count when computable. If the rule needs metadata not yet retrieved, say so; fetching summaries for all records is inexpensive and can precede the decision.
4. **A pilot batch first**, such as 25 records chosen by a stated rule, then decide with the observed eligibility rate.

Record the answer with [the decision record](../templates/decision-record.md): the selection rule, its basis, the counts selected and not selected, and the confirmation. A subset rule is a retrieval bound, not an eligibility criterion. Unselected records keep their identifiers and lane membership with the coverage state "outside approved cap"; they are not excluded, and the coverage statement and any review label must reflect the bound. Do not choose a subset rule after reading outcomes, and do not use relevance ranking as a subset rule without saying so.

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

### Plan, ask, then fetch

Use `scripts/fetch_fulltext.py` (run with `uv run`) in three steps from the review workspace:

1. **Plan.** `uv run <skill-dir>/scripts/fetch_fulltext.py plan <pmids.json>` checks access without downloading anything: PMC identifiers from PubMed links and Europe PMC metadata, Europe PMC's open-access flag, and an OpenAlex open-access lookup for records not in PMC. It sorts records into `pmc_open_access`, `pmc_restricted`, `pmc_access_unknown`, `open_elsewhere`, `closed`, and `lookup_failed`, writes `fulltext_plan.json`, and lists records that need the user in `needs_user.tsv`.
2. **Ask.** Report the counts, how many are retrievable by script, and the needs-user list, then ask which categories or PMIDs to fetch. Include `pmc_restricted` by default: the category means no open-access license, not no text. PMC `efetch` often still serves the body (for example NIH author manuscripts); in testing it did for 9 of 12 restricted records in one review and 0 of 3 in another. Trying them is quick and either retrieves the text or confirms absence. Rerun the plan before deciding if any lookups failed.
3. **Fetch.** `... fetch --categories pmc_open_access,pmc_restricted` (or `--pmid` for specific records) tries the routes in order: PMC `efetch` (JATS), Europe PMC `fullTextXML` (JATS), then PMC BioC. It saves the raw response and the parsed passages with SHA-256 hashes, records every attempt in `attempts/`, and writes `fulltext_index.json`. Already retrieved records are kept unchanged unless `--refetch` is given, which keeps the earlier record.

The routes, identity checks, and short retry settings (30 s timeout, at most two retries per route) are reused read-only from `wasp-lit`'s `scripts/pubmed_extension.py`. The script finds that module under `~/.agents/skills` and does not modify it; pass `--wasp` if it lives elsewhere. Without `wasp-lit`, report full-text retrieval as blocked rather than substituting an unchecked route.

Outcomes are `retrieved`, `unavailable` (at least one route confirmed absence), and `failed` (every route errored; rerun those PMIDs later). Observed provider behavior to account for:

- Europe PMC returns HTTP 500, not 404, for `fullTextXML` of articles that are in PMC but not open access. When its metadata says `isOpenAccess=N`, the script records that 500 as absence from that route.
- When PMC `efetch` returns metadata without a body, that is a confirmed absence from that route, not an error. A text served this way without an open-access license is for local use only; its license field records the restriction.
- The PMC BioC service serves only the PMC open-access subset. It rate-limits rapid requests (HTTP 429 with `Retry-After` of about a minute) and has had outages, and the HTTP client shares that back-off across all NCBI hosts, so one 429 stalls every other NCBI request. The script therefore skips BioC for articles Europe PMC marks `isOpenAccess=N`; this cut three restricted articles from about 210 s to 9 s in testing. BioC's `[Error] : No result can be found` reply is recorded as absence. Otherwise treat a BioC 429 or 5xx as a failed attempt, not as unavailability.
- Publisher sites often refuse scripted downloads (HTTP 403) even for open-access articles. Do not work around this; list the record for the user.

### Full texts that need the user

`needs_user.tsv` lists each record that no permitted route could retrieve, with its DOI, category, open-access status, and any open-access or landing URL. Give the user that list and ask whether they can retrieve the papers through institutional access or supply PDFs. Register each supplied file with `... register --pmid <PMID> --file <path> --origin "<how it was obtained>"`. Registration copies the file unchanged into the full-text folder, hashes it, records its origin and license status, removes it from the needs-user list, and marks its identity check as pending. Confirm the title, authors, and DOI against the PubMed record before extracting from it, and record the result. A user-supplied copy is for the user's local use; do not redistribute it.

Retain original PDFs or structured full texts where available and permitted. Label readable extracts as extracts. Record whether figures, tables, supplementary files, and corrections were actually retrieved and inspected. Missing full text leaves eligibility or detailed claims unresolved when they depend on it.
