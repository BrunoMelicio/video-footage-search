"""Image-frame indexing and cross-modal retrieval. No pip dependencies."""
import base64
import hashlib
import json
import math
import os
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / 'runtime'
MODEL = os.environ.get('EMBED_MODEL', 'embeddinggemma-2:440m')
OLLAMA = os.environ.get('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
INTERVAL = 2.0
MAX_DURATION = 120
QUERY_PREFIX = 'task: search result | query: '
MODEL_LOCK = threading.Lock()

def request(path, payload=None):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode() if payload is not None else None, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('Ollama: ' + error.read().decode()[:300]) from error
    except urllib.error.URLError as error:
        raise RuntimeError('Start Ollama and download ' + MODEL) from error

def normalize(vector):
    if not vector or not all(isinstance(v, (float,int)) and math.isfinite(v) for v in vector):
        raise ValueError('Invalid model vector')
    norm = math.sqrt(sum(v*v for v in vector))
    if not norm:
        raise ValueError('Zero model vector')
    return [v/norm for v in vector]

def embed(item):
    with MODEL_LOCK:
        result = request('/api/embed', {'model':MODEL, 'input':item})
    vectors = result.get('embeddings', [])
    if len(vectors) != 1:
        raise ValueError('Expected one embedding; update Ollama for multimodal support')
    return normalize(vectors[0])

def model_digest():
    model = next((m for m in request('/api/tags').get('models',[]) if m['name']==MODEL), None)
    if model is None:
        raise RuntimeError('Run: ollama pull ' + MODEL)
    return model['digest']

def run(command, timeout=120):
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError('Video processing failed: ' + result.stderr[-500:])
    return result.stdout

def probe(path):
    tool = shutil.which('ffprobe')
    if not tool:
        raise RuntimeError('Install FFmpeg (including ffprobe) first')
    metadata = json.loads(run([tool,'-v','error','-protocol_whitelist','file,pipe','-show_entries','format=duration:stream=codec_type','-of','json',str(path)]))
    if not any(s.get('codec_type')=='video' for s in metadata.get('streams',[])):
        raise ValueError('File does not contain a video stream')
    duration = float(metadata.get('format',{}).get('duration',0))
    if not math.isfinite(duration) or not 0 < duration <= MAX_DURATION:
        raise ValueError(f'Choose a video between 0 and {MAX_DURATION} seconds')
    return duration

def timestamps(duration, interval=INTERVAL):
    if not math.isfinite(duration) or duration<=0 or not math.isfinite(interval) or interval<=0:
        raise ValueError('Invalid duration or sampling interval')
    return [i*interval for i in range(math.ceil(duration/interval))]

def index_video(source, name, progress=lambda message: None):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('Install FFmpeg first')
    duration = probe(source)
    digest = model_digest()
    identity = hashlib.sha256(source.read_bytes() + (MODEL+digest+str(INTERVAL)+'v1').encode()).hexdigest()[:24]
    directory = RUNTIME / identity
    cache = directory / 'index.json'
    if cache.exists():
        progress('Using cached frame embeddings')
        result = json.loads(cache.read_text())
        result['name'] = name
        return result
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'frames').mkdir(exist_ok=True)
    progress('Preparing a browser-compatible video')
    run([ffmpeg,'-v','error','-y','-protocol_whitelist','file,pipe','-i',str(source),'-map','0:v:0','-an','-vf','scale=720:720:force_original_aspect_ratio=decrease:force_divisible_by=2','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(directory/'video.mp4')])
    frames = []
    times = timestamps(duration)
    for i, time in enumerate(times):
        progress(f'Embedding frame {i+1} of {len(times)}')
        filename = f'frame-{i:03d}.jpg'
        path = directory/'frames'/filename
        run([ffmpeg,'-v','error','-y','-ss',str(time),'-i',str(directory/'video.mp4'),'-frames:v','1','-q:v','3',str(path)],timeout=30)
        vector = embed({'image':base64.b64encode(path.read_bytes()).decode()})
        frames.append({'timestamp':time,'thumbnail':f'/media/{identity}/frames/{filename}','embedding':vector})
    result = {'id':identity,'name':name,'duration':duration,'interval':INTERVAL,'model':MODEL,'modelDigest':digest,'video':f'/media/{identity}/video.mp4','frames':frames}
    temp = cache.with_suffix('.tmp')
    temp.write_text(json.dumps(result))
    temp.replace(cache)
    return result

def load_index(identity):
    if len(identity)!=24 or any(c not in '0123456789abcdef' for c in identity):
        raise ValueError('Invalid video ID')
    path = RUNTIME/identity/'index.json'
    if not path.exists():
        raise ValueError('Load and index a video first')
    return json.loads(path.read_text())

def public_index(index):
    return {key:index[key] for key in ('id','name','duration','interval','model','video')} | {'frameCount':len(index['frames']), 'poster':index['frames'][0]['thumbnail']}

def rank_frames(frames, query, limit=5, separation=4):
    if any(len(frame['embedding'])!=len(query) for frame in frames):
        raise ValueError('Text and image embedding dimensions differ')
    candidates = sorted(({'timestamp':f['timestamp'],'thumbnail':f['thumbnail'],'similarity':sum(a*b for a,b in zip(query,f['embedding']))} for f in frames), key=lambda f:f['similarity'],reverse=True)
    selected = []
    for frame in candidates:
        if all(abs(frame['timestamp']-other['timestamp'])>=separation for other in selected):
            selected.append(frame)
            if len(selected)==limit:
                break
    return selected

def search(identity, query):
    if not isinstance(query,str) or not query.strip() or len(query)>500:
        raise ValueError('Enter a scene description between 1 and 500 characters')
    index = load_index(identity)
    if index['model']!=MODEL or index['modelDigest']!=model_digest():
        raise ValueError('Model changed; reload the video to rebuild its index')
    vector = embed(QUERY_PREFIX + query.strip())
    results = rank_frames(index['frames'],vector)
    return {'results':results,'query':query,'video':public_index(index)}
