"""Download public research footage and prepare three short local review samples.

Run from any directory: python3 scripts/prepare_review_samples.py
No pip dependencies. Media stays in ignored runtime/.
"""
import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('lobby', 'https://homepages.inf.ed.ac.uk/rbf/CAVIARDATA1/LeftBag/LeftBag.mpg', None),
    ('parking', 'https://mevadata-public-01.s3.amazonaws.com/drops-123-r13/2018-03-13/17/2018-03-13.17-10-03.17-15-03.school.G424.r13.avi', 'bytes=0-16777215'),
    ('retail', 'https://homepages.inf.ed.ac.uk/rbf/CAVIARDATA2/EnterExitCrossingPaths1cor/EnterExitCrossingPaths1cor.mpg', None),
]

def main():
    output = ROOT/'runtime/demo'
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    with tempfile.TemporaryDirectory() as temporary:
        for identity, url, byte_range in SOURCES:
            print('Preparing ' + identity, flush=True)
            source = Path(temporary)/(identity + Path(url).suffix)
            req = urllib.request.Request(url, headers={'Range': byte_range} if byte_range else {})
            with urllib.request.urlopen(req, timeout=120) as response:
                data = response.read()
            source.write_bytes(data)
            target = output/(identity+'.mp4')
            # A contiguous opening segment; no fabricated events or frame rearrangement.
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),
                '-t','30','-an','-vf',"scale=w='min(960,iw)':h=-2",'-c:v','libx264','-preset','veryfast',
                '-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
            manifest.append({'id':identity,'url':url,'requestedByteRange':byte_range,
                'downloadSha256':hashlib.sha256(data).hexdigest(),
                'outputSha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (output/'sources.json').write_text(json.dumps(manifest, indent=2))
    print('Samples ready. Restart the app if it was already open.', flush=True)

if __name__=='__main__':
    main()
