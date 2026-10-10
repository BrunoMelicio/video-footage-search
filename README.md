# Framefind

Local text-to-video-frame search, built as project 2 of the embeddings app series. Separate repository from Lookmatch.

Upload a short video or load the included sample. FFmpeg extracts a frame every two seconds; Ollama embeds each image. A text query is embedded in the same model space and compared using cosine similarity. Results show candidate timestamps, and clicking **Jump to moment** seeks the video player.

## Requirements

- Python 3.10+ (standard library only; no pip install).
- FFmpeg and ffprobe available on PATH. On macOS: `brew install ffmpeg`.
- Ollama with multimodal embedding support. Verified environment: Ollama 0.40.2 and `embeddinggemma-2:440m` (438.8M parameters, 714 MB on disk, NVFP4, 768-dimensional output). Reuse the model downloaded for Lookmatch.
- Modern browser. No paid API, generative language model or vector database required.

## Run

Start Ollama (open its app or run `ollama serve` in another terminal), then:

```sh
ollama pull embeddinggemma-2:440m
python3 server.py
```

Open http://localhost:8001. Click **Load sample**, wait for indexing, then click an example query or type your own. Click a result to jump to its timestamp. Use **Upload video** for a video up to 120 seconds and 50 MB. Uploaded files are converted to browser-compatible H.264 MP4; audio is removed from that local preview and is not indexed. Lookmatch can continue running on port 8000.

Frame embeddings and generated previews are stored in ignored `runtime/`. Their cache key includes video content, model digest, sampling interval and pipeline version. Re-loading the same video/model reuses the cache. Only one video indexes at a time; the interface reports progress. Changing the model requires re-indexing. Bind address is localhost only. Set `PORT=8002 python3 server.py` to choose another port.

## Included sample and example tests

The 24-second sample reel is a small, deliberately distinct-scene smoke test, not a surveillance accuracy benchmark.

| Sample interval | Query | Expected top result |
|---|---|---|
| 00:00–00:08 | pink flowers in a garden | Timestamp below 8 seconds |
| 00:08–00:16 | a grassy meadow with a tall evergreen tree | Timestamp from 8 to below 16 seconds |
| 00:16–00:24 | a large white animated rabbit | Timestamp from 16 to below 24 seconds |

Annotations are in `tests/queries.json`. No annotations, captions, filenames or expected ranges enter the embeddings; retrieval uses only extracted image pixels and the user's text. The sample is muted and includes real motion from the source clips. See [ATTRIBUTION.md](ATTRIBUTION.md) for sources, licenses and edits.

```sh
python3 -m unittest discover -s tests -v
python3 evaluate.py
```

Unit checks cover sampling boundaries, invalid vectors, incompatible dimensions, temporal result spacing and invalid video IDs. `evaluate.py` runs actual image and text inference, reports the top timestamp and fails if it falls outside the annotated interval. Saved run evidence is in `tests/retrieval-results.json` when present.

To rebuild the sample from its sources:

```sh
python3 scripts/build_sample.py
```

## Model inputs

Image frame: `{"model":"embeddinggemma-2:440m","input":{"image":"BASE64_JPEG_BYTES"}}`.

Text query: `{"model":"embeddinggemma-2:440m","input":"task: search result | query: YOUR_DESCRIPTION"}`.

The text task prefix follows the [official model card](https://huggingface.co/google/embeddinggemma-2). Frames receive no text prefix. Both inputs produce normalized vectors in the same space. The app uses image frames, not native video/audio embeddings or generated captions. Nearby results are spaced at least four seconds apart to reduce repetition; up to five results are shown.

## Limits and next steps

Scores are not probabilities or proof that a described event occurred. Single sampled frames recognize visible scenes and objects; they do not reliably establish actions. Two-second sampling can miss brief events, and the sample's three broad scenes are easier than similar real-world moments. Search always returns the closest candidates even for an absent scene.

Next: independent live-action clips and out-of-video queries; adjustable sampling and multiple videos; adjacent-frame context, transcripts and clip-level retrieval for actions. Keep evaluation queries and expected timestamp ranges in Git as the dataset grows.
