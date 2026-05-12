# SaaS Help Center GEO Optimizer Architecture

## Intent

This repo turns a help-center export into a GEO scoring workflow that content,
support, and growth teams can act on quickly.

It focuses on the qualities AI answer systems care about most:

- clear entity naming
- structured headings
- FAQ readiness
- schema coverage
- citation-bait content structure
- freshness

## Flow

1. `app/data/sample_help_center.json` provides a realistic SaaS help-center export.
2. `app/services/geo_service.py` scores each article and builds a prioritized fix queue.
3. `app/main.py` exposes HTML proof routes and JSON APIs.
4. `app/render.py` generates the README proof pages.
5. `scripts/render_readme_assets.py` captures PNG screenshots from those static proof pages.

## Routes

- `/`
  - overview surface and GEO posture summary
- `/queue`
  - prioritized content fix queue
- `/evidence`
  - article-level proof and score breakdown
- `/api-summary`
  - sample API payload and integration story
- `/api/dashboard/summary`
  - top-level score summary
- `/api/articles`
  - all scored articles
- `/api/articles/{slug}`
  - single article breakdown
- `/api/sample`
  - compact payload for demos and smoke checks

## Why It Matters

Most help centers were written for human search, not answer engines. This repo
gives SaaS teams a way to measure whether support content is structured well
enough for:

- AI Overviews
- chatbot citations
- internal support copilots
- assistant-style answer summaries

## Validation

- `py -3.11 -m unittest discover -s tests`
- `py -3.11 scripts\run_demo.py`
- `py -3.11 scripts\smoke_check.py`
- `py -3.11 scripts\render_readme_assets.py`
