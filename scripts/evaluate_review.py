"""Exploratory real-footage retrieval, including absent-object queries.

This is a diagnostic report, not an accuracy benchmark. Inspect each result
against the actual footage. There is deliberately no tuned score threshold.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import ROOT, index_video, search

report = []
for sample in json.loads((ROOT/'samples/review-catalog.json').read_text()):
    if sample['id'] == 'original':
        continue
    print('\n' + sample['name'], flush=True)
    index = index_video(ROOT/sample['file'], sample['name'], lambda msg: print(msg, flush=True))
    for query in sample['queries']:
        result = search(index['id'], query)
        top = result['results'][0]
        row = {'sample': sample['id'], 'videoId': index['id'], 'query': query,
               'absentObjectControl': query.startswith('a dog'), 'results': result['results']}
        report.append(row)
        print(f"{query}: {top['timestamp']:.0f}s, cosine {top['similarity']:.3f}", flush=True)
destination = ROOT/'runtime/review-evaluation.json'
destination.write_text(json.dumps(report, indent=2))
print(f'\nSaved {destination}', flush=True)
