# Election information maintenance

The reviewed source of public election facts is `data/elections.json`. The two
hub pages and status summaries are generated HTML, so dates, sources and actions
remain available without JavaScript. Edit the data, then run:

The election hub is currently the site's landing page at `/` and `/en/`.
The original project introduction, mission and contact information are preserved
at `/about.html` and `/en/about.html`. The generator owns the landing pages as
well as the existing election URLs, keeping all four routes consistent.

Election information is presented as native HTML with source-name credits.
The centre finder and political-structure directory are generated from
`data/voting-centres.json` and `data/approved-parties.json`. Preserve official
names and addresses as supplied; a listed centre does not establish an
individual's registration or voting assignment. Public pages do not link to
source documents or document viewers. Source URLs and fingerprints remain in
the editorial data for verification. Collection also checks the two directory
sources for changes; it never updates public records without review.

```text
python scripts/build-elections.py
python scripts/build-elections.py --check
```

The GitHub workflow collects public CEP notices and changes to the calendar
twice daily at 04:17 and 16:17 UTC. It can also be run manually. Its artifact is
`cep-editorial-review`. The workflow has read-only repository permissions and
never approves, commits or publishes website content. GitHub schedules may run
late; this is discovery, not an assurance that the site is always current.

To collect locally:

```text
python scripts/collect-cep-updates.py
```

Read each changed notice and attachment before updating public guidance. A
notice's source ID and body matter: some source URLs have mismatched topic names.
The calendar is scanned, so review dates visually against its numbered rows.
Keep online candidacy registration, document filing, voter registration and
party membership separate. Registration statistics are preliminary, not final
approved candidacies or election results. A centre directory is not evidence of
an individual's registration or voting assignment. Do not infer that scheduled
activities occurred just because their dates passed.

Only reviewed updates belong in the public JSON. Record the real review date;
fetching a source never advances it. Check both language pages, associated lesson
copy and quizzes, audio scripts and links. The page displays a warning after
seven days without an editorial review when JavaScript is available. The actual
review date is always present in static HTML. Failed collection preserves all
reviewed website content and produces a failing workflow plus an error artifact.

After editorial review of the collected sources, the optional command below
accepts their IDs/hashes as the next discovery baseline. It does not edit website
copy or review dates:

```text
python scripts/collect-cep-updates.py --write-baseline
```

Audio text is in `data/election-audio.json`; published transcripts accompany the
players. ElevenLabs narration is labeled as generated audio. Never place API keys
in this repository. The existing human-recorded evergreen clips are preserved.


## Candidate directory and source webs

The candidate directory lives at `/candidates/` and `/en/candidates/`. The older
`candidates.html` pages remain educational guides. The election landing page
links prominently to the directory. White is the main color throughout the
directory, profiles and spider webs.

`data/candidates/registry.json` is the reviewed snapshot of 8,990 public CEP
registrations captured on 6 November 2026. Totals reconcile across president,
senate, deputy, mayor, CASEC and ASEC, and there are no identical source rows.
All are labeled preliminary. Source records do not contain portraits or stable
IDs. Persistent registration IDs were assigned once and saved; never recompute
them when a name, party or locality changes. Reconcile changed rows manually.
Do not merge people by name or infer withdrawal from an absent row. Do not
convert a press report into a CEP validation or rejection decision.

`data/candidates/enrichment.json` stores reviewed publications once and links
profiles by source ID. It also records portrait provenance and source contexts.
The non-registry archive now has 29 source records across 33 registrations;
portrait provenance also appears as a source in each candidate's web. These
sources describe the credited photo context rather than inventing an article
summary or endorsing party statements. The portrait review of 7 November adds
29 portraits, for 31 total:
19 presidential, nine deputy and three municipal registrations. Two presidential
registrations and most local registrations still need a verified portrait.
Coverage is incomplete. Three links are
campaign-linked social accounts, not individual posts. Unknown publication or
photograph dates remain unknown. Source counts are never a candidate score.

Portrait sources include candidate sites, the MPH party's named candidate cards,
and named press coverage. `editorial/candidate-portrait-provenance.json` preserves
each identity context, source and asset URLs, original image hash, crop bounds
and delivery sizes. Party membership, office and locality were checked before
attaching local portraits; a party card with no matching registration was excluded.
Do not confuse Jean Ernest Muscadin with André Muscadin. A press photo is never
labeled an official current-election portrait without evidence. The Salomon
portrait is labeled archival; other unknown capture dates remain unknown.

Cards use locally hosted 160 × 200, 320 × 400 and 480 × 600 WebP crops, with
responsive selection and loading only when visible. Profiles use a separate
192 × 192 crop in the web centre. The gallery names the photo source; profiles
link to it and describe its context. Crop, resize and encoding preserve the
published person and surroundings; there is no generated face, facial retouching
or identity matching from face detection. The original large files stay outside
the public build. Every card variant is below 35,000 bytes and every web-centre
image below 18,000 bytes. These are asset limits, not field performance claims.

Generate the static HTML profiles, office lists, compact search catalogs and
candidate sitemap using Python standard library only:

```text
python scripts/build-candidates.py
python scripts/build-candidates.py --check
python scripts/build-elections.py --check
```

Vercel runs the candidate generator during its build. Generated output is
ignored by Git to avoid committing thousands of duplicate HTML files. All
reviewed inputs, assets, scripts and styles are committed. Build output remains
static: visitors do not query the CEP or a paid service to open a profile.
Profiles and office pagination remain readable without JavaScript.

The public collector is discovery only:

```text
python scripts/collect-candidates.py
```

Its default output is `editorial/candidate-review-queue.json`, never the reviewed
registry. It validates pagination and office totals before producing a complete
queue. Source failures leave reviewed website content unchanged. Review names,
identity links, source types, dates, corrections and portrait provenance before
accepting updates. The initial importer deliberately refuses to overwrite an
existing reviewed registry; subsequent changes need identity reconciliation.

Public Facebook, Instagram and TikTok material is authorized for portrait
discovery. Verify the person and account relationship, keep the original post
link/date/account credit and check suitable editorial use. A current campaign
portrait is preferred; do not silently relabel an old or undated photo as an
official current-election portrait. Use an honest missing-photo state rather
than inventing faces or using another person's image.

Spider webs use SVG strands and HTML controls, without a graph library or
continuous physics. The source archive is native HTML; hover/focus/tap previews
read the already-reviewed page data. Only explicit Play creates a YouTube
privacy-enhanced iframe. Do not add remote frames or publisher fetches on hover,
unsafe HTML from collected sources, public PDF links, or automatic publication.

The Kreyol UI and source-summary copy received separate blind AI reviews before
publication; it is not described as native-human certification. Lab browser
checks cover narrow layouts, touch/keyboard access, source previews, directory
filters, language identity, Back restoration and JavaScript-disabled pages.
Physical-device usability and field Core Web Vitals remain unmeasured.

The 7 November spider-web usability review found that mobile source actions
opened below the screen, multiple source points had identical publisher labels,
and Back left stale source fragments. Mobile source previews now use a native
dialog with a close control, contained keyboard focus and focus restoration.
Desktop previews remain alongside the web; an explicit source choice stays
selected while the pointer crosses other points. Empty topics are disabled and
explained, and registry-only webs disclose their limited coverage. Source points
use distinct titles. Saved links retain the candidate, source and topic.
The registration preview includes its actual office, party, locality, position
and status, while preliminary status also remains visible above the web.

Seventeen photo-credit-only source previews were revised from the credited
source material into useful article or campaign-page summaries. Three newspaper
previews use only the public excerpt and disclose the account requirement for
the full article. Social account links are labeled as accounts; photo pages and
party presentations have their own format labels. The native archive preserves
these labels and excerpt notes without JavaScript. The new bilingual strings
received a blind independent AI review; its proper-name correction was applied.

Repeat the rendered UI tasks after generating the static pages (requires the
optional Playwright Python package and its Chromium browser):

```text
python scripts/check-candidate-web-ui.py
python scripts/check-candidate-web-edge-cases.py
python scripts/check-candidate-web-ui.py --base https://www.ayitisitwayen.org
python scripts/check-candidate-web-edge-cases.py --base https://www.ayitisitwayen.org
```

The main audit covers all 33 enriched profiles and a registry-only profile in
each remaining office, in both languages on 390px and 1280px viewports: 152
profile cases, 376 source previews and 356 topic visits. Additional checks cover
320px, short landscape screens, keyboard focus, source sharing, language changes,
missing links, player cleanup and a clearly synthetic nine-source pagination
fixture. Browser evidence is written to a temporary folder, outside the public
site. These checks are browser automation, not a human usability study, and do
not represent 8,990 individually observed browser sessions. The complete static
build still checks every generated registration profile in CI.
