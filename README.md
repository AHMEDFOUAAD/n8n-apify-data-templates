# n8n workflow templates for Apify data Actors

Two tested, import-ready [n8n](https://n8n.io) workflows that pull structured public data through Apify Actors into Google Sheets (and Slack). They use only core n8n nodes (HTTP Request, Code, Google Sheets, Slack), so they work on n8n Cloud and self-hosted without installing community nodes.

> **Disclosure:** I am the author of this template **and** I sell the Apify Actor it calls on the Apify Store (pay-per-event). Every run's first 25 saved results are free, so the template's default settings (25 per run) cost nothing in Actor charges. Beyond that it is pay-per-result; the Actor's Pricing tab on Apify is the authoritative price. Apify's own plan and platform-usage terms apply to your Apify account.

| Template | What it does | Actor (Apify Store) | Example task |
|---|---|---|---|
| [Podcast transcripts to Google Sheets](podcast-transcripts-to-google-sheets/) | Daily: saves the transcripts podcasts already publish in their RSS feeds (Podcasting 2.0 `<podcast:transcript>`) as one row per new episode | [Podcast Transcripts from RSS](https://apify.com/ahmed.fouaad82/podcast-published-transcripts) | [Get published podcast transcripts from an RSS feed](https://apify.com/ahmed.fouaad82/podcast-published-transcripts/examples/podcast-transcripts-from-rss-feed) |
| [Lever salary watch to Google Sheets + Slack](lever-salary-watch-sheets-slack/) | Weekdays: keeps a register of Lever job postings that publish a salary range and posts new ones to Slack, highest paid first | [Lever Jobs Scraper - Salary Ranges & Remote Filters](https://apify.com/ahmed.fouaad82/lever-salary-jobs) | [Lever jobs with salary ranges](https://apify.com/ahmed.fouaad82/lever-salary-jobs/examples/lever-jobs-with-salary-ranges) |

## How they call Apify

Each workflow sends one `POST` to `https://api.apify.com/v2/acts/<actor>/run-sync-get-dataset-items` with an n8n **Header Auth** credential (`Authorization: Bearer <your Apify token>`). The query parameter `maxTotalChargeUsd` is taken from the settings node (`maxCostPerRunUsd`, default `0.10`), so Apify stops charging a run at that limit. No token, credential ID or pinned data is stored in the JSON files.

## Import

1. Download the `workflow.json` of a template (open it, then **Raw**, then save).
2. In n8n: **Workflows -> Import from File** (or paste the JSON onto the canvas).
3. Follow the template's README (also in the yellow sticky note on the canvas).

## How they were tested

Both workflows were imported and executed headlessly in n8n 2.47.3 (Docker `n8nio/n8n`, 2026-11-10) against the live Actors: real Apify runs succeeded with 0 charged events and the cost cap was applied (`isMaxTotalChargeUsdSetByUser: true`). Dedupe, empty-result, invalid-token (error branch) and settings-validation paths were checked. The Google Sheets and Slack nodes were replaced by stand-ins in that test, so do one run against your own sheet first.

## License

MIT. See [LICENSE](LICENSE). Issues and suggestions are welcome.
