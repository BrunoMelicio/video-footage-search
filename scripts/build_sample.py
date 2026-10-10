"""Reproduce the included teaching fixture from public source videos."""
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def run(args):
    subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)

with tempfile.TemporaryDirectory() as temporary:
    directory=Path(temporary)
    urllib.request.urlretrieve('https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',directory/'flowers.mp4')
    urllib.request.urlretrieve('https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip',directory/'bunny.zip')
    with zipfile.ZipFile(directory/'bunny.zip') as archive:
        # Read only the known movie entry; never extract arbitrary paths.
        (directory/'bunny.mp4').write_bytes(archive.read('BigBuckBunny_320x180.mp4'))
    segments=[('flowers.mp4',0,True),('bunny.mp4',10,False),('bunny.mp4',60,False)]
    for i,(name,start,loop) in enumerate(segments):
        run([*(['-stream_loop','-1'] if loop else []),'-ss',str(start),'-i',str(directory/name),'-t','8','-vf','scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,fps=24,setsar=1','-an','-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p',str(directory/f'part-{i}.mp4')])
    (directory/'concat.txt').write_text('\n'.join(f"file 'part-{i}.mp4'" for i in range(3)))
    (ROOT/'samples').mkdir(exist_ok=True)
    run(['-f','concat','-safe','0','-i',str(directory/'concat.txt'),'-c','copy','-movflags','+faststart',str(ROOT/'samples/sample-reel.mp4')])
print('Built samples/sample-reel.mp4. See ATTRIBUTION.md.')
