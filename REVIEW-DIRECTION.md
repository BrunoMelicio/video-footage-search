# Auto-Surveillance: recorded-footage review

The first product is a local workspace for a human reviewer to find candidate moments in recorded footage. Building entrances, parking areas and retail share the same core flow: select recordings, define the time window, search, watch surrounding footage, and save reviewed evidence.

## Working exploration, 2026-10-28

The running UI has a recording library, a player, candidate markers on a recording timeline, five-second playback controls, source credits, and visual search with per-recording example queries. It searches one recording at a time. Imports remain limited to two minutes / 50 MB. There is no conversational model, event detector, cross-camera tracking, production authentication, or reliable absent-event rejection yet.

Three real camera samples are prepared locally in ignored runtime/demo/. They are public research recordings, not footage from a production customer. The parking example covers a car park, not warehouse work. The retail example covers a shop entrance, not a checkout or shop floor.

| Setting | Source / excerpt | Query | Observed top frame |
| --- | --- | --- | --- |
| Building | CAVIAR LeftBag, first 30 seconds | a person wearing a blue jacket | 00:00; blue-jacketed person visible |
| Parking | MEVA school.G424, opening ~30 seconds | a person wearing red near a white pickup truck | 00:12; person in red beside foreground vehicles |
| Retail | CAVIAR EnterExitCrossingPaths1cor, full 15.32 seconds | a person in a light beige sweater | 00:12; person in beige visible |

These are exploratory observations after inspecting sampled footage, not a held-out accuracy benchmark. Full raw rankings are saved to runtime/review-evaluation.json by scripts/evaluate_review.py. Retrieval does not receive the sample's name, source, descriptions or query expectations as model input.

An absent-dog query returns candidates in every recording: lobby cosine 0.718, parking 0.679, retail 0.688. In the lobby, this exceeds the correct blue-jacket query's 0.687. Cross-query cosine is not calibrated confidence. A fixed arbitrary threshold would not solve this test. The bag query ranks 00:06 and needs temporal verification; it does not prove a bag was left behind. No claim is made that all positive query results are correct.

## Next increments

1. **Reliable retrieval evaluation:** label intervals independently, include empty scenes and absent objects, measure recall within a review budget and false positives. Test multiple cameras, low light, occlusion and small subjects. Compare the present model to alternatives using the same held-out cases.
2. **Clip context and verification:** retrieve a window, check adjacent frames and object crops, and return supported observations with timestamps. Distinguish candidate, reviewer-confirmed and rejected states. Learn abstention from representative validation data; do not turn raw cosine into a confidence percentage.
3. **Practical recorded-footage ingestion:** background jobs, segmentation of long recordings, persistent recording/camera metadata, correct source time and timezone, time-range filtering and multiple recordings. Preserve original evidence separately from generated previews and record hashes.
4. **Grounded follow-ups:** maintain the selected cameras/time window and prior candidate IDs. “Only after 6 pm”, “show ten seconds earlier”, and “find another red vehicle” become explicit filters or searches. Every factual answer links to source footage; unsupported questions get an explicit inability to determine.
5. **Review output and deployment:** bookmarks, notes, context clip export, source offsets, access control, retention and audit records. Evaluate with real reviewers before operational use.

Suggested scenario questions: building—people near an entrance and visible bags; parking—vehicles and clothing near parked cars; retail—people near a shop entrance or counter. “Left a bag”, “loitering”, “entered but never exited” and “stole an item” require temporal evidence and cannot be inferred from a single ranked frame.

## Sources and preparation

- CAVIAR: https://homepages.inf.ed.ac.uk/rbf/CAVIARDATA1/ . Acknowledge EC Funded CAVIAR project / IST 2001 37540. The source page states Creative Commons BY-SA without identifying a version in its text. Retain the attribution and share-alike terms when redistributing derivatives.
- MEVA: https://mevadata.org/ . Kitware / IARPA, CC BY 4.0. File: 2018-03-13.17-10-03.17-15-03.school.G424.r13.avi. The local acquisition used the first 16 MiB, from which the opening segment decoded successfully. Source offsets begin at zero; timestamps shown in the UI are clip-relative, not wall-clock times.
- OpenCV's vtest.avi was inspected as an additional outdoor walkway example, but is not bundled or listed in the review library.

Prepare local assets with `python3 scripts/prepare_review_samples.py` (network download and FFmpeg required). Then run `python3 scripts/evaluate_review.py`. Media and caches are ignored by Git. The original synthetic-scene test remains available and `python3 evaluate.py` still checks it.
