# Space Conference Tracker

This repository tracks conferences related to **space**, **LEO**, and **Earth observation**.

The current tracker is centered on three fields:

- conference dates
- early bird deadline
- registration price

It is hosted as a simple Jekyll site and uses `_data/conferences.yaml` as the source of truth.

## What The Site Shows

- upcoming conferences sorted by start date
- archived conferences kept for reference
- conference date range
- early bird deadline status
- registration price snapshot
- focus area, location, and official website
- a homepage submission form that opens a GitHub issue and can be converted into a PR by GitHub Actions

## Data Model

Each conference entry currently uses this shape:

```yaml
- name: SmallSat Conference
  acronym: SmallSat
  focus: LEO / Small Satellites
  conference_start: 03.08.2026
  conference_end: 06.08.2026
  early_bird_deadline: 15.05.2026
  registration_price: USD 895
  location: Logan, Utah, USA
  website: https://example.org
```

Notes:

- `registration_price` is free text because conference pricing is often tiered.
- `conference_end` can match `conference_start` for one-day events.
- unknown values can be left empty, except `website`, `name`, and `acronym`.

## Contributing

Update `_data/conferences.yaml` directly and open a pull request.

You can also use the homepage form. It asks for:

- conference name or acronym
- public event URL

The submission workflow then tries to enrich the entry with:

- conference dates
- early bird deadline
- registration price
- location
- website normalization

If a field cannot be extracted safely, it is left blank or marked `TBD` for later review.

## Run Locally

Prerequisites:

- Ruby
- Bundler

Install dependencies:

```bash
bundle install
```

Start the site:

```bash
bundle exec jekyll serve
```

Then open `http://127.0.0.1:4000/`.

## Automation

The repository still includes a scheduled checker that can review conference pages and propose updates to:

- `conference_start`
- `conference_end`
- `early_bird_deadline`
- `registration_price`
- `location`
- `website`

GitHub setup:

1. Add repository secret `OPENAI_API_KEY` if you want structured extraction.
2. Optional repository variable `OPENAI_MODEL`.
3. Optional repository variable `OPENAI_BASE_URL`.
4. Set GitHub Actions permissions to `Read and write permissions`.
5. Keep GitHub Issues enabled if you want homepage submissions to create PRs.

Local agent run:

```bash
python3 -m pip install -r scripts/requirements-conference-agent.txt
python3 scripts/conference_agent.py \
  --search-fallback \
  --report-file /tmp/conference-agent-report.md
```
