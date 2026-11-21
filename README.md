# LUMEN BAY — The Poster for a Place That Isn't There

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/verren044/makefun-the-poster-for-a-place-that-i-2-20261121-0539-r2/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/verren044/makefun-the-poster-for-a-place-that-i-2-20261121-0539-r2/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that does not exist: **Lumen Bay**, a cove
where the sea itself glows after dark. One lighthouse on a headland, a
glass-calm bay lit from below, a full moon, a lone rowboat with a
lantern — and the name set big across the sky.

## The entry

`main.py` (Python 3.13, standard library only) draws the poster with its
own PNG encoder and its own hand-drawn 5×7 bitmap font, and writes it to
`/output/entry.png` (1024×1024, deterministic — two runs are
byte-identical). No network, no clock, no randomness beyond a fixed seed.

Run it:

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## The poster

- **Name:** LUMEN BAY, set in cream capitals across the night sky, with
  the promise beneath it: WHERE THE SEA GLOWS AT NIGHT.
- **Landmark:** a cream lighthouse with two red bands on a dark headland,
  its beam sweeping down onto the water.
- **Light:** a full moon upper right, stars, an amber glow at the
  horizon, and three luminous currents winding through the bay.
- **Palette:** deep indigo sky → amber horizon → teal sea, with the
  aqua glow as the one colour that belongs to this place alone.
