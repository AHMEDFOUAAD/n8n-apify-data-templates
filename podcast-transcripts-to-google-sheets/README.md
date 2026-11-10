# Build a podcast transcript library in Google Sheets from RSS feeds (n8n + Apify)

[`workflow.json`](workflow.json) - import into n8n (**Workflows -> Import from File**).

> **Disclosure:** I am the author of this template **and** I sell the Apify Actor it calls on the Apify Store (pay-per-event). Every run's first 25 saved results are free, so the template's default settings (25 per run) cost nothing in Actor charges. Beyond that it is pay-per-result; the Actor's Pricing tab on Apify is the authoritative price. Apify's own plan and platform-usage terms apply to your Apify account.

## What it does

- Reads the podcast RSS feeds you list and collects the transcripts that publishers already attach to episodes (the Podcasting 2.0 `<podcast:transcript>` tag: VTT, SRT, JSON, HTML or text). It does **not** transcribe audio, so it is fast and cheap, but shows that publish no transcript are skipped (Buzzsprout, Omny Studio and many Podcasting 2.0 hosts publish them; many large shows do not).
- Appends one row per **new** episode to Google Sheets: title, date, speakers, word count, transcript link and full text. Episodes are matched on their RSS GUID, so a daily schedule never duplicates rows.
- Transcripts longer than 45,000 characters are cut to fit a Sheets cell (`textTruncated = true`; the full file stays at `transcriptUrl`).
- If the Apify call fails, the workflow stops with the reason and writes nothing.

Flow: Manual / daily 07:00 trigger -> **Podcast settings** -> settings check -> Apify `ahmed.fouaad82~podcast-published-transcripts` -> read saved GUIDs -> keep only new episodes -> append to sheet.

## Setup (about 5 minutes)

1. **Apify:** create a free account at apify.com and copy your API token (Console -> Settings -> API & Integrations). In n8n create a **Header Auth** credential: Name `Authorization`, Value `Bearer <your token>`. Select it in the node **Fetch published transcripts**.
2. **Google Sheets:** connect your Google credential in both Sheets nodes. Create a tab named `Transcripts` whose first row is:
   `guid, publishedAt, podcastTitle, episodeTitle, episodeNumber, durationMinutes, wordCount, speakers, language, transcriptUrl, audioUrl, feedUrl, textTruncated, text, savedAt`
3. In **Podcast settings** set `feedUrls` (one or more RSS URLs) and `spreadsheetId` (the long ID in your sheet's URL). Click **Run now**, check the sheet, then activate the schedule.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `feedUrls` | a Buzzsprout demo feed | RSS feed URLs (comma or newline separated) |
| `maxEpisodesPerFeed` | 3 | Newest episodes checked per feed; raise to backfill |
| `maxTranscriptsPerRun` | 25 | Total transcripts per run; 25 = inside the free slice |
| `publishedSince` | empty | Optional date, e.g. `2026-01-01` |
| `spreadsheetId`, `sheetName` | - / `Transcripts` | Target sheet |
| `maxCostPerRunUsd` | 0.10 | Sent to Apify as `maxTotalChargeUsd` (hard charge cap per run) |

## Cost cap

The first 25 saved transcripts of every run are free; beyond that the Actor charges per saved transcript (at the time of writing $2 per 1,000; check the [Pricing tab](https://apify.com/ahmed.fouaad82/podcast-published-transcripts/pricing)). With the defaults (25 per run, $0.10 cap) a run's Actor charges are $0, and a misconfigured run can never charge more than `maxCostPerRunUsd`.

## Links

- Actor on the Apify Store: https://apify.com/ahmed.fouaad82/podcast-published-transcripts
- Published example task (try it in the browser first): https://apify.com/ahmed.fouaad82/podcast-published-transcripts/examples/podcast-transcripts-from-rss-feed
- Podcasting 2.0 transcript tag: https://podcastindex.org/namespace/1.0#transcript

## Customize

Send the new rows on to a vector store for RAG, add a summary step with an LLM node, or swap Google Sheets for Airtable/Notion.
