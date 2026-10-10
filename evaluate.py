"""Real model check: text query → held-out, manually annotated video segment."""
import json
from engine import ROOT, index_video, search

index=index_video(ROOT/'samples/sample-reel.mp4','Sample reel',print)
cases=json.loads((ROOT/'tests/queries.json').read_text())
report=[]
for case in cases:
    result=search(index['id'],case['query'])
    top=result['results'][0]
    passed=case['start']<=top['timestamp']<case['end']
    report.append({'query':case['query'],'expectedRange':[case['start'],case['end']],'topTimestamp':top['timestamp'],'similarity':top['similarity'],'passed':passed})
    print(f"{'PASS' if passed else 'FAIL'} {case['query']}: {top['timestamp']:.0f}s, cosine {top['similarity']:.3f}")
print(json.dumps(report,indent=2))
assert all(case['passed'] for case in report), 'A top-ranked frame was outside its annotated segment'
