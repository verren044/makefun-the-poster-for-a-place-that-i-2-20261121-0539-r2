# LUMEN BAY — a travel poster for a place that does not exist.
# A program that draws one travel poster (1024x1024 PNG) with nothing but
# the Python standard library: its own PNG encoder, its own 5x7 bitmap
# font, and a seeded generator, so two runs are byte-identical.
#
# The place: Lumen Bay, a cove where the sea itself glows after dark.
# The promise: one lighthouse on a headland, a glass-calm glowing bay,
# a crescent moon, a lone rowboat — and the name set big across the sky.
#
# No network, no clock, no randomness beyond a fixed-seed generator.

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
SKY_TOP = (16, 22, 46)
SKY_MID = (44, 56, 96)
SKY_LOW = (120, 74, 96)
HORIZON = (232, 160, 76)
SEA_TOP = (29, 74, 94)
SEA_BOT = (8, 28, 44)
GLOW = (57, 230, 195)
GLOW_SOFT = (127, 245, 221)
CREAM = (255, 233, 196)
MOON = (247, 234, 208)
DARK = (13, 21, 38)
TOWER = (242, 232, 216)
BAND = (184, 69, 47)
BEAM = (255, 210, 122)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def blend(self, x, y, c, a):
        """Paint colour c over (x, y) with opacity a (0..255)."""
        if 0 <= x < self.w and 0 <= y < self.h and a > 0:
            i = (y * self.w + x) * 3
            inv = 255 - a
            self.px[i] = (c[0] * a + self.px[i] * inv) // 255
            self.px[i + 1] = (c[1] * a + self.px[i + 1] * inv) // 255
            self.px[i + 2] = (c[2] * a + self.px[i + 2] * inv) // 255

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[base] = c[0]
                self.px[base + 1] = c[1]
                self.px[base + 2] = c[2]
                base += 3

    def disc(self, cx, cy, r, c, alpha=255):
        r2 = r * r
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int(math.sqrt(max(0, r2 - dy * dy)))
            for xx in range(cx - dx, cx + dx + 1):
                if alpha == 255:
                    self.set(xx, yy, c)
                else:
                    self.blend(xx, yy, c, alpha)

    def hline(self, x0, x1, y, c, alpha=255):
        for xx in range(max(0, x0), min(self.w, x1 + 1)):
            if alpha == 255:
                self.set(xx, y, c)
            else:
                self.blend(xx, y, c, alpha)

    def vgrad(self, y0, y1, top, bot):
        """Fill rows y0..y1 with a vertical gradient from top to bot."""
        span = max(1, y1 - y0)
        for yy in range(max(0, y0), min(self.h, y1 + 1)):
            t = (yy - y0) / span
            c = (int(top[0] + (bot[0] - top[0]) * t),
                 int(top[1] + (bot[1] - top[1]) * t),
                 int(top[2] + (bot[2] - top[2]) * t))
            base = yy * self.w * 3
            for xx in range(self.w):
                self.px[base] = c[0]
                self.px[base + 1] = c[1]
                self.px[base + 2] = c[2]
                base += 3

    def poly(self, pts, c, alpha=255):
        """Scanline-fill a polygon (list of (x, y))."""
        if not pts:
            return
        ys = [p[1] for p in pts]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(math.ceil(xs[k])), int(xs[k + 1]) + 1):
                    if alpha == 255:
                        self.set(xx, yy, c)
                    else:
                        self.blend(xx, yy, c, alpha)

    def thick_line(self, x0, y0, x1, y1, r, c, alpha=255):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            t = s / steps
            self.disc(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t), r, c, alpha)


def lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ---------------------------------------------------------------- font
# A hand-drawn 5x7 bitmap font: '#' is ink, '.' is empty.
GLYPHS = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'Y': ("#...#", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#.."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(s, scale):
    return (len(s) * 6 - 1) * scale


def draw_text(cv, x, y, s, scale, c, shadow=None):
    """Draw s at (x, y), top-left, in colour c; shadow is an optional
    offset colour drawn first for contrast against the sky."""
    if shadow is not None:
        draw_text(cv, x + scale, y + scale, s, scale, shadow)
    cx = x
    for ch in s:
        g = GLYPHS.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == '#':
                    cv.rect(cx + rx * scale, y + ry * scale, scale, scale, c)
        cx += 6 * scale


# ---------------------------------------------------------------- scene
def draw_scene(cv):
    # Sky: deep indigo at the top, warming to amber at the horizon.
    cv.vgrad(0, 400, SKY_TOP, SKY_MID)
    cv.vgrad(400, 540, SKY_MID, SKY_LOW)
    # A soft amber glow just above the horizon, then one thin bright line.
    for yy in range(512, 538):
        cv.hline(0, W, yy, HORIZON, int(70 * (yy - 512) / 26))
    cv.rect(0, 538, W, 4, (244, 196, 120))
    # Sea: teal at the horizon, near-black at the bottom.
    cv.vgrad(542, H, SEA_TOP, SEA_BOT)

    # Stars: a fixed-seed generator, so the sky never changes.
    seed = 20261121
    for _ in range(150):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sx = seed % W
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sy = seed % 420
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        bright = 140 + seed % 115
        # Keep the moon's disc clear of stars.
        if (sx - 905) ** 2 + (sy - 115) ** 2 < 85 * 85:
            continue
        cv.set(sx, sy, (bright, bright, min(255, bright + 20)))
        if seed % 5 == 0:
            cv.set(sx + 1, sy, (bright, bright, min(255, bright + 20)))

    # Moon: pale disc with a soft halo, tucked in the upper-right corner
    # so it never touches the title.
    cv.disc(905, 115, 72, (240, 220, 180), 14)
    cv.disc(905, 115, 58, (247, 234, 208), 40)
    cv.disc(905, 115, 50, MOON)
    cv.disc(888, 103, 8, (228, 214, 186))
    cv.disc(922, 130, 5, (228, 214, 186))
    cv.disc(912, 96, 4, (235, 222, 196))

    # Headland: a dark rocky cliff mass on the left, rising from the sea.
    cv.poly([(0, H), (0, 660), (110, 612), (250, 566), (330, 620),
             (300, 780), (210, H)], DARK)
    # A few pale rock highlights on the cliff face.
    cv.thick_line(60, 700, 150, 660, 3, (30, 44, 70))
    cv.thick_line(180, 760, 250, 700, 3, (30, 44, 70))
    cv.disc(40, 980, 26, DARK)
    cv.disc(120, 1000, 34, DARK)

    # Lighthouse on the headland: cream tower, two red bands, warm lamp.
    cv.poly([(192, 592), (228, 592), (222, 470), (198, 470)], TOWER)
    cv.poly([(196, 540), (224, 540), (223, 522), (197, 522)], BAND)
    cv.poly([(197, 500), (223, 500), (222, 484), (198, 484)], BAND)
    cv.rect(190, 460, 40, 12, DARK)
    cv.rect(198, 440, 24, 20, (255, 214, 130))
    cv.disc(210, 450, 30, (255, 210, 122), 30)
    cv.disc(210, 450, 16, (255, 210, 122), 60)
    cv.poly([(194, 440), (226, 440), (210, 424)], DARK)

    # The beam: one narrow warm sweep from the lamp down onto the water.
    cv.poly([(210, 448), (860, 618), (860, 656)], BEAM, 22)

    # The glow: three gentle luminous currents winding through the bay,
    # low and slow so they read as light on water, not waves.
    swirls = [
        (560, 660, 16, 70, 320),
        (600, 780, 20, 90, 380),
        (540, 900, 14, 80, 420),
    ]
    for (x0, y0, amp, per, length) in swirls:
        for s in range(length):
            x = x0 + s
            y = int(y0 + amp * math.sin(s / per))
            r = 3 + (s % 7) // 4
            cv.disc(x, y, r, GLOW, 130)
            cv.disc(x, y, max(1, r - 2), GLOW_SOFT, 175)
    # Sparkles where the glow breaks the surface.
    seed = 77
    for _ in range(90):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sx = 520 + seed % 460
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sy = 580 + seed % 400
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        if seed % 3 == 0:
            cv.disc(sx, sy, 2, GLOW_SOFT, 180)
        else:
            cv.set(sx, sy, GLOW)

    # Gentle wave lines across the sea.
    for (wy, amp, per, a) in [(600, 8, 90, 26), (700, 10, 110, 22),
                              (820, 12, 130, 18), (940, 14, 150, 14)]:
        for x in range(360, 1024, 4):
            y = int(wy + amp * math.sin(x / per))
            cv.hline(x, x + 2, y, (120, 180, 200), a)

    # Rowboat with a lantern, drifting on the glow.
    cv.poly([(672, 760), (744, 760), (728, 780), (688, 780)], DARK)
    cv.thick_line(708, 760, 708, 710, 3, DARK)
    cv.poly([(708, 714), (708, 756), (740, 756)], (232, 226, 208))
    cv.disc(708, 728, 5, (255, 214, 130))
    cv.disc(708, 728, 10, (255, 210, 122), 50)

    # The name, big across the sky; the promise, small beneath it.
    title = "LUMEN BAY"
    tw = text_width(title, 11)
    draw_text(cv, (W - tw) // 2, 64, title, 11, CREAM, shadow=(10, 16, 34))
    tag = "WHERE THE SEA GLOWS AT NIGHT"
    tw2 = text_width(tag, 3)
    draw_text(cv, (W - tw2) // 2, 168, tag, 3, (255, 214, 150),
              shadow=(10, 16, 34))


# ---------------------------------------------------------------- PNG out
def png_bytes(cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def main():
    cv = Canvas(W, H)
    draw_scene(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if out_dir.endswith(".png"):
        path = out_dir
    else:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes(cv))
    print("wrote", path)


if __name__ == "__main__":
    main()
