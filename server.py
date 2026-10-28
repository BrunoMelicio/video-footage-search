import json
import mimetypes
import os
import re
import tempfile
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from engine import ROOT, RUNTIME, MODEL, index_video, public_index, request, search

MAX_UPLOAD = 50*1024*1024
JOBS = {}
JOBS_LOCK = threading.Lock()
WORKER = ThreadPoolExecutor(max_workers=1)

def review_samples():
    return [item for item in json.loads((ROOT/'samples/review-catalog.json').read_text()) if (ROOT/item['file']).is_file()]

def selected_sample(parsed, default='original'):
    identity = parse_qs(parsed.query).get('id',[default])[0]
    return next((item for item in review_samples() if item['id']==identity),None)

def update_job(identity, **values):
    with JOBS_LOCK:
        JOBS[identity].update(values)

def start_job(source, name, cleanup=False):
    with JOBS_LOCK:
        if any(job['state'] in ('queued','indexing') for job in JOBS.values()):
            raise ValueError('A video is indexing. Wait for it to finish.')
        identity = uuid.uuid4().hex
        JOBS[identity] = {'state':'queued','message':'Waiting to index'}
    def work():
        try:
            update_job(identity,state='indexing')
            index = index_video(source,name,lambda message:update_job(identity,message=message))
            update_job(identity,state='ready',message='Video ready',video=public_index(index))
        except Exception as error:
            update_job(identity,state='error',message=str(error))
        finally:
            if cleanup:
                source.unlink(missing_ok=True)
    WORKER.submit(work)
    return identity

class Handler(BaseHTTPRequestHandler):
    def json(self, value, status=200):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path=='/api/samples':
            return self.json({'samples':[{key:value for key,value in item.items() if key!='file'} for item in review_samples()]})
        if parsed.path=='/api/status':
            try:
                models = request('/api/tags').get('models',[])
                return self.json({'model':MODEL,'ready':any(m['name']==MODEL for m in models)})
            except RuntimeError as error:
                return self.json({'model':MODEL,'ready':False,'error':str(error)})
        if parsed.path=='/api/job':
            identity = parse_qs(parsed.query).get('id',[''])[0]
            with JOBS_LOCK:
                job = dict(JOBS.get(identity,{}))
            return self.json(job if job else {'error':'Unknown job'},200 if job else 404)
        if parsed.path.startswith('/media/'):
            root = RUNTIME
            relative = unquote(parsed.path[len('/media/'):])
            # Only indexed player media and thumbnails may be served.
            if not re.fullmatch(r'[a-f0-9]{24}/(?:video\.mp4|frames/frame-\d{3}\.jpg)',relative):
                return self.json({'error':'Not found'},404)
        elif parsed.path=='/sample-preview.mp4':
            sample = selected_sample(parsed)
            if sample is None:
                return self.json({'error':'Unknown sample'},404)
            return self.file(ROOT/sample['file'])
        else:
            root = ROOT/'static'
            relative = unquote(parsed.path).lstrip('/') or 'index.html'
        path = (root/relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            return self.json({'error':'Not found'},404)
        return self.file(path)

    def file(self, path):
        size = path.stat().st_size
        start, end, status = 0, size-1, 200
        ranges = self.headers.get('Range')
        if ranges:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)',ranges)
            if not match or not any(match.groups()):
                self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.end_headers(); return
            first,last = match.groups()
            if first:
                start=int(first); end=min(int(last),size-1) if last else size-1
            else:
                start=max(0,size-int(last))
            if start>end or start>=size:
                self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.end_headers(); return
            status=206
        self.send_response(status)
        self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(end-start+1))
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Cache-Control','no-cache')
        if status==206:
            self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with path.open('rb') as source:
                source.seek(start); remaining=end-start+1
                while remaining>0:
                    chunk=source.read(min(65536,remaining))
                    if not chunk: break
                    self.wfile.write(chunk); remaining-=len(chunk)
        except (BrokenPipeError,ConnectionResetError):
            pass

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        source = None
        try:
            if path=='/api/sample':
                sample = selected_sample(parsed)
                if sample is None:
                    return self.json({'error':'Unknown sample'},404)
                return self.json({'jobId':start_job(ROOT/sample['file'],sample['name'])},202)
            length = int(self.headers.get('Content-Length','0'))
            if path=='/api/upload':
                if not 0<length<=MAX_UPLOAD:
                    return self.json({'error':'Choose a video under 50 MB'},413)
                RUNTIME.mkdir(exist_ok=True)
                handle=tempfile.NamedTemporaryFile(dir=RUNTIME,suffix='.upload',delete=False)
                source=Path(handle.name)
                with handle:
                    remaining=length
                    while remaining:
                        data=self.rfile.read(min(65536,remaining))
                        if not data: raise ValueError('Incomplete upload')
                        handle.write(data); remaining-=len(data)
                name=unquote(self.headers.get('X-Filename','Uploaded video')).replace('\n',' ')[:120]
                identity=start_job(source,name,cleanup=True)
                source=None
                return self.json({'jobId':identity},202)
            if path=='/api/search':
                if not 0<length<=4096:
                    return self.json({'error':'Invalid search request'},400)
                payload=json.loads(self.rfile.read(length))
                return self.json(search(payload['videoId'],payload['query']))
            return self.json({'error':'Unknown endpoint'},404)
        except (ValueError,KeyError) as error:
            return self.json({'error':str(error)},400)
        except Exception as error:
            return self.json({'error':str(error)},503)
        finally:
            if source: source.unlink(missing_ok=True)

if __name__=='__main__':
    port=int(os.environ.get('PORT','8001'))
    RUNTIME.mkdir(exist_ok=True)
    print(f'Auto-Surveillance: http://localhost:{port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
