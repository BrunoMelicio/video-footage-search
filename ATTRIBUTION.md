# Sample media attribution

The repository includes `samples/sample-reel.mp4`, a 24-second edited teaching fixture. It contains these segments, concatenated and transcoded to 640×360 H.264 at 24 fps. Audio was removed. No endorsement is implied.

1. **00:00–00:08: flowers** — MDN interactive example, from https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4. Source is distributed in MDN's `cc0-videos` collection. [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The approximately five-second clip is repeated and trimmed to eight seconds.
2. **00:08–00:16: animated landscape** — excerpt at source 00:10–00:18 from *Big Buck Bunny*.
3. **00:16–00:24: animated rabbit** — excerpt at source 01:00–01:08 from *Big Buck Bunny*.

*Big Buck Bunny*: © copyright 2008, Blender Foundation / https://www.bigbuckbunny.org/. [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/). Source download: https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip. License information: https://peach.blender.org/about/ and https://commons.wikimedia.org/wiki/File:Big_Buck_Bunny_Trailer_400p.ogv.

Frame thumbnails derived from these segments retain the same source attribution. Uploaded user videos are not included in Git.

## Camera examples and documentation screenshots

`scripts/prepare_review_samples.py` downloads these camera examples into ignored `runtime/demo/`; source videos are not added to Git.

| Local example | Original recording | Source and terms | Modifications |
|---|---|---|---|
| `lobby.mp4` | `LeftBag/LeftBag.mpg` | [CAVIAR](https://homepages.inf.ed.ac.uk/rbf/CAVIARDATA1/), EC Funded CAVIAR project / IST 2001 37540. Source page states Creative Commons BY-SA without a version in its text. | Opening 30 seconds; H.264 conversion; no audio. |
| `retail.mp4` | `EnterExitCrossingPaths1cor/EnterExitCrossingPaths1cor.mpg` | [CAVIAR](https://homepages.inf.ed.ac.uk/rbf/CAVIARDATA1/), EC Funded CAVIAR project / IST 2001 37540. Same source-stated CC BY-SA terms. | Approximately 15.32 seconds; H.264 conversion; no audio. |
| `parking.mp4` | `2018-03-13.17-10-03.17-15-03.school.G424.r13.avi` | [MEVA](https://mevadata.org/), Kitware / IARPA, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). | Opening approximately 30 seconds decoded from the first 16 MiB; resized to 960 pixels wide; H.264 conversion; no audio. |

`docs/assets/review-workspace.png` and `docs/assets/review-mobile.png` are actual Auto-Surveillance interface captures containing frames and thumbnails from CAVIAR's Lisbon retail sequence. The underlying footage is credited above; its derivatives retain CAVIAR's source-stated CC BY-SA terms. Interface capture, scaling and layout are the only presentation changes; no people or events were generated or rearranged. No endorsement is implied.

The preparation script records source URLs, requested byte ranges and input/output hashes in ignored `runtime/demo/sources.json`. These recordings are research examples, not customer surveillance footage.
