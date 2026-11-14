#!/usr/bin/env python3
"""Generates all textures and models of the christmas_view mod.

Usage:
  python3 gen_textures.py [NEW OLD OLD_SHAVED]

Each sheep argument is "<model.b3d>:<tex1.png>,<tex2.png>,..." - the model and
the original textures whose combined alpha decides which texels stay visible.
NEW        - mobs_sheep.b3d + mobs_sheep_base.png,mobs_sheep_wool.png from tiny_shelter / shelter_ta
OLD        - mobs_sheep.b3d + mobs_sheep_base.png,mobs_sheep_wool.png from survival_shelter
OLD_SHAVED - mobs_sheep_shaved.b3d + mobs_sheep_shaved.png from survival_shelter
For the NEW model the shaved variant is made with mobs_sheep_shaved.png from
the same folder as the first texture.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3d  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(MOD, "textures")
MODELS = os.path.join(MOD, "models")
P = "christmas_view_"

rnd = random.Random(2512)

# ---------------------------------------------------------------- palette
T = (0, 0, 0, 0)
WHITE = (250, 250, 252, 255)
FUR = (240, 240, 236, 255)
FUR_S = (206, 208, 210, 255)
RED = (200, 24, 36, 255)
RED_D = (140, 12, 24, 255)
RED_L = (232, 64, 64, 255)
GREEN = (34, 120, 52, 255)
GREEN_D = (20, 78, 36, 255)
GREEN_L = (64, 156, 72, 255)
GOLD = (240, 196, 60, 255)
GOLD_D = (184, 136, 30, 255)
GOLD_L = (255, 236, 150, 255)
OUTL = (40, 28, 30, 255)
BROWN = (176, 106, 52, 255)
BROWN_D = (128, 72, 34, 255)
BROWN_L = (210, 146, 84, 255)
SNOW = (246, 250, 255, 255)
SNOW_S = (206, 222, 240, 255)
SNOW_D = (168, 190, 220, 255)
COAL = (34, 34, 40, 255)
CARROT = (240, 128, 30, 255)


def save(img, name):
    img.save(os.path.join(TEX, P + name))


def from_rows(rows, pal):
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w, h), T)
    px = img.load()
    for y, r in enumerate(rows):
        assert len(r) == w, (y, r, len(r))
        for x, c in enumerate(r):
            if c in pal:
                px[x, y] = pal[c]
    return img


def jitter(c, amount=8, rng=None):
    d = (rng or rnd).randint(-amount, amount)
    return tuple(max(0, min(255, v + d)) for v in c[:3]) + (c[3],)


def outline(img, color=OUTL):
    a = np.array(img)
    op = a[:, :, 3] > 0
    ring = np.zeros_like(op)
    ring[1:, :] |= op[:-1, :]
    ring[:-1, :] |= op[1:, :]
    ring[:, 1:] |= op[:, :-1]
    ring[:, :-1] |= op[:, 1:]
    ring &= ~op
    a[ring] = color
    return Image.fromarray(a)


def pad(img, n=1):
    out = Image.new("RGBA", (img.size[0] + 2 * n, img.size[1] + 2 * n), T)
    out.alpha_composite(img, (n, n))
    return out


def gray(v, a=255):
    return (v, v, v, a)


def blank(w, h):
    return Image.new("RGBA", (w, h), T)


def disc(img, cx, cy, r, color, shade=None):
    """Filled circle; shade = (light, dark) for a simple spherical shading."""
    px = img.load()
    w, h = img.size
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if 0 <= x < w and 0 <= y < h:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d <= r:
                    c = color
                    if shade:
                        lx, ly = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
                        if math.hypot(lx + 0.4, ly + 0.4) < 0.35:
                            c = shade[0]
                        elif lx + ly > 0.75:
                            c = shade[1]
                    px[x, y] = c


# ================================================================ gifts (chests)
# All gift parts are grey scale and get their colour at runtime with
# ^[multiply, so one set of files is enough for every colour.
G = 32  # gift texture size


def gift_paper():
    img = Image.new("RGBA", (G, G))
    px = img.load()
    for y in range(G):
        for x in range(G):
            v = 236
            if (x + y) % 11 == 0:
                v = 248
            if x in (0, G - 1) or y in (0, G - 1):
                v = 176
            elif x in (1, G - 2) or y in (1, G - 2):
                v = 214
            px[x, y] = gray(max(0, min(255, v + rnd.randint(-5, 5))))
    return img


def gift_pattern(w=G, h=G):
    """Little white snowflakes and dots printed on the paper."""
    img = blank(w, h)
    px = img.load()
    flake = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    for gy in range(0, h, 8):
        for gx in range(0, w, 8):
            ox = gx + (4 if (gy // 8) % 2 else 0) + 3
            oy = gy + 3
            if (gx // 8 + gy // 8) % 2 == 0:
                for dx, dy in flake:
                    x, y = (ox + dx) % w, (oy + dy) % h
                    if 2 <= x < w - 2 and 2 <= y < h - 2:
                        px[x, y] = (255, 255, 255, 170)
            else:
                x, y = ox % w, oy % h
                if 2 <= x < w - 2 and 2 <= y < h - 2:
                    px[x, y] = (255, 255, 255, 130)
    return img


def ribbon_band(img, x0, x1, vertical=True):
    """Shaded ribbon band (grey scale) from x0 to x1 (inclusive)."""
    px = img.load()
    w, h = img.size
    n = x1 - x0 + 1
    for k in range(n):
        v = 236
        if k == 0 or k == n - 1:
            v = 178
        elif k == n // 2:
            v = 255
        for t in range(h if vertical else w):
            x, y = (x0 + k, t) if vertical else (t, x0 + k)
            if 0 <= x < w and 0 <= y < h:
                px[x, y] = gray(v)


def draw_bow(img, cx, cy, s=1.0):
    """A bow seen from above: two loops, a knot and two tails (grey scale)."""
    d = ImageDraw.Draw(img)
    for sign in (-1, 1):
        # loop
        pts = [(cx, cy), (cx + sign * 9 * s, cy - 7 * s), (cx + sign * 12 * s, cy - 2 * s),
               (cx + sign * 9 * s, cy + 3 * s)]
        d.polygon(pts, fill=gray(232), outline=gray(170))
        d.line([(cx + sign * 2 * s, cy - 1 * s), (cx + sign * 8 * s, cy - 4 * s)],
               fill=gray(200), width=1)
        # tail
        tail = [(cx, cy), (cx + sign * 5 * s, cy + 9 * s), (cx + sign * 8 * s, cy + 8 * s),
                (cx + sign * 2 * s, cy)]
        d.polygon(tail, fill=gray(214), outline=gray(160))
    d.rectangle([cx - 2 * s, cy - 2 * s, cx + 2 * s - 1, cy + 2 * s - 1], fill=gray(255),
                outline=gray(186))


def gen_gifts():
    save(gift_paper(), "gift_paper.png")
    save(gift_pattern(), "gift_pattern.png")

    side = blank(G, G)
    ribbon_band(side, 13, 18)
    save(side, "gift_ribbon_side.png")

    bottom = blank(G, G)
    ribbon_band(bottom, 13, 18)
    ribbon_band(bottom, 13, 18, vertical=False)
    save(bottom, "gift_ribbon_bottom.png")

    top = bottom.copy()
    draw_bow(top, 16, 15)
    save(top, "gift_ribbon_top.png")

    # big (double) chest from connected_chests: a 64x32 design cut in halves,
    # the ribbon and the bow sit on the seam between the two nodes
    big_top = blank(2 * G, G)
    ribbon_band(big_top, 29, 34)
    ribbon_band(big_top, 13, 18, vertical=False)
    draw_bow(big_top, 32, 15, 1.35)
    big_side = blank(2 * G, G)
    ribbon_band(big_side, 29, 34)
    big_bottom = big_side.copy()
    ribbon_band(big_bottom, 13, 18, vertical=False)
    for name, img in (("top", big_top), ("side", big_side), ("bottom", big_bottom)):
        save(img.crop((0, 0, G, G)), "gift_big_%s_l.png" % name)
        save(img.crop((G, 0, 2 * G, G)), "gift_big_%s_r.png" % name)
    # a paper without the inner border on the seam side
    pp = gift_paper()
    left = pp.copy()
    left.paste(pp.crop((4, 0, 6, G)).resize((2, G)), (G - 2, 0))
    save(left, "gift_paper_l.png")
    save(left.transpose(Image.FLIP_LEFT_RIGHT), "gift_paper_r.png")

    # padlock (gold) for locked chests and a gift tag for protected ones
    lock = from_rows([
        "..oooo..",
        ".oGGGGo.",
        ".oG..Go.",
        "oooooooo",
        "oYYYYYYo",
        "oYYooYYo",
        "oYYooYYo",
        "oYYYYYYo",
        "oDDDDDDo",
        "oooooooo",
    ], {"o": OUTL, "G": (190, 190, 200, 255), "Y": GOLD, "D": GOLD_D})
    img = blank(G, G)
    img.alpha_composite(lock.resize((10, 13), Image.NEAREST), (11, 15))
    save(img, "gift_lock.png")
    big = blank(2 * G, G)
    big.alpha_composite(lock.resize((10, 13), Image.NEAREST), (27, 15))
    save(big.crop((0, 0, G, G)), "gift_big_lock_l.png")
    save(big.crop((G, 0, 2 * G, G)), "gift_big_lock_r.png")

    tag = from_rows([
        "....oo.....",
        "...o..o....",
        "....oo.....",
        "....o......",
        "..ooooooo..",
        ".oWWWWWWWo.",
        "oWWWRRWWWWo",
        "oWWRRRRWWWo",
        "oWWWRRWWWWo",
        "oWWWWWWWWWo",
        ".ooooooooo.",
    ], {"o": OUTL, "W": (250, 244, 224, 255), "R": RED})
    img = blank(G, G)
    img.alpha_composite(tag, (19, 17))
    save(img, "gift_tag.png")

    # inside: cardboard with red tissue paper
    def inside(w, h):
        img = Image.new("RGBA", (w, h))
        px = img.load()
        for y in range(h):
            for x in range(w):
                if x < 2 or y < 2 or x >= w - 2 or y >= h - 2:
                    c = (186, 140, 92, 255)
                else:
                    c = (196, 34, 44, 255) if ((x + 2 * y) // 5) % 3 else (226, 70, 76, 255)
                px[x, y] = jitter(c, 6)
        return img
    save(inside(G, G), "gift_inside.png")
    save(inside(G, 2 * G), "gift_inside_big.png")


# ================================================================ ice apple
def gen_apple():
    rows = [
        "................",
        "........b.......",
        ".......b...ll...",
        ".......b.lLl....",
        "....oooboo......",
        "...oIiiIiiIo....",
        "..oIiWWiiiiIo...",
        "..oiWWiiiiiIo...",
        "..oiWiiiiiiIo...",
        "..oiiiiiiiiDo...",
        "..oIiiiiiiIDo...",
        "..oIiiiiiIDDo...",
        "...oIiiiIDDo....",
        "....oIDDDDo.....",
        ".....oo.oo......",
        "................",
    ]
    pal = {"o": (96, 150, 200, 255), "I": (150, 206, 244, 255), "i": (196, 232, 255, 255),
           "W": (255, 255, 255, 255), "D": (120, 176, 226, 255), "b": (110, 150, 176, 255),
           "l": (170, 220, 236, 255), "L": (226, 246, 255, 255)}
    small = from_rows(rows, pal)
    # 32x32: upscale and add frosty sparkles and crack lines
    img = small.resize((32, 32), Image.NEAREST)
    px = img.load()
    for (x, y) in [(10, 13), (11, 14), (12, 15), (12, 16), (13, 17), (18, 20), (19, 21), (20, 21)]:
        if px[x, y][3]:
            px[x, y] = (232, 248, 255, 255)
    for (x, y) in [(8, 12), (22, 16), (15, 24)]:
        if px[x, y][3]:
            px[x, y] = WHITE
    save(img, "apple.png")

    # riesenpilz turns the apple into a 3D nodebox apple (tiny_shelter,
    # survival_shelter): top / bottom / side tiles of the same layout
    arng = random.Random(21)
    ICE = (196, 232, 255, 255)
    ICE_L = (232, 248, 255, 255)
    ICE_D = (140, 196, 236, 255)
    STEM_I = (150, 186, 206, 255)
    LEAF_I = (156, 214, 196, 255)
    side = Image.new("RGBA", (16, 16))
    px = side.load()
    for y in range(16):
        for x in range(16):
            if y >= 7:
                c = ICE
                if x <= 5:
                    c = ICE_L
                elif x >= 10 or y >= 14:
                    c = ICE_D
            else:
                c = LEAF_I if (3 <= y <= 6 and 4 <= x <= 10) else STEM_I
            px[x, y] = jitter(c, 6, arng)
    for (x, y) in [(5, 9), (6, 10), (7, 10), (8, 11), (11, 8), (12, 9)]:
        px[x, y] = WHITE
    save(side, "apple_side.png")
    top = Image.new("RGBA", (32, 32))
    px = top.load()
    for y in range(32):
        for x in range(32):
            d = math.hypot(x - 13.5, y - 13.5)
            c = ICE_L if d < 5 else (ICE if d < 11 else ICE_D)
            px[x, y] = jitter(c, 6, arng)
    for (x, y) in [(15, 15), (14, 16), (15, 16), (14, 17), (15, 17)]:
        px[x, y] = STEM_I
    save(top, "apple_top.png")
    bottom = Image.new("RGBA", (16, 16))
    px = bottom.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = jitter(ICE_D, 6, arng)
    save(bottom, "apple_bottom.png")


# ================================================================ wreath (doors)
def wreath(size, r_out, r_in, bow=True, rng=None):
    rng = rng or random.Random(7)
    img = blank(size, size)
    px = img.load()
    c = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x + 0.5 - c, y + 0.5 - c)
            if r_in <= d <= r_out + rng.uniform(-1.2, 1.0):
                col = rng.choice([GREEN, GREEN, GREEN_D, GREEN_L, (28, 100, 44, 255)])
                px[x, y] = jitter(col, 8, rng)
    # needles sticking out
    for _ in range(int(size * 2.2)):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(r_in - 1, r_out + 1.5)
        x, y = int(c + math.cos(a) * rr), int(c + math.sin(a) * rr)
        if 0 <= x < size and 0 <= y < size:
            px[x, y] = GREEN_D if rng.random() < 0.6 else GREEN_L
    # berries and little baubles
    mid = (r_out + r_in) / 2
    k = 0
    for i in range(14):
        a = i * 2 * math.pi / 14 + rng.uniform(-0.15, 0.15)
        if bow and 1.2 < a < 1.95:
            continue
        x = c + math.cos(a) * (mid + rng.uniform(-1.5, 1.5))
        y = c + math.sin(a) * (mid + rng.uniform(-1.5, 1.5))
        k += 1
        if k % 3 == 0:
            disc(img, x, y, size / 22, GOLD, (GOLD_L, GOLD_D))
        else:
            disc(img, x, y, size / 30 + 0.6, RED, (RED_L, RED_D))
    if bow:
        s = size / 64
        d = ImageDraw.Draw(img)
        bx, by = c, c + mid
        for sign in (-1, 1):
            d.polygon([(bx, by), (bx + sign * 11 * s, by - 7 * s), (bx + sign * 13 * s, by + 1 * s),
                       (bx + sign * 9 * s, by + 5 * s)], fill=RED, outline=RED_D)
            d.polygon([(bx, by), (bx + sign * 6 * s, by + 13 * s), (bx + sign * 10 * s, by + 12 * s),
                       (bx + sign * 3 * s, by)], fill=RED, outline=RED_D)
        d.rectangle([bx - 3 * s, by - 3 * s, bx + 3 * s, by + 3 * s], fill=RED_L, outline=RED_D)
    return img


def gen_wreaths():
    # doors with door_a.b3d / door_b.b3d: 38x32 layout (front face x 0..15,
    # back face x 16..31 mirrored, the rest is the edges), drawn at 4x
    w = wreath(56, 25, 15)
    door = blank(38 * 4, 32 * 4)
    door.alpha_composite(w, (4, 6))
    door.alpha_composite(w.transpose(Image.FLIP_LEFT_RIGHT), (68, 6))
    save(door, "door_wreath.png")
    # protector doors: one 16x16 tile per half; the wreath sits on the top half
    top = blank(64, 64)
    top.alpha_composite(wreath(54, 24, 14, rng=random.Random(9)), (5, 8))
    save(top, "door_wreath_top.png")
    # item badge (32x32 over a 16x16 icon): bottom right corner
    badge = blank(32, 32)
    badge.alpha_composite(wreath(18, 8.5, 4.5, bow=False, rng=random.Random(3)), (14, 14))
    save(badge, "badge_wreath.png")


# ================================================================ candy canes (fences)
def candy(w=32, h=32, period=12, red_w=5):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            k = (x + y) % period
            if k < red_w:
                c = RED if k not in (0, red_w - 1) else RED_D
            else:
                c = WHITE if k != red_w else (226, 226, 230, 255)
            px[x, y] = c
    return img


def cane_sprite(h, flip=False):
    """Candy cane for icons: shaft 3 px wide with a round hook, h px tall."""
    w = 10
    img = blank(w, h)
    px = img.load()
    cx, cy, r = 5.5, 4.5, 3.0  # hook centre and radius (middle of the stroke)
    for y in range(h):
        for x in range(w):
            fx, fy = x + 0.5, y + 0.5
            on = False
            if fy >= cy and 1 <= x <= 3:            # shaft (left side of the hook)
                on = True
            d = math.hypot(fx - cx, fy - cy)
            if fy < cy + 0.01 and abs(d - r) <= 1.5:  # upper half ring
                on = True
            if fy >= cy and fy < cy + 2.5 and 7 <= x <= 9:  # hook end
                on = True
            if on:
                px[x, y] = RED if ((x + y) // 2) % 3 == 0 else WHITE
    img = outline(pad(img))
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img


def gen_candy():
    save(candy(), "candy.png")
    # fence item icon: palisade of three canes with two rails
    icon = blank(32, 32)
    d = ImageDraw.Draw(icon)
    for y0 in (12, 22):
        d.rectangle([2, y0, 29, y0 + 2], fill=WHITE, outline=RED)
    for x in (2, 12, 22):
        icon.alpha_composite(cane_sprite(27), (x - 2, 2))
    save(icon, "fence_inv.png")
    rail = blank(32, 32)
    for y0 in (8, 19):
        c = candy(30, 5, 6, 3)
        rail.alpha_composite(outline(pad(c, 0)), (1, y0))
    save(outline(rail), "fence_rail_inv.png")


# ================================================================ ornaments (torches)
ORN = 32  # ornament ball texture


def ornament_ball_frames():
    """Equirectangular texture of the ball (u around, v from top to bottom),
    4 frames: little sparkles twinkle on the glass."""
    frames = []
    rng = random.Random(41)
    sparkles = [(rng.randrange(ORN), rng.randrange(4, ORN - 4)) for _ in range(14)]
    for f in range(4):
        img = Image.new("RGBA", (ORN, ORN))
        px = img.load()
        for y in range(ORN):
            for x in range(ORN):
                v = y / (ORN - 1)
                c = RED
                if 0.44 < v < 0.56:
                    c = GOLD if (x // 2) % 2 else GOLD_L
                elif 0.40 < v <= 0.44 or 0.56 <= v < 0.60:
                    c = WHITE
                elif 0.2 < v < 0.3 and (x + y) % 8 < 2:
                    c = RED_L
                elif 0.7 < v < 0.8 and (x - y) % 8 < 2:
                    c = RED_L
                if v > 0.85:
                    c = RED_D
                px[x, y] = jitter(c, 4, rng)
        for i, (x, y) in enumerate(sparkles):
            if (i + f) % 4 == 0:
                px[x, y] = WHITE
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = (x + dx) % ORN, y + dy
                    px[xx, yy] = GOLD_L
            elif (i + f) % 4 == 1:
                px[x, y] = GOLD_L
        frames.append(img)
    strip = Image.new("RGBA", (ORN, ORN * 4))
    for i, fr in enumerate(frames):
        strip.paste(fr, (0, i * ORN))
    return strip


def gen_ornament_textures():
    save(ornament_ball_frames(), "ornament_ball.png")
    cap = Image.new("RGBA", (8, 8))
    px = cap.load()
    for y in range(8):
        for x in range(8):
            px[x, y] = GOLD_L if x in (2, 3) else (GOLD if x % 3 else GOLD_D)
    save(cap, "ornament_cap.png")
    save(Image.new("RGBA", (2, 2), GOLD_D), "ornament_string.png")
    # inventory image
    inv = blank(16, 16)
    disc(inv, 8, 9.5, 5.5, RED, (RED_L, RED_D))
    p = inv.load()
    for x in range(3, 14):
        if p[x, 9][3]:
            p[x, 9] = GOLD
    p[6, 6] = WHITE
    p[5, 7] = WHITE
    for x in range(7, 10):
        p[x, 3] = GOLD_D
        p[x, 4] = GOLD
    p[8, 2] = GOLD_D
    p[8, 1] = GOLD_D
    save(outline(inv), "ornament_inv.png")


def sphere(cx, cy, cz, r, seg=12, rings=8):
    """UV sphere as quads: list of (verts, uvs)."""
    quads = []
    for j in range(rings):
        t0, t1 = math.pi * j / rings, math.pi * (j + 1) / rings
        for i in range(seg):
            p0, p1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg

            def v(t, p):
                return (cx + r * math.sin(t) * math.cos(p), cy + r * math.cos(t),
                        cz + r * math.sin(t) * math.sin(p))
            # outward winding: (t0,p0) (t0,p1) (t1,p1) (t1,p0) seen from outside
            verts = [v(t1, p0), v(t0, p0), v(t0, p1), v(t1, p1)]
            uvs = [(i / seg, 1 - (j + 1) / rings), (i / seg, 1 - j / rings),
                   ((i + 1) / seg, 1 - j / rings), ((i + 1) / seg, 1 - (j + 1) / rings)]
            quads.append((verts, uvs))
    return quads


def box(x0, y0, z0, x1, y1, z1):
    f = {
        "-z": [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)],
        "+z": [(x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (x0, y0, z1)],
        "+x": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "-x": [(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)],
        "+y": [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)],
        "-y": [(x0, y0, z1), (x0, y0, z0), (x1, y0, z0), (x1, y0, z1)],
    }
    uv = [(0, 0), (0, 1), (1, 1), (1, 0)]
    return [(q, uv) for q in f.values()]


def fix_winding(quads, center):
    """Makes every quad face away from center (for the closed shapes)."""
    out = []
    for verts, uvs in quads:
        a, b, c = (np.array(v, float) for v in verts[:3])
        n = np.cross(b - a, c - a)
        m = np.mean(np.array(verts, float), axis=0)
        if np.dot(n, m - np.array(center, float)) < 0:
            verts = verts[::-1]
            uvs = uvs[::-1]
        out.append((verts, uvs))
    return out


def write_obj(path, groups):
    """groups: list of (material, quads); coordinates in 1/16 node, Luanti
    space (the OBJ is mirrored on X, Luanti mirrors it back)."""
    v, vt, vn, body = [], [], [], []
    k = 0
    for mat, quads in groups:
        body.append("usemtl " + mat)
        for verts, uvs in quads:
            a, b, c = (np.array(p, float) for p in verts[:3])
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            n = n / ln if ln else n
            for (x, y, z), (u, w) in zip(verts, uvs):
                v.append("v %.4f %.4f %.4f" % (-x / 16, y / 16, z / 16))
                vt.append("vt %.4f %.4f" % (u, w))
            # mirrored on X: the normal too, and the winding is reversed below
            vn.append("vn %.4f %.4f %.4f" % (-n[0], n[1], n[2]))
            idx = [k * 4 + i + 1 for i in range(4)][::-1]
            body.append("f " + " ".join("%d/%d/%d" % (i, i, k + 1) for i in idx))
            k += 1
    with open(path, "w") as fh:
        fh.write("# generated by christmas_view/tools/gen_textures.py\n")
        fh.write("\n".join(v + vt + vn + body) + "\n")


def ornament_model(cx, cy, cz, r, string_to=None):
    ball = fix_winding(sphere(cx, cy, cz, r), (cx, cy, cz))
    top = cy + r
    cap = fix_winding(box(cx - 1.25, top - 0.6, cz - 1.25, cx + 1.25, top + 1.2, cz + 1.25),
                      (cx, top + 0.3, cz))
    loop = fix_winding(box(cx - 0.4, top + 1.2, cz - 0.15, cx + 0.4, top + 2.0, cz + 0.15),
                       (cx, top + 1.6, cz))
    groups = [("ball", ball), ("cap", cap + loop)]
    if string_to is not None:
        sx, sy, sz = string_to
        s = fix_winding(box(cx - 0.15, top + 1.8, cz - 0.15, cx + 0.15, sy, cz + 0.15),
                        (cx, (top + sy) / 2, cz))
        if sx != cx or sz != cz:  # wall: a short arm to the wall
            s += fix_winding(box(min(sx, cx) - 0.15, sy - 0.3, cz - 0.15, max(sx, cx), sy, cz + 0.15),
                             ((sx + cx) / 2, sy - 0.15, cz))
        groups.append(("string", s))
    else:
        groups.append(("string", []))
    return groups


def transform(groups, fn):
    out = []
    for mat, quads in groups:
        out.append((mat, [([fn(*v) for v in verts], uvs) for verts, uvs in quads]))
    return out


def gen_ornament_models():
    # The models are built "as seen in the world" (y up) and then turned into
    # the frame the engine expects for paramtype2 = "wallmounted":
    # - floor: as is;
    # - ceiling: the engine turns the mesh upside down, so it is stored flipped;
    # - wall: the engine puts the -Y side of the mesh against the wall and +Z
    #   up, so a model built with the wall at -X is turned (x, y, z) -> (z, x, y).
    r = 3.6
    write_obj(os.path.join(MODELS, P + "ornament_floor.obj"), ornament_model(0, -8 + r, 0, r))
    ceiling = ornament_model(0, 8 - 6 - r, 0, r, string_to=(0, 8, 0))
    write_obj(os.path.join(MODELS, P + "ornament_ceiling.obj"),
              transform(ceiling, lambda x, y, z: (x, -y, -z)))
    wall = ornament_model(-8 + r + 1, -2.5, 0, r, string_to=(-8, -2.5 + r + 3.4, 0))
    write_obj(os.path.join(MODELS, P + "ornament_wall.obj"),
              transform(wall, lambda x, y, z: (z, x, y)))


# ================================================================ pine needles garland
def gen_garland_needles(n_frames=4, S=32):
    rng = random.Random(77)
    frames = blank(S, S * n_frames)
    colors = [(255, 60, 60), (255, 214, 60), (80, 170, 255), (90, 230, 110), (255, 130, 220)]
    # two wavy strings of lights across the tile
    wires = []
    for base, amp, ph in ((9, 3, 0.0), (23, 3, 1.7)):
        pts = [(x, base + amp * math.sin(x / S * 2 * math.pi + ph)) for x in range(S)]
        wires.append(pts)
    bulbs = []
    for wi, pts in enumerate(wires):
        for i, x in enumerate(range(2 + wi * 3, S, 6)):
            bulbs.append((x, pts[x][1], colors[(i + wi * 2) % len(colors)], (i + wi) % n_frames))
    baubles = [(5, 16, RED), (19, 2, GOLD), (27, 15, (60, 120, 230, 255)), (13, 28, RED)]
    for f in range(n_frames):
        img = blank(S, S)
        px = img.load()
        for pts in wires:
            for x, y in pts:
                px[x, int(round(y))] = (40, 60, 30, 255)
        for (bx, by, col, phase) in bulbs:
            on = (f - phase) % n_frames < 2
            by = int(round(by)) + 1
            c = col if on else tuple(int(v * 0.45) for v in col)
            for dx, dy in ((0, 0), (0, 1)):
                if 0 <= by + dy < S:
                    px[bx + dx, by + dy] = c + (255,)
            if on:  # little glow around the lit bulb
                for dx, dy in ((-1, 0), (1, 0), (-1, 1), (1, 1), (0, -1), (0, 2)):
                    x, y = bx + dx, by + dy
                    if 0 <= x < S and 0 <= y < S and px[x, y][3] == 0:
                        px[x, y] = col + (150,)
                px[bx, by] = (255, 255, 230, 255)
        for (x, y, col) in baubles:
            disc(img, x + 0.5, y + 0.5, 1.6, col, (WHITE, tuple(int(v * 0.6) for v in col[:3]) + (255,)))
        frames.alpha_composite(img, (0, f * S))
    save(frames, "garland_needles.png")
    save(frames.crop((0, 0, S, S)), "garland_needles_inv.png")


# ================================================================ smartshop garland
def gen_shop_garland(n_frames=4, S=32):
    """Garland around the smartshop face instead of its border: a grey wire
    (coloured in init.lua with the status colour of the shop) and a separate
    layer of blinking multicoloured bulbs."""
    colors = [(255, 60, 60), (255, 214, 60), (80, 170, 255), (90, 230, 110), (255, 130, 220)]
    wire = blank(S, S * n_frames)
    wp = wire.load()
    for f in range(n_frames):
        for i in range(S):
            for (x, y) in ((i, 0), (i, S - 1), (0, i), (S - 1, i), (i, 1), (i, S - 2), (1, i), (S - 2, i)):
                outer = x in (0, S - 1) or y in (0, S - 1)
                twist = (i // 2) % 2 == (0 if outer else 1)
                v = 235 if twist else 150
                wp[x, f * S + y] = (v, v, v, 255)
    # bulb positions along the inner side of the wire, clockwise
    pos = []
    for k in range(6):
        t = 3 + k * 5
        pos += [(t, 2, "t")]
    for k in range(6):
        t = 3 + k * 5
        pos += [(S - 4, t, "r")]
    for k in range(6):
        t = S - 5 - k * 5
        pos += [(t, S - 4, "b")]
    for k in range(6):
        t = S - 5 - k * 5
        pos += [(2, t, "l")]
    bulbs = blank(S, S * n_frames)
    for f in range(n_frames):
        img = blank(S, S)
        px = img.load()
        for i, (x, y, side) in enumerate(pos):
            col = colors[i % len(colors)]
            on = (f - i) % n_frames < 2
            c = col if on else tuple(int(v * 0.45) for v in col)
            cells = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            if on:
                for (cx, cy) in cells:
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        gx, gy = cx + dx, cy + dy
                        if 2 <= gx < S - 2 and 2 <= gy < S - 2 and (gx, gy) not in cells:
                            px[gx, gy] = col + (120,)
            for (cx, cy) in cells:
                px[cx, cy] = c + (255,)
            if on:
                px[x, y] = (255, 255, 230, 255)
        bulbs.alpha_composite(img, (0, f * S))
    save(wire, "shop_wire.png")
    save(bulbs, "shop_bulbs.png")


# ================================================================ bones -> snowman
# The node box lives in init.lua (units of 1/16):
#   bottom ball +-5, y -8..-2   middle +-4, y -2..1.5   scarf +-3.5, y 1.5..2.5
#   head +-3, y 2.5..6   hat brim +-3.5, y 6..6.5   hat crown +-2.5, y 6.5..8
#   nose x +-0.5, y 3.5..4.5, z -5.5..-3   arms x -8..8, y 0..1, z +-0.5
# Node box faces take their UV from the position inside the node, so every
# tile is painted as a map of what sits at that place.
def gen_snowman_bones(S=32):
    rng = random.Random(1225)
    HAT = (30, 30, 36, 255)

    def snow(y, ball_bottom):
        c = SNOW if rng.random() > 0.18 else SNOW_S
        if y - ball_bottom < 0.6:
            c = SNOW_S
        return c

    def ball_bottom(y):
        return -8 if y < -2 else (-2 if y < 1.5 else 2.5)

    def bands(y):
        if y >= 6.5:
            return RED if y < 7 else HAT
        if y >= 6:
            return HAT
        if 1.5 <= y < 2.5:
            return RED if int((y - 1.5) * 4) % 2 == 0 or rng.random() < 0.7 else RED_L
        return None

    def face(kind):
        img = blank(S, S)
        px = img.load()
        for py in range(S):
            for pxx in range(S):
                u = (pxx + 0.5) * 16 / S - 8
                v = 8 - (py + 0.5) * 16 / S
                c = None
                if kind == "top":
                    r = max(abs(u), abs(v))
                    if r <= 2.5:
                        c = HAT
                    elif r <= 3.5:
                        c = HAT
                    elif abs(v) < 0.5 and abs(u) >= 5:
                        c = BROWN if abs(u) < 7.5 else BROWN_D
                    else:
                        c = snow(0, -8)
                elif kind == "bottom":
                    c = SNOW_S
                else:
                    x, y = u, v
                    c = bands(y)
                    if c is None and 0 <= y < 1:
                        if (kind in ("front", "back") and abs(x) >= 4) or (kind == "side" and abs(x) < 0.5):
                            c = BROWN if kind != "side" else BROWN_D
                    if c is None and kind == "side" and 3.5 <= y < 4.5 and 3 <= abs(x) <= 5.5:
                        c = CARROT
                    if c is None and kind == "front":
                        if 3.5 <= y < 4.5 and abs(x) < 0.5:
                            c = CARROT
                        elif 4.75 <= y < 5.5 and 1 <= abs(x) < 2:
                            c = COAL
                        elif 2.75 <= y < 3.25 and abs(x) < 2 and int((x + 2) * 2) % 2 == 0:
                            c = COAL
                        elif abs(x) < 0.75 and any(b <= y < b + 0.75 for b in (0.5, -1.25, -3.75, -5.75)) \
                                and not (0 <= y < 1 and abs(x) >= 4):
                            c = COAL
                    if c is None:
                        c = snow(y, ball_bottom(y))
                px[pxx, py] = c
        return img

    save(face("top"), "bones_top.png")
    save(face("bottom"), "bones_bottom.png")
    save(face("side"), "bones_side.png")
    save(face("back"), "bones_back.png")
    save(face("front"), "bones_front.png")


# ================================================================ santa hats (armor)
HAT_RED = RED
HAT_RED_D = RED_D


def gen_hats():
    # 3d_armor texture: 64x32 player skin layout, the hat layer of the head
    # is x 32..63, y 0..15 (top 40..47 x 0..7, sides at y 8..15)
    img = blank(64, 32)
    px = img.load()
    rng = random.Random(5)
    for x in range(40, 48):           # top
        for y in range(0, 8):
            px[x, y] = jitter(HAT_RED if (x + y) % 5 else HAT_RED_D, 6, rng)
    for x in range(32, 64):           # around the head: red cap + white fur band
        for y in range(8, 12):
            if y < 10:
                c = HAT_RED if (x + y) % 6 else HAT_RED_D
            else:
                c = FUR if rng.random() < 0.75 else FUR_S
            px[x, y] = jitter(c, 6, rng)
    # pompom hanging on the back of the head (back face x 56..63)
    # the tip falls down on the left side (x 48..55) with a pompom
    for (x, y) in [(51, 10), (52, 10), (51, 11), (52, 11), (51, 12), (52, 12)]:
        px[x, y] = jitter(HAT_RED, 6, rng)
    for (x, y) in [(50, 13), (51, 13), (52, 13), (53, 13), (50, 14), (51, 14), (52, 14),
                   (53, 14), (51, 15), (52, 15)]:
        px[x, y] = WHITE
    for (x, y) in [(43, 3), (44, 3), (43, 4), (44, 4)]:
        px[x, y] = HAT_RED_D
    save(img, "hat_head.png")

    # preview: 32x64 front view, the head is x 8..23, y 0..15
    pv = blank(32, 64)
    p = pv.load()
    for x in range(7, 25):
        for y in range(0, 7):
            if y < 3:
                if x in (7, 24):
                    continue
                c = HAT_RED if (x + y) % 6 else HAT_RED_D
            else:
                c = FUR if rng.random() < 0.75 else FUR_S
            p[x, y] = jitter(c, 6, rng)
    disc(pv, 25.5, 3.5, 2.6, WHITE, (WHITE, FUR_S))
    save(pv, "hat_preview.png")

    # inventory badge: small santa hat in the top right corner
    hat = from_rows([
        "......rrrWW",
        "....rrrr.WW",
        "...rrrr....",
        "..rrrrr....",
        ".rrrrrrr...",
        "WWWWWWWWW..",
        "WWWWWWWWW..",
    ], {"r": HAT_RED, "W": WHITE})
    badge = blank(32, 32)
    badge.alpha_composite(outline(pad(hat)), (32 - 13, 0))
    save(badge, "hat_badge.png")


# ================================================================ sheep
def tri_normal(v):
    n = np.cross(v[1] - v[0], v[2] - v[0])
    ln = np.linalg.norm(n)
    return n / ln if ln > 0 else n


def paint_sheep(model_path, alpha_srcs, out_name, W, H):
    """Overlay with a red cape with white fur trim on the back and a santa hat
    on the head. Painted in 3D on the model and written into its UV space."""
    m = b3d.load(model_path)
    V, UV, TR, VB = m["verts"], m["uv"], m["tris"], m["vbone"]

    def tbone(t):
        bs = [VB[i] for i in t]
        return max(set(bs), key=bs.count)
    tb = [tbone(t) for t in TR]
    tn = np.array([tri_normal(V[t]) for t in TR])
    head = [i for i, b in enumerate(tb) if b == "Head"]
    front_i = max(head, key=lambda i: V[TR[i]][:, 2].mean())
    if tn[front_i][2] < 0:
        tn = -tn

    hv = np.concatenate([V[TR[i]] for i in head])
    # head core without ears / horns: the x range of the front-facing faces
    fronts = [i for i in head if tn[i][2] > 0.7]
    fz = max(V[TR[i]][:, 2].mean() for i in fronts)
    fronts = [i for i in fronts if V[TR[i]][:, 2].mean() > fz - 1.6]
    fv = np.concatenate([V[TR[i]] for i in fronts])
    fx0, fx1 = fv[:, 0].min(), fv[:, 0].max()
    hy0, hy1 = hv[:, 1].min(), hv[:, 1].max()
    hz0, hz1 = hv[:, 2].min(), hv[:, 2].max()
    body = np.concatenate([V[TR[i]] for i, b in enumerate(tb) if b == "Root"])
    by0, by1 = body[:, 1].min(), body[:, 1].max()
    bz0, bz1 = body[:, 2].min(), body[:, 2].max()
    bxc = (body[:, 0].min() + body[:, 0].max()) / 2

    hat_h = (hy1 - hy0) * 0.3        # how far the hat comes down the head
    cape_low = by1 - (by1 - by0) * 0.38  # lowest point of the cape on the flanks
    rng = random.Random(11)

    def color(p, n, bone):
        x, y, z = p
        if bone == "Head":
            if not (fx0 - 0.2 <= x <= fx1 + 0.2):
                return None  # ears, horns
            band = hy1 - hat_h
            if n[1] > 0.7:
                return HAT_RED
            if y > band + 0.75:
                # pompom on the right side, near the back
                if n[0] < -0.7 and abs(y - (hy1 - 0.6)) < 0.6 and abs(z - (hz0 + 1.0)) < 0.7:
                    return WHITE
                return HAT_RED if (int(y * 3) + int(z * 3)) % 7 else HAT_RED_D
            if y > band:
                return FUR if rng.random() < 0.75 else FUR_S
            return None
        if bone == "Root":
            t = (z - bz0) / (bz1 - bz0)  # 0 tail .. 1 neck
            if t > 0.9:
                # collar at the neck
                if n[1] > 0.3 or (abs(n[0]) > 0.7 and y > cape_low):
                    return FUR if rng.random() < 0.8 else FUR_S
                return None
            if n[1] > 0.7:
                # top of the back: red, a gold clasp near the neck
                if t > 0.8 and abs(x - bxc) < 0.5:
                    return GOLD
                return RED if (int(x * 2) + int(z * 2)) % 5 else RED_D
            if abs(n[0]) > 0.7 or n[2] < -0.7:
                # the cape hangs a bit lower at the back
                low = cape_low - (0.6 * (1 - t))
                if y > low + 0.6:
                    return RED if (int(y * 2) + int(z * 2)) % 5 else RED_D
                if y > low:
                    return FUR if rng.random() < 0.75 else FUR_S
            return None
        return None  # legs

    img = np.zeros((H, W, 4), np.uint8)
    for ti, t in enumerate(TR):
        uv = UV[t] * np.array([W, H])
        x0, y0 = np.floor(uv.min(0)).astype(int)
        x1, y1 = np.ceil(uv.max(0)).astype(int)
        a, b, c = uv
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-9:
            continue
        for py in range(max(0, y0 - 1), min(H, y1 + 1)):
            for px_ in range(max(0, x0 - 1), min(W, x1 + 1)):
                q = (px_ + 0.5, py + 0.5)
                l1 = ((b[1] - c[1]) * (q[0] - c[0]) + (c[0] - b[0]) * (q[1] - c[1])) / den
                l2 = ((c[1] - a[1]) * (q[0] - c[0]) + (a[0] - c[0]) * (q[1] - c[1])) / den
                l3 = 1 - l1 - l2
                if min(l1, l2, l3) < -0.02:
                    continue
                p = V[t[0]] * l1 + V[t[1]] * l2 + V[t[2]] * l3
                col = color(p, tn[ti], tb[ti])
                if col is not None:
                    img[py, px_] = jitter(col, 6, rng)
    vis = np.zeros((H, W), bool)
    for src in alpha_srcs:
        a = Image.open(src).convert("RGBA").resize((W, H), Image.NEAREST)
        vis |= np.array(a)[:, :, 3] > 0
    img[~vis] = 0
    Image.fromarray(img).save(os.path.join(TEX, P + out_name))


def paint_old_sheep(model_path, alpha_srcs, out_name, W, H):
    """The older mobs_animal sheep (survival_shelter) maps every side of the
    body box onto one and the same texture rectangle, and every side of the
    head onto another one, so nothing can be painted on the back only. The
    overlay is painted right in UV space instead: a red wrap with white fur
    edges around the middle of the body (it shows on the back, the flanks
    and the belly alike) and a red cap band with white fur around the head."""
    m = b3d.load(model_path)
    V, UV, TR, VB = m["verts"], m["uv"], m["tris"], m["vbone"]

    def tbone(t):
        bs = [VB[i] for i in t]
        return max(set(bs), key=bs.count)

    def biggest(bone, axis, sign):
        best, area = None, 0
        for t in TR:
            if tbone(t) != bone:
                continue
            n = tri_normal(V[t])
            if abs(n[axis]) > 0.7:
                a = np.linalg.norm(np.cross(V[t][1] - V[t][0], V[t][2] - V[t][0]))
                if a > area:
                    best, area = t, a
        uv = UV[best] * np.array([W, H])
        return uv.min(0), uv.max(0)
    (bu0, bv0), (bu1, bv1) = biggest("Root", 1, 1)   # body: u along the length
    (hu0, hv0), (hu1, hv1) = biggest("Head", 0, -1)  # head side: v from the top
    rng = random.Random(13)
    img = np.zeros((H, W, 4), np.uint8)
    blen = bu1 - bu0
    c0, c1 = bu0 + blen * 0.12, bu0 + blen * 0.62  # neck side of the body
    trim = blen * 0.05
    for y in range(H):
        for x in range(W):
            u, v = x + 0.5, y + 0.5
            col = None
            if bu0 <= u <= bu1 and bv0 <= v <= bv1 and c0 <= u <= c1:
                if u < c0 + trim or u > c1 - trim:
                    col = FUR if rng.random() < 0.75 else FUR_S
                else:
                    col = RED if (x + y) % 7 else RED_D
            hh = hv1 - hv0
            if hu0 <= u <= hu1 and hv0 <= v <= hv1:
                if v < hv0 + hh * 0.3:
                    col = HAT_RED if (x + 2 * y) % 7 else HAT_RED_D
                elif v < hv0 + hh * 0.42:
                    col = FUR if rng.random() < 0.75 else FUR_S
            if col:
                img[y, x] = jitter(col, 6, rng)
    vis = np.zeros((H, W), bool)
    for src in alpha_srcs:
        a = Image.open(src).convert("RGBA").resize((W, H), Image.NEAREST)
        vis |= np.array(a)[:, :, 3] > 0
    img[~vis] = 0
    Image.fromarray(img).save(os.path.join(TEX, P + out_name))


# ================================================================ unified_inventory
urnd = random.Random(2512 + 31)
UI_PX = 40  # texture pixels per formspec unit for the garland and the drifts


def snow_tile(size=48, frames=48, flakes=2, seed=1):
    """Seamless falling snow: every flake falls exactly size*k px during the
    loop and sways sideways, so the animation and the tiling have no seams."""
    rng = random.Random(seed)
    shapes = [
        [(0, 0)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
    ]
    fl = []
    for _ in range(flakes):
        fl.append((rng.uniform(0, size), rng.uniform(0, size), 1,
                   rng.uniform(1, 3), rng.uniform(0, 2 * math.pi),
                   rng.choices(shapes, (5, 3, 2))[0], rng.randint(170, 240)))
    img = blank(size, size * frames)
    px = img.load()
    for f in range(frames):
        t = f / frames
        for (x0, y0, k, amp, ph, shape, a) in fl:
            x = x0 + amp * math.sin(2 * math.pi * t * 2 + ph)
            y = y0 + size * k * t
            for dx, dy in shape:
                xx = int(round(x + dx)) % size
                yy = int(round(y + dy)) % size
                px[xx, f * size + yy] = (255, 255, 255, a)
    return img


def drift(w, h):
    """Snow drift strip: bumpy top, blue shadows, glitter."""
    img = blank(w, h)
    px = img.load()
    surf = [int(h * 0.38 + 5 * math.sin(x / 37.0) + 3 * math.sin(x / 13.0 + 1)
                + 2 * math.sin(x / 5.3)) for x in range(w)]
    for x in range(w):
        for y in range(max(0, surf[x]), h):
            d = y - surf[x]
            if d < 2:
                c = SNOW
            elif d < 6:
                c = (236, 244, 255, 255)
            else:
                t = (y - surf[x]) / max(1, h - surf[x])
                c = (int(228 - 40 * t), int(238 - 34 * t), 255, 255)
            if urnd.random() < 0.02:
                c = WHITE
            px[x, y] = c
    r = 7
    for y in range(h - r, h):
        for x in range(r):
            if math.hypot(r - x - 0.5, y - (h - r) + 0.5) > r:
                px[x, y] = T
                px[w - 1 - x, y] = T
    return img


SNOWMAN = [
    ".....kkkk.....",
    ".....kkkk.....",
    "....kkkkkk....",
    "...kRRRRRRk...",
    "....wwwwww....",
    "...wwkwwkwww..",
    "...wwwwOOOww..",
    "...wwwwwwwww..",
    "....rrrrrrrr..",
    "...wwwrrwwww..",
    ".b.wwwrrwwwwb.",
    "..bwwwkwwwwb..",
    "..wwwwwwwwww..",
    ".wwwwwkwwwwww.",
    ".wwwwwwwwwwws.",
    "wwwwwwwwwwwwss",
    "wwwwwwwwwwwwss",
    ".wwwwwwwwwwss.",
    "..wwwwwwwwss..",
]
SNOWMAN_PAL = {"k": COAL, "R": RED, "w": SNOW, "s": SNOW_S, "O": CARROT, "r": RED_L,
               "b": BROWN_D}

GINGER = [
    "...bbbb...",
    "..bbbbbb..",
    "..bWbbWb..",
    "..bbbbbb..",
    "..bWWWWb..",
    "...bbbb...",
    "bbbbbbbbbb",
    "WbbbRbbbbW",
    "...bbbb...",
    "...bRbb...",
    "..bbbbbb..",
    "..bb..bb..",
    ".bbb..bbb.",
    ".WW....WW.",
]
GINGER_PAL = {"b": BROWN, "W": WHITE, "R": RED}


def gift_sprite(w, h, paper, ribbon):
    img = blank(w, h + 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 4, w - 1, h + 3], fill=paper)
    d.rectangle([0, 4, w - 1, 5], fill=tuple(min(255, v + 30) for v in paper[:3]) + (255,))
    cx = w // 2
    d.rectangle([cx - 1, 4, cx, h + 3], fill=ribbon)
    d.rectangle([0, 4 + h // 2, w - 1, 5 + h // 2], fill=ribbon)
    d.polygon([(cx, 4), (cx - 4, 0), (cx - 4, 4)], fill=ribbon)
    d.polygon([(cx - 1, 4), (cx + 3, 0), (cx + 3, 4)], fill=ribbon)
    return outline(pad(img))


GROUND_H = 0.9
UI_WIDTHS = (17.75, 14)
UI_HEIGHTS = (12.25, 12.5, 9.75)
BULB_COLORS = [(255, 64, 64), (255, 210, 60), (80, 160, 255), (80, 230, 110), (255, 120, 210)]


def garland_strip(units, thick=0.5):
    """Horizontal strip: pine twig wire sagging between hooks with glowing bulbs."""
    w, h = int(round(units * UI_PX)), int(round(thick * UI_PX))
    img = blank(w, h)
    px = img.load()
    rng = random.Random(int(units * 100))
    span = UI_PX * 1.6  # distance between hooks
    n = max(1, round(w / span))
    span = w / n

    def wy(x):
        t = (x % span) / span
        return 3 + 5 * math.sin(math.pi * t)
    for x in range(w):
        y = wy(x)
        for k in range(-3, 4):
            if rng.random() < 0.75 - abs(k) * 0.12:
                yy = int(round(y + k + rng.uniform(-1, 1)))
                if 0 <= yy < h:
                    px[x, yy] = jitter(rng.choice([GREEN, GREEN_D, GREEN_L]), 10, rng)
        yy = int(round(y))
        if 0 <= yy < h:
            px[x, yy] = (70, 60, 30, 255)
    out = blank(w, h)
    gp = out.load()
    step = span / 3
    bulbs = []
    x, i = step / 2, 0
    while x < w - 2:
        bulbs.append((x, wy(x) + 2, BULB_COLORS[i % len(BULB_COLORS)]))
        x += step
        i += 1
    for (x, y, col) in bulbs:  # soft glow under everything
        cx, cy = x, y + 5
        for yy in range(int(cy - 9), int(cy + 10)):
            for xx in range(int(cx - 9), int(cx + 10)):
                if 0 <= xx < w and 0 <= yy < h:
                    dd = math.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 0.9)
                    if dd < 9:
                        a = int(150 * (1 - dd / 9) ** 1.6)
                        if a > gp[xx, yy][3]:
                            gp[xx, yy] = col + (a,)
    out.alpha_composite(img)
    d = ImageDraw.Draw(out)
    for (x, y, col) in bulbs:
        d.rectangle([x - 1.5, y - 1, x + 1.5, y + 1], fill=(60, 80, 60, 255))
        d.ellipse([x - 3, y + 1, x + 3, y + 10], fill=col + (255,))
        d.ellipse([x - 1.5, y + 3, x, y + 5], fill=(255, 255, 240, 255))
    return out


def gen_ui():
    save(snow_tile(seed=1), "ui_snow1.png")
    save(snow_tile(seed=3, flakes=2), "ui_snow2.png")
    save(drift(1024, 48), "ui_drift.png")
    save(outline(pad(from_rows(SNOWMAN, SNOWMAN_PAL))), "ui_snowman.png")
    save(outline(pad(from_rows(GINGER, GINGER_PAL))), "ui_ginger.png")
    save(gift_sprite(12, 9, RED, GOLD), "ui_gift_red.png")
    save(gift_sprite(10, 11, (40, 130, 70, 255), RED), "ui_gift_green.png")
    save(gift_sprite(14, 8, (50, 100, 210, 255), WHITE), "ui_gift_blue.png")
    save(cane_sprite(22), "ui_cane.png")
    save(cane_sprite(22, flip=True), "ui_cane_flip.png")
    # garland around the window: one strip per edge, drawn for the exact
    # window sizes of the servers (full / lite layout, the window is
    # GROUND_H taller because of the snow drift strip)
    for w in UI_WIDTHS:
        save(garland_strip(w), "ui_garland_h_%d.png" % round(w * 100))
    for h in UI_HEIGHTS:
        save(garland_strip(h + GROUND_H).transpose(Image.ROTATE_270),
             "ui_garland_v_%d.png" % round(h * 100))


# ================================================================
def main():
    os.makedirs(TEX, exist_ok=True)
    os.makedirs(MODELS, exist_ok=True)
    gen_gifts()
    gen_apple()
    gen_wreaths()
    gen_candy()
    gen_ornament_textures()
    gen_ornament_models()
    gen_garland_needles()
    gen_shop_garland()
    gen_snowman_bones()
    gen_hats()
    gen_ui()
    if len(sys.argv) >= 4:
        new_model, new_tex = sys.argv[1].split(":", 1)
        new_tex = new_tex.split(",")
        shaved = os.path.join(os.path.dirname(new_tex[0]), "mobs_sheep_shaved.png")
        paint_sheep(new_model, new_tex, "sheep.png", 128, 128)
        paint_sheep(new_model, [new_tex[0], shaved], "sheep_shaved.png", 128, 128)
        old_model, old_tex = sys.argv[2].split(":", 1)
        paint_old_sheep(old_model, old_tex.split(","), "sheep_old.png", 160, 144)
        sh_model, sh_tex = sys.argv[3].split(":", 1)
        paint_old_sheep(sh_model, sh_tex.split(","), "sheep_old_shaved.png", 160, 144)


if __name__ == "__main__":
    main()
