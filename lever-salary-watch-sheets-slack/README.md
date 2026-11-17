# Track salary ranges on Lever job boards in Google Sheets and Slack (n8n + Apify)

[`workflow.json`](workflow.json) - import into n8n (**Workflows -> Import from File**).

> **Disclosure:** I am the author of this template **and** I sell the Apify Actor it calls on the Apify Store (pay-per-event). Every run's first 25 saved results are free, so the template's default settings (25 per run) cost nothing in Actor charges. Beyond that it is pay-per-result; the Actor's Pricing tab on Apify is the authoritative price. Apify's own plan and platform-usage terms apply to your Apify account.

## What it does

- Watches the Lever job boards you list (your own or competitors') through Lever's public postings API and keeps only postings that publish a numeric salary.
- Builds a salary register in Google Sheets: title, team, location, remote/hybrid, min, max, currency, pay interval, link, first-seen date. Postings are matched by Lever posting ID, so repeated runs add only new jobs (on the first run every matching posting counts as new).
- Posts one Slack digest of the new postings, grouped by currency and pay interval, highest paid first within each group (max 15 lines + "N more").
- If the Apify call fails, the workflow stops with the reason and changes nothing.

Use it for compensation benchmarking, recruiting research or a pay-transparent job alert.

Flow: Manual / weekdays 08:00 trigger -> **Job watch settings** -> settings check (board URL -> slug, EU boards rejected) -> Apify `ahmed.fouaad82~lever-salary-jobs` -> read known posting IDs -> keep new postings and format salary -> append to sheet -> Slack digest.

## Setup (about 5 minutes)

1. **Apify:** create a free account at apify.com and copy your API token. In n8n create a **Header Auth** credential: Name `Authorization`, Value `Bearer <your token>`. Select it in the node **Fetch Lever jobs with salaries**.
2. **Google Sheets:** connect your credential in both Sheets nodes and create a tab `Salary watch` with this header row:
   `jobId, board, title, team, department, location, workplaceType, commitment, salaryMin, salaryMax, salaryCurrency, salaryInterval, salaryRange, postedAt, jobUrl, firstSeenAt`
3. **Slack:** connect your Slack credential and set `slackChannel`.
4. In **Job watch settings** enter Lever board slugs (the `acme` in `https://jobs.lever.co/acme`) or board URLs, then click **Run now** and check the sheet.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `leverBoards` | `leverdemo` (Lever's demo board) | Board slugs or URLs, comma separated |
| `minSalary` | 0 | Published minimum floor; 0 disables it |
| `salaryCurrency`, `salaryInterval` | `USD`, `per-year-salary` | Used only when `minSalary` > 0; exact match, no currency conversion |
| `remoteOnly` | false | Keep only postings the employer marks remote |
| `maxJobsPerRun` | 25 | 25 = inside the free slice |
| `spreadsheetId`, `sheetName` | - / `Salary watch` | Target sheet |
| `slackChannel` | `#jobs` | Digest channel |
| `maxCostPerRunUsd` | 0.10 | Sent to Apify as `maxTotalChargeUsd` (hard charge cap per run) |

Global Lever boards only; `jobs.eu.lever.co` boards are not supported. Salary values are what employers publish on Lever, not verified offers.

## Cost cap

The first 25 saved jobs of every run are free; beyond that the Actor charges per saved job (at the time of writing $2 per 1,000; check the [Pricing tab](https://apify.com/ahmed.fouaad82/lever-salary-jobs/pricing)). With the defaults (25 per run, $0.10 cap) a run's Actor charges are $0, and a misconfigured run can never charge more than `maxCostPerRunUsd`.

## Links

- Actor on the Apify Store: https://apify.com/ahmed.fouaad82/lever-salary-jobs
- Published example task (try it in the browser first): https://apify.com/ahmed.fouaad82/lever-salary-jobs/examples/lever-jobs-with-salary-ranges
