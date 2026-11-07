# Election information maintenance

The reviewed source of public election facts is `data/elections.json`. The two
hub pages and status summaries are generated HTML, so dates, sources and actions
remain available without JavaScript. Edit the data, then run:

The election hub is currently the site's landing page at `/` and `/en/`.
The original project introduction, mission and contact information are preserved
at `/about.html` and `/en/about.html`. The generator owns the landing pages as
well as the existing election URLs, keeping all four routes consistent.

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
