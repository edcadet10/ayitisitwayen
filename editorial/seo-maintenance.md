# Search discovery and SEO

The sitemap index at `/sitemap.xml` covers canonical public HTML pages in four
maps: the static site, candidate profiles, directory pages and source archives.
The 7 November 2026 release has 21,659 canonical URLs: 63 static pages, 17,980
bilingual profiles, 1,504 directory pages and 2,112 archive pages. Earlier sitemap
coverage omitted the archives, paginated directories and audio transcript page.

Candidate search titles and descriptions identify the person, the candidacy,
office, locality and preliminary registration status. Directory titles vary by
office/page; archive titles vary by person, year and page. Neither candidacy
metadata nor Person markup asserts that a registrant holds the office or has
received CEP validation. External article/video indexes are not represented as
original reporting or as dedicated video watch pages.

Each canonical page has its own URL; later pagination pages do not canonicalize
to page one. The duplicate presidential landing aliases canonicalize to the main
candidate directory. Existing election/home aliases retain their canonical home
URLs and are omitted from the sitemap. Creole and English versions have reciprocal
language links. Profile metadata uses WebPage/about Person; Google ProfilePage
rich-result markup is not appropriate for this third-party directory. Home pages
describe the site and publisher with WebSite and Organization markup. Schema
breadcrumbs reflect the real directory/profile/archive hierarchy.

`data/site-seo.json` has bilingual metadata templates and a deliberate content
revision date. New templates received an independent AI blind Creole/English
review; all nine passed. `data/site-page-dates.json` preserves declared static
page update dates. Candidate sitemap dates take the latest relevant data review
or metadata revision. Builds do not reset every date to today's date. Update
these dates when the underlying content/metadata meaningfully changes.

Raw data, editorial files and build scripts receive an HTTP `X-Robots-Tag:
noindex` header. They remain fetchable so browser features and rendering work.
Public HTML pages are not covered by those headers. Google's verification file
is retained. `robots.txt` advertises the sitemap index and allows public crawling.

After changing content/templates:

```text
python scripts/build-candidates.py
python scripts/build-elections.py
python scripts/build-sitemaps.py
python scripts/check-candidate-data.py
python scripts/check-seo.py
```

The SEO check evaluates every generated HTML page, requires complete canonical
sitemap coverage, checks language links and JSON-LD, rejects duplicate search
titles, and verifies the sitemap index and indexing headers. CI repeats the full
build/regeneration and SEO checks. No paid search/indexing service is used.

Submit `/sitemap.xml` in the verified Search Console property after deployment.
The component maps can also be submitted to monitor discovery separately. For
a large batch, submit sitemaps rather than trying to individually request every
URL. Google's Indexing API is limited to supported job-posting/livestream pages
and is not used for this directory. The retired sitemap-ping endpoint is not used.
Sitemap acceptance, URL discovery, crawling and actual indexing are different
states; never describe submission as confirmation that all URLs are indexed.

Primary references:

- [Build and submit sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Sitemap indexes](https://developers.google.com/search/docs/crawling-indexing/sitemaps/large-sitemaps)
- [Titles](https://developers.google.com/search/docs/appearance/title-link)
- [Language versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Pagination](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)
- [Request recrawling](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)

## Candidate profile discovery update, 15 November 2026

Verified portrait profiles now use their own image and name in Open Graph and
Twitter image metadata. Unpictured profiles retain the site-logo fallback. Five
published name forms have visible, source-linked attribution and matching Person
alternateName metadata; directory search recognizes those same forms. The main
presidential directory links every current presidential registration by name in a
complete native alphabetical index, including entries beyond the first gallery
page. IDs and canonical URLs remain stable.

`candidate_revision` in `data/site-seo.json` records this deliberate candidate
template/metadata revision. `content_revision` remains the floor for the shared
election guides. Do not advance either value solely because a build ran.

These changes improve identification, browsing and descriptive metadata. Their
ranking impact requires later Search Console measurement; no rich result,
Knowledge Panel, Discover placement or universal search position is promised.
