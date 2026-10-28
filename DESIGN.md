# Auto-Surveillance visual specification

Current product name: **Auto-Surveillance**. Tagline: **Next gen surveillance**. Historical Framefind references below describe the original demo.

## Review workspace revision — 2026-10-28

The current interface supersedes the initial concept below. It uses a compact navy header, a gray workspace background, a recording library, a central player with candidate timeline markers, and a right-side visual search/results panel. Teal marks actions and candidates. Typography is Helvetica Neue with monospace timestamps. At narrower widths, search moves below the player; on mobile the library uses a two-column grid. No synthetic camera metadata, detection boxes or fabricated conversations are displayed. See REVIEW-DIRECTION.md for scope and research findings.

Browser checks covered selecting/indexing all three examples, lobby/parking/retail queries, candidate playback, desktop at 1440px, mobile at 390px, and no horizontal overflow on mobile. Screenshots were captured to /private/tmp/framefind-review-desktop.png and /private/tmp/framefind-review-mobile.png. The following specification is retained as historical context for the original demo.

Concept generated before implementation on 2026-10-10; source screenshot `exec-5fd71e68-d51a-4a7c-920b-1364ce9b8ea4.png` in the conversation's generated images.

Tokens: true white background; navy #101b30; slate #65728c; blue #215ff3; gray dividers #d5dce7. Arial/Helvetica; 62px main heading, 28px subtitle, 24px section headings, 16px controls, 13–14px captions. Six-pixel control corners; no panel shadows or decorative badges.

Structure: minimal wordmark header; centered heading and subtitle; 58/42 player/search split; open result rows with thumbnails and timestamp controls. Native video player, no image overlay. Mobile stacks the player above search.

Allowed copy: Framefind; Local video search; Find a moment.; Describe a scene. Jump to the frame.; Sample reel; Load sample; Upload video; Search the video; Search; Try an example; Pink flowers; Animated rabbit; Forest landscape; Matching moments; Jump to moment; Results are candidate frames. Brief events may fall between samples.

Functional deviations: actual licensed footage replaces the illustrative concept scenes; actual scores/timestamps replace illustrative values; sample attribution and upload/index progress are shown. Real results can contain repeated scene types because they reflect inference, rather than the concept's invented ordering. Up to five actual rows replace the concept's three illustrative rows. Result jump controls sit below scores to keep filenames and controls readable. The white background, typography, blue controls, dividers, primary composition and media framing follow the concept.

## Verification ledger

Playwright Chromium was used because the in-app browser was unavailable earlier in the session. Concept and desktop/mobile screenshots were inspected with view_image at a 1505×1045 desktop viewport and 390×844 mobile viewport.

| Comparison | Result |
|---|---|
| Header and visible primary copy | Wordmark, heading, subtitle, section labels and actions match the concept; functional additions are listed above |
| Layout | Centered introductory heading, wide left player and right search/results column preserved; mobile stacks cleanly |
| Typography | Arial, bold large heading and deliberate control/caption sizing preserved |
| Palette | True white background, navy text, slate captions, blue actions and thin gray dividers preserved |
| Media framing | Native 16:9 player, no color overlay; actual licensed footage replaces concept imagery |
| Result controls | Thumbnail/time/score/jump structure retained, with the documented placement change |

No accidental above-the-fold copy changes or unresolved visual mismatches remain after the documented functional adaptations. The implementation was faithfully verified against the generated design. Functional checks covered sample indexing, text retrieval, uploaded sample, video metadata, seeking to 18 seconds, playback, byte-range delivery, and mobile overflow.
