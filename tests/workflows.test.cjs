const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = process.env.WORKFLOW_ROOT || path.resolve(__dirname, '..');
const podcast = JSON.parse(fs.readFileSync(path.join(root, 'podcast-transcripts-to-google-sheets/workflow.json')));
const lever = JSON.parse(fs.readFileSync(path.join(root, 'lever-salary-watch-sheets-slack/workflow.json')));
const node = (w, name) => w.nodes.find(n => n.name === name);
test('podcast: read only GUID column A:A and retain header mapping', () => {
  assert.deepEqual(node(podcast, 'Read saved episodes').parameters.options.dataLocationOnSheet,
    { values: { rangeDefinition: 'specifyRangeA1', range: 'A:A' } });
  const rows = run(podcast, 'Keep only new episodes', [{ guid: 'known' }], {
    'Fetch published transcripts': [
      { guid: 'known', hasTranscript: true, text: 'saved' },
      { guid: 'new', hasTranscript: true, text: 'new text' },
      { guid: 'new', hasTranscript: true, text: 'duplicate' },
    ],
  });
  assert.deepEqual(rows.map(i => i.json.guid), ['new']);
});
test('lever: group salary currencies and intervals, rank only within a group', () => {
  const job = (id, currency, interval, salaryMin) => ({ id, salaryCurrency: currency, salaryInterval: interval, salaryMin });
  const jobs = [job('year-low', 'USD', 'per-year-salary', 50000), job('month-low', 'USD', 'per-month-salary', 10000),
    job('eur-low', 'EUR', 'per-year-salary', 1000), job('year-high', 'USD', 'per-year-salary', 90000),
    job('month-high', 'USD', 'per-month-salary', 12000), job('eur-high', 'EUR', 'per-year-salary', 2000)];
  const rows = run(lever, 'Keep new postings and format salary', [], { 'Fetch Lever jobs with salaries': jobs });
  assert.deepEqual(rows.map(i => i.json.jobId), ['eur-high', 'eur-low', 'month-high', 'month-low', 'year-high', 'year-low']);
});
test('lever: Slack escapes scraped fields and rejects injected link markup', () => {
  const row = { jobUrl: 'https://jobs.lever.co/acme/123', title: 'R&D <!here>', board: '<!channel>',
    location: '<https://evil.example|click>', workplaceType: 'remote & hybrid', salaryRange: 'USD <50000>' };
  const text = run(lever, 'Build Slack digest', [row])[0].json.text;
  assert.ok(text.includes('<https://jobs.lever.co/acme/123|R&amp;D &lt;!here&gt;>'));
  assert.ok(text.includes('&lt;!channel&gt;'));
  assert.ok(text.includes('&lt;https://evil.example|click&gt;'));
  assert.ok(text.includes('remote &amp; hybrid'));
  assert.ok(text.includes('USD &lt;50000&gt;'));
  assert.ok(!text.includes('<!channel>'));
  for (const jobUrl of ['javascript:alert(1)', 'https://jobs.lever.co/acme/123|x><!channel>']) {
    const unsafe = run(lever, 'Build Slack digest', [{ ...row, jobUrl }])[0].json.text;
    assert.ok(!unsafe.includes('<!channel>'));
    assert.ok(!unsafe.includes('<javascript:'));
  }
});
function run(w, name, input = [], upstream = {}) {
  return new Function('$input', '$', node(w, name).parameters.jsCode)(
    { all: () => input.map(json => ({ json })) },
    name => ({ first: () => ({ json: upstream[name] }), all: () => upstream[name].map(json => ({ json })) }),
  );
}
for (const [label, w, settings] of [['podcast', podcast, 'Podcast settings'], ['lever', lever, 'Job watch settings']]) {
  test(`${label}: zero cap stays zero; missing defaults; invalid cap stops`, () => {
    const base = Object.fromEntries(node(w, settings).parameters.assignments.assignments.map(a => [a.name, a.value]));
    base.spreadsheetId = 'test-sheet';
    for (const value of [0, '0', 0.25, undefined, null]) {
      const result = run(w, 'Check settings and build input', [], { [settings]: { ...base, maxCostPerRunUsd: value } });
      assert.equal(result[0].json.maxCostPerRunUsd, value == null ? 0.1 : Number(value));
    }
    for (const value of [-1, 'invalid', Infinity]) {
      assert.throws(() => run(w, 'Check settings and build input', [], { [settings]: { ...base, maxCostPerRunUsd: value } }), /maxCostPerRunUsd/);
    }
    const fetch = w.nodes.find(n => n.type === 'n8n-nodes-base.httpRequest');
    const cap = fetch.parameters.queryParameters.parameters.find(p => p.name === 'maxTotalChargeUsd');
    assert.ok(cap.value.includes('.maxCostPerRunUsd'));
  });
}
