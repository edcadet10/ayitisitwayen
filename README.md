# Ayiti Sitwayen

Ayiti Sitwayen is an independent civic information and analysis platform focused
on Haiti. It brings together civic education, election guidance, candidate
records, sourced analysis and clearly labeled opinion in Haitian Creole and
English. Research supports that mission.

Production: https://www.ayitisitwayen.org

The site uses static HTML, CSS, JavaScript and Python generators. Pushing the
reviewed main branch triggers GitHub checks and the connected Vercel deployment.
There is no visitor-facing paid API dependency.

## Content and builds

- `data/elections.json`: reviewed election guidance and source dates.
- `data/candidates/`: registrations, verified enrichment, portraits and archives.
- `data/candidate-editorial.json`: original articles, citations, series and audio.
- `data/about.json`: identity, mission and editorial commitments.
- `data/site-page-dates.json`: genuine revision dates for static pages.

```text
python scripts/build-editorial.py
python scripts/build-candidates.py
python scripts/build-elections.py
python scripts/build-sitemaps.py
python -m http.server 8767 --bind 127.0.0.1
```

Open `http://127.0.0.1:8767/`. Candidate profiles and their catalogs are generated
locally and on Vercel; their large output trees are ignored by Git. The editorial,
About and election landing pages are committed and checked for consistency.
Edit reviewed source data, then regenerate; do not hand-edit generated HTML.

```text
python scripts/check-candidate-data.py
python scripts/check-editorial.py
python scripts/build-editorial.py --check
python scripts/build-candidates.py --check
python scripts/build-elections.py --check
python scripts/build-sitemaps.py --check
python scripts/check-seo.py
node --check editorial.js
```

The article builder enforces a maximum of 500 words in each language, including
headline and deck. Only published entries are emitted; stale article HTML blocks
the build. Native text, citations and metadata remain available without
JavaScript. Sitemaps and metadata support discovery; they do not guarantee Google
indexing or rankings.

Selected articles have labeled ElevenLabs narration, transcripts and controls
without autoplay. Credentials belong in the existing private audio pipeline,
never this repository. Changed Creole transcripts require a new recording.

The About contact form opens the visitor’s email application for review and
manual sending. It does not send mail or imply a configured submission service.

See [editorial/README.md](editorial/README.md) for election maintenance and
[editorial/candidate-analysis-method.md](editorial/candidate-analysis-method.md)
for article sourcing, review and publication requirements.

Contact: contact@ayitisitwayen.org
