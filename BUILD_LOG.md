# BUILD_LOG — the-poster-for-a-place-that-i-2-20261121-0539

## Build (fresh session, 21 Nov 2026, after the competition opened)
- `main.py` written from the brief in the kit's RULES.txt and
  competition.yaml only — no earlier entry files were read or copied.
- Pure Python 3.13 stdlib: own PNG encoder (zlib + struct, filter 0,
  RGB, CRC-checked chunks), own 5x7 bitmap font drawn by hand, own
  canvas (gradients, polygons, discs, alpha blending).
- Scene, 1024x1024: indigo-to-amber sky, stars (fixed-seed generator),
  full moon upper right, dark headland left with a cream lighthouse
  (two red bands, warm lamp, narrow beam onto the water), three gentle
  glowing currents in the bay, sparkles, wave lines, a rowboat with a
  lantern, and the name LUMEN BAY big across the sky with the tagline
  WHERE THE SEA GLOWS AT NIGHT beneath it.

## Revision (same session, second message)
- First render reviewed at full size: the title's final letter touched
  the moon, the glow swirls were wild zigzags that crossed the horizon,
  the horizon band was a hard stripe, and the beam was a wide grey
  wedge. Fixed: moon moved to the upper-right corner clear of the
  title; swirls shrunk to low, slow currents inside the sea; horizon
  reduced to a soft amber glow plus one thin bright line; beam narrowed
  to a single warm sweep ending on the water; boat moved to calmer
  water between the currents.

## Verification
- Determinism: `MAKEFUN_OUTPUT_DIR=/tmp/po1` and `/tmp/po2` runs
  compared with `cmp` — byte-identical.
- PNG: magic + all chunk CRCs valid, 1024x1024, bit depth 8, colour
  type 2 (RGB), 20,524 bytes < 1,048,576.
- entry.png sha256:
  `567a8592b613187cace0e9919b06edd0c502fe717cdf51c697cef819d5f580af`
- Visual check at full size: title and tagline legible, no overlap
  with the moon, no garbled or overlapping text, nothing spills
  outside the frame, the eye goes name → lighthouse/beam → glowing
  bay → boat.
- `README.md` carries the three live make.fun badges (competition,
  rank, reward) as image links to the bounty page.
- `.makefun/owner.json` and `LICENSE` left untouched.
