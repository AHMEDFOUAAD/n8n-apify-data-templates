"""Offline n8n import/execution checks; no service credentials or network access."""
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(sys.argv[1]).resolve()
FIXTURES.mkdir(parents=True, exist_ok=True)
workflows = []
for index, folder in enumerate(['podcast-transcripts-to-google-sheets', 'lever-salary-watch-sheets-slack']):
    w = json.loads((ROOT / folder / 'workflow.json').read_text(encoding='utf-8'))
    names = {n['name'] for n in w['nodes']}
    assert len(names) == len(w['nodes'])
    assert len({n['id'] for n in w['nodes']}) == len(w['nodes'])
    for source, ports in w['connections'].items():
        assert source in names
        for outputs in ports.values():
            for edges in outputs:
                for edge in edges:
                    assert edge['node'] in names and edge['index'] >= 0
    assert not w.get('pinData')
    assert all(not n.get('credentials') for n in w['nodes'])
    w['id'] = f'exact{index}'
    w['active'] = False
    workflows.append(copy.deepcopy(w))
    w['id'] = f'fixture{index}'
    w['name'] += ' [offline fixture]'
    settings = next(n for n in w['nodes'] if n['type'] == 'n8n-nodes-base.set')
    for a in settings['parameters']['assignments']['assignments']:
        if a['name'] == 'spreadsheetId':
            a['value'] = 'test-sheet'
        if a['name'] == 'maxCostPerRunUsd':
            a['value'] = 0
    for n in w['nodes']:
        code = None
        if n['type'] == 'n8n-nodes-base.httpRequest':
            if index == 0:
                data = [{'guid': 'known', 'hasTranscript': True, 'text': 'saved'}, {'guid': 'new', 'hasTranscript': True, 'text': 'a' * 46000}, {'guid': 'new', 'hasTranscript': True, 'text': 'duplicate'}]
            else:
                data = [{'id': key, 'salaryCurrency': currency, 'salaryInterval': interval, 'salaryMin': amount, 'title': 'R&D <!here>', 'board': '<!channel>', 'location': '<https://evil.example|click>', 'url': 'https://jobs.lever.co/acme/123'} for key, currency, interval, amount in [('year-low', 'USD', 'per-year-salary', 50000), ('month-low', 'USD', 'per-month-salary', 10000), ('eur-low', 'EUR', 'per-year-salary', 1000), ('year-high', 'USD', 'per-year-salary', 90000), ('month-high', 'USD', 'per-month-salary', 12000), ('eur-high', 'EUR', 'per-year-salary', 2000)]]
            code = 'return ' + json.dumps(data) + '.map(json => ({json}));'
        elif n['name'] in ['Read saved episodes', 'Read known postings']:
            code = "return [{json: {guid: 'known'}}];" if index == 0 else 'return [{json: {}}];'
        elif n['type'] in ['n8n-nodes-base.googleSheets', 'n8n-nodes-base.slack']:
            if index == 0:
                code = "const rows = $input.all(); if (rows.length !== 1 || rows[0].json.guid !== 'new' || rows[0].json.text.length !== 45000 || !rows[0].json.textTruncated) throw new Error('podcast fixture failed'); return [{json:{fixture:'podcast',passed:true}}];"
            elif n['type'] == 'n8n-nodes-base.slack':
                code = "const text = $input.first().json.text; if (!text.includes('<https://jobs.lever.co/acme/123|R&amp;D &lt;!here&gt;>') || text.includes('<!channel>') || !text.includes('&lt;!channel&gt;')) throw new Error('Slack fixture failed: ' + text); return [{json:{fixture:'slack',passed:true}}];"
            else:
                code = "const ids = $input.all().map(i=>i.json.jobId); if (ids.join(',') !== 'eur-high,eur-low,month-high,month-low,year-high,year-low') throw new Error('salary grouping failed'); return [{json:{fixture:'salary',passed:true}}];"
        if code is not None:
            n['type'] = 'n8n-nodes-base.code'
            n['typeVersion'] = 2
            n['parameters'] = {'jsCode': code}
            n.pop('onError', None)
    check = next(n for n in w['nodes'] if n['name'] == 'Check settings and build input')
    check['parameters']['jsCode'] = check['parameters']['jsCode'].replace('return [{ json: {', "if (maxCostPerRunUsd !== 0) throw new Error('zero cap lost');\nreturn [{ json: {")
    workflows.append(w)
(FIXTURES / 'workflows.json').write_text(json.dumps(workflows), encoding='utf-8')
print('PASS Python JSON and workflow structure: 2 source workflows', flush=True)
cmd = ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'sh',
       '-e', 'N8N_DIAGNOSTICS_ENABLED=false', '-e', 'N8N_VERSION_NOTIFICATIONS_ENABLED=false',
       '-v', f'{FIXTURES.as_posix()}:/fixtures:ro', 'n8nio/n8n:latest', '-c',
       'n8n import:workflow --input=/fixtures/workflows.json && n8n execute --id=fixture0 --rawOutput && n8n execute --id=fixture1 --rawOutput']
result = subprocess.run(cmd, text=True, capture_output=True, timeout=240)
(FIXTURES / 'docker-output.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
print(result.stdout[-14000:])
print(result.stderr[-3000:])
print('Docker exit:', result.returncode)
if result.returncode:
    sys.exit(result.returncode)
for marker in ['"fixture":"podcast","passed":true', '"fixture":"salary","passed":true', '"fixture":"slack","passed":true']:
    assert marker in result.stdout.replace(' ', '').replace('\n', ''), marker
print('PASS exact imports + offline n8n execution fixtures (zero cap, podcast dedupe/truncation, salary units, Slack escaping)')
