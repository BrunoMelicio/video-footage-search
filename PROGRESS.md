# Project 2 checkpoint — 2026-10-10

Framefind is a separate app/repository from Lookmatch. First milestone: sample or uploaded short video → image-frame embeddings → text search → clickable candidate timestamps.

## Working setup

- Python standard library + FFmpeg/ffprobe + local Ollama; no pip dependencies.
- Model reused from project 1: embeddinggemma-2:440m, 438.8M parameters, 714 MB disk, NVFP4, 768-dimensional embeddings; Ollama 0.40.2.
- Image frames sampled every two seconds; text queries use `task: search result | query: `; normalized cosine similarity; results spaced four seconds apart.
- Upload limit 50 MB / 120 seconds. Browser preview is transcoded to H.264 MP4 with audio removed. Original upload temporary files are deleted after indexing. Generated runtime files are ignored by Git.
- Run `python3 server.py`; open http://localhost:8001. Click Load sample, then an example or your own query. Jump to moment seeks the player.

## Sample and evidence

The included 24-second sample contains MDN flowers (CC0) and two edited Big Buck Bunny excerpts (CC BY 3.0). See ATTRIBUTION.md and the reproducible build script.

- Flower query → 4 seconds, within 0–8, cosine 0.688.
- Meadow/tree query → 8 seconds, within 8–16, cosine 0.719.
- Animated rabbit query → 18 seconds, within 16–24, cosine 0.783.
- All three actual text-to-frame top-result checks passed; scores saved in tests/retrieval-results.json.
- Six unit checks passed. Browser sample loading, searching, timestamp jump, sample upload and mobile layout passed. HTTP byte ranges return 206 for seeking; invalid media upload reports an error.

Run `python3 -m unittest discover -s tests -v` and `python3 evaluate.py` to reproduce the checks.

## Limits and next steps

Single frames retrieve visible objects/scenes, not reliable action understanding. Brief events can fall between samples. Scores are ranking signals, not probabilities; absent queries still return nearest candidates. This distinct-scene fixture is easier than live-action surveillance.

Next: use a short real-world clip with manually annotated query ranges; add out-of-video queries; adjustable sampling; multiple videos; adjacent-frame or clip context; transcripts/audio later.
