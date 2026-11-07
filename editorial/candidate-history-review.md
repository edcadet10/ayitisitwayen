# Historical archive backfill — 7 November 2026

The previous release had 29 shared publications and only a few individual videos.
That did not satisfy the requested historical coverage. This backfill adds 8,501
article index records and 877 individual video records, plus six written previews
for historical government releases, a UN address, video and radio interviews.
The complete enrichment now has 9,413 shared publications: 8,526 articles, 881
videos, one audio recording, three accounts, one party page and one portrait page.

Historical indexing reaches 74 registration profiles: 19 presidential, 34 Senate
and 21 deputy registrations. Coverage is partial. It does not establish that
every publication about those people was found, or that the other 8,916
registrations have no history. Two presidential identities still have no
historical index entries. `history-coverage.json` preserves a status for every
registration, including pending research.

## Editorial meaning

Article index entries retain a short publisher headline, original URL, source
name, publication date, source type and candidate-specific relationship. A name
in a headline is distinguished from an article-body mention. Indexed entries do
not claim an editorial summary or independent verification of article claims.
Original headlines retain their source language. Raw bodies stay outside the
public repository.

Recordings have individual URLs. Candidate-linked channels are labeled as
candidate material; third-party archives have a separate source label. Account
homepages are not individual videos. Missing dates remain missing, and upload
dates are separate from source-stated event dates. An archive page whose
recording could not be confirmed carries an availability note. Players load only
after an explicit visitor choice.

Reporting, campaign claims and government statements remain attributed.
Historical administrative sanctions announcements are not criminal convictions,
current sanctions-status checks or CEP candidacy decisions. Registrations still
carry their preliminary status.

## Research and disconfirmation

Public WordPress searches covered all result pages for 132 recorded name queries
across Juno7, Radio Métropole and Rezo Nòdwès. The earliest indexed article is
dated 5 March 2001. Query totals/pages, source hashes, reviewed aliases and
candidate associations are in `candidate-history-provenance.json`. Completing
a query means only that publisher's search was paginated. It does not exhaust
the internet, unindexed archives or alternate spellings. A denied publisher
endpoint was not counted as zero results.

All 8,990 exact registration names were checked against the collected corpus.
Presidential aliases and a few separately sourced legislative aliases supplement
exact names. Related-post blocks, punctuation-separated names and author credits
were tested. Yves Jean / Yves Jean-Bart and names joined across commas disproved
the initial matching approach. The matcher was tightened; unresolved common-name,
longer-name and judicial-role identities were withheld and recorded.

Video research used public individual pages, bounded public searches, a snapshot
of 410 videos on Etzer Emile's linked channel and 300 on Jerry Tardieu's linked
channel. Unrelated people, sport, worship and retail search hits were rejected.
Snapshots and capped searches are not exhaustive YouTube coverage. Upload dates
were checked separately; event years and archive-sidebar dates were not used as
upload dates.

New bilingual copy received independent AI blind review: a Creole-only reading
was saved before English comparison. One definite provenance wording correction
was applied. The final two filter/preview hints also passed. This is not
native-human certification.

## Access and verification

A profile initially includes at most 24 sources. Eight spider-web topics show
complete counts; topic/filter intent loads that candidate's same-origin catalog.
Search, year, source type and headline/mention filters apply to the graph and
list. The graph shows eight source points per page, the list 24 cards. Saved links
can reach old items directly. Native paginated year archives work without
JavaScript and preserve original source links and limitation notes.

The full generator evaluated 21,626 unique artifact paths for all 8,990
registrations. Linux CI performs the full file build and regeneration check.
Data checks cover identity exclusions, source IDs, individual-video URLs, safe
rendering and preliminary status.

Before the final legislative additions, Chromium passed 348 profile cases across
87 profiles, two languages and mobile/desktop layouts, with 2,200 previews and
1,108 topic visits. Every populated topic was exercised; large topics sampled
the first graph page. Separate historical tasks cover 2002/2011 deep links,
year discovery, pagination, empty search, mentions, failed-catalog recovery and
JavaScript-disabled year archives. The largest archive initially loaded 163,325
decoded bytes locally; filtering took 444 ms with sixfold CPU slowdown. These
are browser lab checks, not physical-device research or field Core Web Vitals.

## Continuing coverage

The free, read-only collector writes an ignored editorial queue:

```text
python scripts/collect-candidate-history.py --candidate c-bf5bb68eea8a5b819128 --publisher juno7 --max-pages 5
```

It distinguishes a page cap, request error and completed query. Results never
automatically merge or publish. Review identity, locality, source type, dates and
context before adding entries. Continue pending candidates and other publishers
and social platforms; this corpus is not everything ever published.

```text
python scripts/prepare-candidate-ui-fixtures.py
python scripts/check-candidate-data.py
python scripts/check-candidate-web-ui.py
python scripts/check-candidate-web-edge-cases.py
python scripts/check-candidate-history-ui.py
```

The browser checks accept `--base https://www.ayitisitwayen.org` for production.
