# -*- coding: utf-8 -*-
"""Vertical ink painting: Wah Kei Industrial Building, Kwai Chung, at moonrise."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 1.5
LW, LH = 1200, 1600
W, H = int(LW * S), int(LH * S)
PAPER = np.array([247.0, 241.0, 228.0], np.float32)
INK = np.array([24.0, 23.0, 18.0], np.float32)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH = os.path.join(OUT_DIR, "huaji_ink.png")
PREVIEW_PATH = os.path.join(OUT_DIR, "huaji_ink_preview.png")

rng = np.random.default_rng(29)
random.seed(29)
D = np.zeros((H, W), np.float32)


# ------------------------------------------------------------------ helpers
def value_noise(cell, octaves=4, seed=0):
    r = np.random.default_rng(seed)
    total = np.zeros((H, W), np.float32)
    amp, norm = 1.0, 0.0
    c = cell
    for _ in range(octaves):
        gh = max(2, int(H / (c * S)) + 3)
        gw = max(2, int(W / (c * S)) + 3)
        g = r.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        total += np.asarray(im, np.float32) / 255.0 * amp
        norm += amp
        amp *= 0.5
        c *= 0.5
    return np.clip(total / norm, 0, 1)


N = value_noise(170, 4, 3)
N2 = value_noise(38, 3, 8)
F = value_noise(3.0, 2, 21)
Y = np.arange(H, dtype=np.float32)[:, None] / S
X = np.arange(W, dtype=np.float32)[None, :] / S


def poly_mask(points):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon([(x * S, y * S) for x, y in points], fill=255)
    return im


def rect_mask(x, y, w, h):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=255)
    return im


def ellipse_mask(cx, cy, rx, ry):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=255)
    return im


def A(im):
    return np.asarray(im, np.float32) / 255.0


def blur_a(a, r):
    if r <= 0:
        return a
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r * S)), np.float32) / 255.0


def comp(a, d=1.0, erase=False, blur=0.0):
    global D
    a = np.clip(a, 0, 1)
    if blur:
        a = blur_a(a, blur)
    x = np.clip(a * d, 0, 1)
    if erase:
        D *= (1.0 - x)
    else:
        D = 1.0 - (1.0 - D) * (1.0 - x)


def wash(mask, tone, texture=0.3, blur=0.8, erase=False):
    a = A(mask)
    if texture:
        a = a * (1 - texture * 0.5 + texture * N2)
    comp(a, tone, erase=erase, blur=blur)


def paper(mask, blur=0.5):
    comp(A(mask), 1.0, erase=True, blur=blur)


def bar(p1, p2, w1, w2):
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = max(1e-3, math.hypot(dx, dy))
    nx, ny = -dy / L, dx / L
    return [(x1 + nx * w1 / 2, y1 + ny * w1 / 2),
            (x2 + nx * w2 / 2, y2 + ny * w2 / 2),
            (x2 - nx * w2 / 2, y2 - ny * w2 / 2),
            (x1 - nx * w1 / 2, y1 - ny * w1 / 2)]


def solid(shape, d=0.9, blur=0.4):
    comp(A(poly_mask(shape)), d, blur=blur)


def brush(strokes, tone, texture=0.0, blur=0.4, erase=False):
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for pts, w0, w1 in strokes:
        for k in range(len(pts) - 1):
            x1, y1 = pts[k]
            x2, y2 = pts[k + 1]
            n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 1.2))
            for i in range(n + 1):
                tt = i / n
                x = x1 + (x2 - x1) * tt
                y = y1 + (y2 - y1) * tt
                w = w0 * (1 - tt) + w1 * tt
                rr = max(0.5, w * 0.5) * S
                dr.ellipse([x * S - rr, y * S - rr, x * S + rr, y * S + rr], fill=255)
    a = A(im)
    if texture:
        a = a * (1 - texture * 0.5 + texture * F)
    comp(a, tone, erase=erase, blur=blur)


def ridge_line(peaks, base, seed, rough=1.3):
    r = random.Random(seed)
    xs = np.linspace(-40, LW + 40, 800)
    env = np.zeros_like(xs)
    for cx, amp, sig in peaks:
        env += amp * np.exp(-((xs - cx) / sig) ** 2)
    waves = [(1.0, 300, r.uniform(0, 6.28)), (0.55, 120, r.uniform(0, 6.28)),
             (0.32, 52, r.uniform(0, 6.28)), (0.18, 23, r.uniform(0, 6.28)),
             (0.10, 11, r.uniform(0, 6.28))]
    noise = sum(a * np.sin(2 * np.pi * xs / lam + ph) for a, lam, ph in waves)
    noise /= sum(a for a, _, _ in waves)
    noise = (0.5 + 0.5 * noise) ** 1.45
    return xs, base - env * (0.52 + 0.62 * rough * noise)


# ------------------------------------------------------------------ sky
background = np.ones((H, W, 3), np.float32) * PAPER
background *= (0.975 + 0.045 * N[..., None])
D += np.clip((Y - 260) / 700, 0, 1) * 0.03 * (0.5 + 0.5 * N)

# moon
rr = np.sqrt((X - 280) ** 2 + (Y - 300) ** 2)
halo = np.exp(-((rr - 58) / 24) ** 2) * (rr > 53)
comp(halo, 0.08, blur=8)
comp(np.exp(-((rr - 58) / 55) ** 2), 0.03, blur=14)
comp(A(ellipse_mask(280, 300, 54, 54)), 1.0, erase=True, blur=0.5)
for cy, rx, ry, tone in [(292, 120, 6, 0.045), (318, 160, 7, 0.03)]:
    comp(A(ellipse_mask(280, cy, rx, ry)) * (0.4 + 0.6 * N), tone, blur=6)

# ------------------------------------------------------------------ mountains
def mountain(peaks, base, tone, seed, cun_n=0, crest=0.09):
    r = random.Random(seed)
    xs, ys = ridge_line(peaks, base, seed)
    pts = [(float(x), float(y)) for x, y in zip(xs, ys)]
    m = poly_mask(pts + [(LW + 40, 1620), (-40, 1620)])
    ma = A(m)
    rc = np.interp(np.arange(W) / S, xs, ys).astype(np.float32)
    t = (Y - rc[None, :]) / np.maximum(1.0, 980 - rc[None, :])
    grad = np.clip(1 - t, 0, 1) ** 1.05
    comp(ma * grad * (0.45 + 0.8 * N2) * (0.8 + 0.4 * F), tone, blur=1.3)
    rim = np.exp(-np.clip((Y - rc[None, :]) / 3.0, 0, 8) ** 2) * ma
    comp(rim * (0.6 + 0.5 * N2), crest * 1.3, blur=0.8)
    if cun_n:
        sm = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(sm)
        for _ in range(cun_n):
            x = r.uniform(-20, 1050)
            top = float(np.interp(x, xs, ys)) + r.uniform(10, 150)
            L = r.uniform(6, 28)
            sl = r.uniform(-6, 6)
            for i in range(7):
                tt = i / 6.0
                px, py = x + sl * tt, top + L * tt
                rad = r.uniform(0.5, 1.2) * S
                dr.ellipse([px * S - rad, py * S - rad, px * S + rad, py * S + rad], fill=255)
        comp(A(sm) * ma * (0.35 + 0.9 * F), 0.18, blur=0.6)
    for _ in range(24):
        x = r.uniform(0, 1000)
        y = float(np.interp(x, xs, ys)) + r.uniform(-1, 12)
        comp(A(ellipse_mask(x, y, r.uniform(0.7, 2.2), r.uniform(0.7, 2.0))),
             r.uniform(0.1, 0.3), blur=0.4)
    for _ in range(5):
        x0 = r.uniform(0, 900)
        x1 = x0 + r.uniform(50, 140)
        seg = [(float(x), float(y)) for x, y in zip(xs, ys) if x0 <= x <= x1]
        if len(seg) > 3:
            brush([(seg, 1.4, 0.7)], 0.26, blur=0.6)
    return m


mountain([(180, 250, 100), (500, 220, 110), (820, 150, 120)], 700, 0.24, 51)
mountain([(280, 300, 110), (620, 250, 95), (940, 180, 140)], 760, 0.36, 52, 60, 0.08)
mountain([(120, 220, 90), (430, 190, 85), (720, 130, 100), (1030, 90, 150)], 820, 0.46, 53, 90, 0.10)

# mist at mountain feet
r = random.Random(61)
for yy in (820, 880, 940):
    for _ in range(5):
        cx = r.uniform(-100, 1300)
        comp(A(ellipse_mask(cx, yy + r.uniform(-15, 15), r.uniform(220, 440), r.uniform(18, 42))),
             0.5, erase=True, blur=13)
comp(A(ellipse_mask(600, 960, 700, 40)), 0.3, erase=True, blur=18)

# ------------------------------------------------------------------ city
# distant blocks
for bx, by, bw, bh in [(120, 980, 90, 180), (760, 940, 80, 220), (840, 1000, 70, 160),
                       (900, 960, 60, 200)]:
    m = rect_mask(bx, by, bw, bh)
    paper(m, blur=0.4)
    wash(m, 0.28, texture=0.25, blur=0.9)
    brush([([(bx - 1, by), (bx + bw + 1, by)], 1.8, 1.0)], 0.4, blur=0.7)


def building(x, y, w, h, tone, seed, roof="flat", lights=False):
    r = random.Random(seed)
    m = rect_mask(x, y, w, h)
    paper(m, blur=0.5)
    grad = np.clip(1.08 - (Y - y) / max(20, h) * 0.18, 0.85, 1.1)
    comp(A(m) * grad * (0.75 + 0.45 * N), tone, blur=0.9)
    # broad vertical brushwork
    strokes = []
    for _ in range(4):
        bx = x + r.uniform(3, w - 3)
        strokes.append(([(bx, y + r.uniform(3, 25)), (bx + r.uniform(-2, 2), y + h - r.uniform(5, 30))],
                        r.uniform(18, 40), r.uniform(6, 16)))
    brush(strokes, min(0.10, tone * 0.22), texture=0.7, blur=1.8)
    # side shade
    sm = rect_mask(x + w - max(6, w * 0.1), y, max(6, w * 0.1), h)
    wash(sm, min(0.28, tone * 0.6), texture=0.2, blur=1.2)
    # edges
    brush([([(x + 1, y + h), (x + 1, y + h * 0.4), (x + 1.6, y + 2)], 2.8, 1.6)],
          min(0.8, tone * 2.0), texture=0.3, blur=0.6)
    brush([([(x - 1, y), (x + w * 0.5, y - 1.5), (x + w + 1, y)], 3.2, 1.8)],
          min(0.75, tone * 1.8), texture=0.25, blur=0.6)
    # floor hints and vertical panels
    for _ in range(r.randint(1, 2)):
        px = x + r.uniform(0.12, 0.88) * w
        brush([([(px, y + 6), (px + r.uniform(-1, 1), y + h - 6)], r.uniform(1.4, 2.2), 0.8)],
              min(0.09, tone * 0.2), blur=1.2)
    for _ in range(r.randint(2, 4)):
        yy = y + r.uniform(0.12, 0.9) * h
        brush([([(x + 2, yy), (x + w - 2, yy + r.uniform(-1, 1))], 2.2, 1.2)],
              min(0.14, tone * 0.3), blur=0.9)
    # windows
    if lights:
        for _ in range(r.randint(8, 18)):
            xx = x + r.uniform(0.08, 0.86) * w
            yy = y + r.uniform(0.05, 0.95) * h
            brush([([(xx, yy), (xx + r.uniform(4, 9), yy)], 2.0, 1.6)],
                  r.uniform(0.5, 0.85), erase=True, blur=0.4)
    else:
        for _ in range(r.randint(4, 10)):
            xx = x + r.uniform(0.08, 0.86) * w
            yy = y + r.uniform(0.05, 0.95) * h
            brush([([(xx, yy), (xx + r.uniform(4, 9), yy)], 1.8, 1.6)],
                  r.uniform(0.18, 0.36), blur=0.5)
    # roof
    if roof == "saw":
        n = r.randint(3, 5)
        seg = w / n
        pts = [(x - 2, y + 2)]
        for k in range(n):
            pts += [(x + k * seg + seg * 0.5, y - r.uniform(12, 18)), (x + (k + 1) * seg, y + 2)]
        rm = poly_mask(pts)
        paper(rm, blur=0.5)
        wash(rm, min(0.65, tone * 1.1), texture=0.35, blur=0.8)
    elif roof == "pitch":
        rm = poly_mask([(x - 6, y + 2), (x + w * 0.5, y - r.uniform(24, 36)), (x + w + 6, y + 2)])
        paper(rm, blur=0.5)
        wash(rm, min(0.6, tone * 1.05), texture=0.3, blur=0.8)
    else:
        comp(A(rect_mask(x - 2, y - 8, w + 4, 8)), min(0.8, tone * 1.5), blur=0.5)
        brush([([(x - 2, y), (x + w + 2, y)], 3.2, 1.8)], min(0.75, tone * 1.7), blur=0.6)
    # roof clutter
    if r.random() < 0.9:
        tx = x + w * r.uniform(0.06, 0.6)
        tw = r.uniform(10, 18)
        tm = rect_mask(tx, y - 16, tw, 15)
        paper(tm, blur=0.3)
        wash(tm, 0.35, texture=0.15, blur=0.4)
        brush([([(tx, y - 16), (tx + tw, y - 16)], 1.1, 1.0)], 0.55, blur=0.3)
    if r.random() < 0.65:
        ax = x + w * r.uniform(0.25, 0.8)
        brush([([(ax, y), (ax, y - r.uniform(12, 30))], 1.2, 0.6)], 0.6, blur=0.3)
    comp(A(ellipse_mask(x + w / 2, y + h + 3, w * 0.5, 6)), 0.18, blur=3)


# left cluster
building(-20, 1000, 120, 160, 0.48, 71, "flat", True)
building(92, 940, 110, 220, 0.55, 72, "flat", True)
building(196, 1010, 110, 150, 0.46, 73, "saw")
building(300, 950, 118, 210, 0.58, 74, "flat", True)
# chimney
chim = poly_mask([(236, 760), (254, 760), (258, 960), (232, 960)])
paper(chim, blur=0.5)
wash(chim, 0.62, texture=0.35, blur=0.8)
for yy in (800, 850, 900):
    brush([([(234, yy), (256, yy)], 1.3, 1.2)], 0.45, blur=0.4)
for dx, dy, sw in [(2, -50, 8), (14, -100, 12), (28, -150, 15)]:
    brush([([(245, 758), (245 + dx, 738), (238 + dx, 700), (241 + dx, 758 + dy)], sw, sw * 1.8)],
          0.12, texture=0.5, blur=4)


# towers
def tower(x, y, w, h, seed, sign=False):
    r = random.Random(seed)
    m = rect_mask(x, y, w, h)
    paper(m, blur=0.5)
    # solid concrete mass
    comp(A(m) * (0.88 + 0.22 * N), 0.72, blur=1.0)
    # four structural bays with slightly different ink values
    for j in range(4):
        bx = x + j * w / 4
        shift = r.uniform(-0.035, 0.045)
        bm = rect_mask(bx + 1, y + 1, w / 4 - 2, h - 2)
        comp(A(bm), abs(shift), erase=(shift < 0), blur=1.6)
        brush([([(bx, y + 4), (bx, y + h - 4)], 1.2, 0.8)], 0.14, blur=0.8)
    # right side shade
    side = rect_mask(x + w - 14, y, 14, h)
    wash(side, 0.14, texture=0.3, blur=1.0)
    # uneven weathered concrete patches
    for _ in range(6):
        px = x + r.uniform(0, w * 0.78)
        py = y + r.uniform(0, h * 0.78)
        pw = r.uniform(w * 0.14, w * 0.38)
        ph = r.uniform(h * 0.04, h * 0.18)
        comp(A(rect_mask(px, py, pw, ph)), r.uniform(0.035, 0.08), erase=True, blur=4.5)
    for _ in range(4):
        px = x + r.uniform(0, w * 0.7)
        py = y + r.uniform(0, h * 0.8)
        comp(A(rect_mask(px, py, r.uniform(w * 0.1, w * 0.3), r.uniform(h * 0.03, h * 0.12))),
             r.uniform(0.04, 0.08), blur=4)
    # irregular vertical weathering / pipes
    stains = []
    for _ in range(7):
        bx = x + r.uniform(6, w - 6)
        y0 = y + r.uniform(20, 160)
        y1 = y + r.uniform(300, h - 20)
        stains.append(([(bx, y0), (bx + r.uniform(-1.5, 1.5), y1)], r.uniform(1.4, 3.2),
                       r.uniform(0.8, 1.6)))
    brush(stains, 0.10, texture=0.5, blur=1.0)
    # edges
    brush([([(x + 1.5, y + h), (x + 1.5, y + 20), (x + 2.2, y + 2)], 4.2, 2.2)], 0.74, texture=0.3, blur=0.6)
    brush([([(x + w - 1.5, y + h), (x + w - 1.5, y + 4)], 2.8, 1.4)], 0.60, blur=0.5)
    brush([([(x - 1, y), (x + w / 2, y - 1.6), (x + w + 1, y)], 4.2, 2.2)], 0.80, texture=0.25, blur=0.6)
    # floor lines
    floors = 32
    fh = h / floors
    for i in range(1, floors):
        if i % 8 == 0:
            brush([([(x + 2, y + fh * i), (x + w - 2, y + fh * i)], 1.4, 0.9)], 0.14, blur=0.5)
        elif i % 2 == 0:
            brush([([(x + 2, y + fh * i), (x + w - 2, y + fh * i)], 0.7, 0.5)], 0.08, blur=0.5)
    # small industrial windows, 5 per floor
    lit_b, lit_d, dark = [], [], []
    for i in range(floors):
        for j in range(3):
            if r.random() < 0.34:
                continue
            xx = x + 14 + j * (w - 28) / 3
            yy = y + fh * (i + 0.55)
            seg = ([(xx, yy), (xx + r.uniform(5.5, 8), yy)], r.uniform(1.6, 2.2), 1.4)
            q = r.random()
            if q < 0.38:
                lit_b.append(seg)
            elif q < 0.55:
                lit_d.append(seg)
            else:
                dark.append(seg)
    brush(lit_b, 0.85, erase=True, blur=0.35)
    brush(lit_d, 0.48, erase=True, blur=0.45)
    brush(dark, 0.30, blur=0.4)
    # a few larger lit rooms (kept horizontal and soft)
    for _ in range(5):
        xx = x + r.uniform(0.08, 0.78) * w
        yy = y + r.uniform(0.1, 0.85) * h
        brush([([(xx, yy), (xx + r.uniform(7, 11), yy)], 5.0, 4.0)], 0.38, erase=True, blur=0.9)
    # roof cap and parapet
    comp(A(rect_mask(x - 4, y - 14, w + 8, 14)), 0.82, blur=0.4)
    brush([([(x - 4, y - 14), (x + w + 4, y - 14)], 1.8, 1.2)], 0.7, blur=0.4)
    brush([([(x + 5, y - 14), (x + 5, y)], 1.2, 1.0)], 0.6, blur=0.3)
    brush([([(x + w - 5, y - 14), (x + w - 5, y)], 1.2, 1.0)], 0.6, blur=0.3)
    # stair bulkhead
    sb = rect_mask(x + w * 0.48, y - 34, 34, 20)
    paper(sb, blur=0.3)
    wash(sb, 0.62, texture=0.2, blur=0.4)
    brush([([(x + w * 0.48, y - 34), (x + w * 0.48 + 34, y - 34)], 1.3, 1.1)], 0.65, blur=0.3)
    # water tank
    tm = rect_mask(x + w * 0.18, y - 30, 22, 16)
    paper(tm, blur=0.3)
    wash(tm, 0.55, texture=0.2, blur=0.4)
    brush([([(x + w * 0.18, y - 30), (x + w * 0.18 + 22, y - 30)], 1.3, 1.1)], 0.65, blur=0.3)
    # antenna
    brush([([(x + w * 0.72, y - 14), (x + w * 0.72, y - 62)], 1.5, 0.7)], 0.68, blur=0.3)
    brush([([(x + w * 0.72 - 10, y - 46), (x + w * 0.72 + 10, y - 46)], 0.9, 0.8)], 0.58, blur=0.3)
    # vertical sign
    if sign:
        sm = rect_mask(x - 16, y + 60, 13, 120)
        paper(sm, blur=0.3)
        wash(sm, 0.07, texture=0.2, blur=0.4)
        brush([([(x - 16, y + 60), (x - 16, y + 180)], 1.0, 0.9)], 0.5, blur=0.3)
        brush([([(x - 3, y + 60), (x - 3, y + 180)], 1.0, 0.9)], 0.5, blur=0.3)
        for k, yy in enumerate([78, 104, 126, 154]):
            brush([([(x - 13, y + yy), (x - 6, y + yy)], 4.4 - k * 0.4, 4.0)], 0.64, blur=0.3)
    comp(A(ellipse_mask(x + w / 2, y + h + 2, w * 0.5, 6)), 0.22, blur=3)


tower(438, 560, 132, 600, 3, sign=False)
tower(594, 560, 132, 600, 4)

# podium
pm = rect_mask(420, 1080, 330, 80)
paper(pm, blur=0.5)
wash(pm, 0.46, texture=0.4, blur=0.8)
brush([([(418, 1080), (752, 1080)], 2.2, 1.4)], 0.6, blur=0.5)
for k in range(5):
    bx = 438 + k * 60
    bm = rect_mask(bx, 1120, 26, 30)
    paper(bm, blur=0.3)
    wash(bm, 0.55, texture=0.15, blur=0.3)

# right low buildings
building(740, 1020, 100, 140, 0.44, 81, "flat", True)
building(840, 1060, 80, 100, 0.46, 82, "saw")

# mist at city base
comp(np.clip(1 - np.abs(Y - 1120) / 45, 0, 1) * (0.6 + 0.5 * N), 0.45, erase=True, blur=8)
comp(np.clip(1 - np.abs(Y - 1090) / 40, 0, 1) * (0.5 + 0.5 * N), 0.22, erase=True, blur=10)

# ------------------------------------------------------------------ port
def crane(cx, apex=840, boom=160, tone=0.9, load=False):
    top = apex
    solid(bar((cx - 26, 1165), (cx - 18, top + 100), 10, 7), tone, 0.3)
    solid(bar((cx + 26, 1165), (cx + 18, top + 100), 10, 7), tone, 0.3)
    solid(bar((cx - 24, top + 100), (cx + 24, top + 100), 9, 9), tone, 0.3)
    solid(bar((cx - 22, top + 100), (cx + 2, top), 8, 4), tone, 0.3)
    solid(bar((cx + 22, top + 100), (cx + 8, top + 3), 8, 4), tone, 0.3)
    bx = cx - boom
    solid(bar((cx + 2, top + 7), (bx, top - 5), 9, 5), tone, 0.3)
    solid(bar((cx + 2, top + 22), (bx, top + 8), 3, 2), tone * 0.9, 0.3)
    for k in range(1, 7):
        t = k / 7.0
        px = (cx + 2) + (bx - cx - 2) * t
        py = (top + 7) + ((top - 5) - (top + 7)) * t
        solid(bar((px, py), (px, py + 15), 1.3, 1.3), tone * 0.85, 0.3)
    # machine house
    comp(A(rect_mask(cx + 6, top + 10, 38, 21)), tone, blur=0.3)
    # counter jib
    solid(bar((cx + 40, top + 28), (cx + 82, top + 26), 3, 2), tone, 0.3)
    comp(A(rect_mask(cx + 76, top + 18, 12, 10)), tone, blur=0.3)
    # trolley/cable
    t = 0.58
    tx = (cx + 2) + (bx - cx - 2) * t
    ty = (top + 7) + ((top - 5) - (top + 7)) * t
    comp(A(rect_mask(tx - 6, ty + 2, 12, 7)), tone, blur=0.3)
    brush([([(tx, ty + 9), (tx, ty + 96)], 1.0, 0.7)], tone, blur=0.3)
    comp(A(rect_mask(tx - 14, ty + 96, 28, 3)), tone, blur=0.3)
    if load:
        cm = rect_mask(tx - 15, ty + 101, 30, 11)
        paper(cm, blur=0.2)
        wash(cm, 0.9, texture=0.1, blur=0.3)


crane(1005, 838, 155, 0.9, load=True)
crane(1145, 828, 130, 0.92)

# quay container stacks
r = random.Random(88)
for bx, bw, rows in [(930, 70, 1), (1060, 60, 1), (1160, 50, 2)]:
    for row in range(rows):
        yy = 1162 - row * 9
        x = bx
        while x < bx + bw:
            cw = r.choice([18, 22, 26])
            cm = rect_mask(x, yy - 8, cw, 8)
            paper(cm, blur=0.2)
            wash(cm, 0.85, texture=0.1, blur=0.25)
            brush([([(x, yy - 8), (x + cw, yy - 8)], 0.6, 0.5)], 0.4, erase=True, blur=0.2)
            x += cw + 2

# ------------------------------------------------------------------ water
wmask = rect_mask(0, 1160, LW, LH - 1160)
wa = A(wmask)
comp(wa * (0.7 + 0.5 * N), 0.13, blur=1.8)
ref_grad = np.clip(1 - (Y - 1162) / 110, 0, 1) ** 0.85
comp(ref_grad * wa * (0.55 + 0.6 * N), 0.30, blur=6)
comp(np.clip(1 - (Y - 1162) / 24, 0, 1) * wa, 0.30, blur=3)

# dark reflections under the towers
r = random.Random(171)
for bx, bw in [(420, 330), (740, 200), (900, 300)]:
    for _ in range(26):
        x = bx + r.uniform(3, bw - 3)
        L = r.uniform(40, 240)
        brush([([(x, 1162), (x + r.uniform(-6, 6), 1162 + L * 0.5),
                 (x + r.uniform(-5, 5), 1162 + L)], r.uniform(2.5, 8), 1.2)],
              r.uniform(0.08, 0.22), texture=0.3, blur=2.0)
# light reflections
r = random.Random(172)
for _ in range(70):
    x = r.uniform(10, 1100)
    L = r.uniform(30, 170)
    brush([([(x, 1166), (x + r.uniform(-2, 2), 1166 + L)], r.uniform(1.4, 3.4), 2.4)],
          r.uniform(0.35, 0.65), erase=True, blur=1.5)

# moon shimmer
for k in range(7):
    xx = 280 + r.uniform(-14, 14)
    brush([([(xx, 1168), (xx + r.uniform(-3, 3), 1168 + r.uniform(150, 380))],
            r.uniform(3, 10), r.uniform(1, 4))], r.uniform(0.12, 0.26), erase=True, blur=3.5)

# container ship at the quay
shx, shy, shw = 830, 1120, 270
hull = poly_mask([(shx, shy), (shx + shw, shy), (shx + shw - 16, shy + 52), (shx + 16, shy + 52)])
paper(hull, blur=0.4)
wash(hull, 0.86, texture=0.25, blur=0.6)
brush([([(shx + 16, shy + 52), (shx + shw - 16, shy + 52)], 2.4, 1.6)], 0.6, erase=True, blur=0.4)
r = random.Random(205)
for row in range(3):
    for col in range(10):
        bx = shx + 14 + col * 24
        by = shy - 8 - row * 9
        if r.random() < 0.12:
            continue
        cm = rect_mask(bx, by, 21, 8)
        paper(cm, blur=0.2)
        wash(cm, r.uniform(0.32, 0.52), texture=0.1, blur=0.25)
        brush([([(bx, by), (bx + 21, by)], 0.6, 0.5)], 0.45, erase=True, blur=0.2)
# bridge with lit windows
bm = rect_mask(shx + shw - 80, shy - 34, 26, 34)
paper(bm, blur=0.3)
wash(bm, 0.9, texture=0.1, blur=0.3)
for k in range(3):
    brush([([(shx + shw - 76, shy - 28 + k * 9), (shx + shw - 66, shy - 28 + k * 9)], 3.0, 2.6)],
          0.7, erase=True, blur=0.3)
fm = rect_mask(shx + shw - 62, shy - 46, 9, 12)
paper(fm, blur=0.2)
wash(fm, 0.86, texture=0.1, blur=0.3)
# deck lights and reflection
for k in range(5):
    comp(A(ellipse_mask(shx + 30 + k * 58, shy - 2, 1.8, 1.8)), 0.9, erase=True, blur=0.6)
comp(A(ellipse_mask(shx + shw * 0.45, shy + 64, shw * 0.42, 18)), 0.32, blur=7)

# broad washes
for y0, y1, tone in [(1190, 1260, 0.045), (1320, 1400, 0.06), (1480, 1580, 0.075)]:
    a = np.clip(1 - np.abs(Y - (y0 + y1) / 2) / ((y1 - y0) / 2 + 1), 0, 1) * (0.6 + 0.7 * N)
    comp(a * wa, tone, blur=9)
for _ in range(8):
    yy = r.uniform(1220, 1560)
    x0 = r.uniform(-100, 300)
    L = r.uniform(500, 1100)
    brush([([(x0, yy), (x0 + L * 0.5, yy + r.uniform(-5, 5)), (x0 + L, yy + r.uniform(-3, 8))],
            r.uniform(7, 16), 2.0)], r.uniform(0.10, 0.17), blur=2.4)

# ripples
r = random.Random(152)
ripples = []
for _ in range(210):
    y = r.uniform(1170, 1590)
    depth = (y - 1170) / 420.0
    x = r.uniform(-80, 1200)
    L = r.uniform(24, 200) * (0.45 + depth * 1.2)
    ripples.append(([(x, y), (x + L * 0.5, y + r.uniform(-4, 4)), (x + L, y)],
                    r.uniform(1.0, 3.6), 0.5))
brush(ripples, 0.34, texture=0.25, blur=0.6)
for x, y, L in [(120, 1540, 240), (900, 1500, 180), (640, 1560, 200)]:
    brush([([(x, y), (x + L / 2, y + 2), (x + L, y)], 4.0, 2.4)], 0.42, blur=0.7)
for x, y, L in [(260, 1500, 260), (760, 1470, 220), (60, 1440, 180)]:
    brush([([(x, y), (x + L / 2, y + 3), (x + L, y)], 7.0, 4.0)], 0.28, blur=1.2)

# ------------------------------------------------------------------ sampan
boat = poly_mask([(290, 1442), (312, 1456), (340, 1462), (368, 1456), (390, 1442),
                  (376, 1460), (340, 1464), (302, 1460)])
paper(boat, blur=0.3)
wash(boat, 0.84, texture=0.2, blur=0.4)
brush([([(298, 1444), (336, 1455), (380, 1444)], 1.4, 1.0)], 0.5, erase=True, blur=0.4)
brush([([(354, 1441), (352, 1428), (354, 1422)], 5.0, 2.6)], 0.9, blur=0.3)
comp(A(ellipse_mask(355.5, 1418, 2.8, 2.8)), 0.9, blur=0.2)
brush([([(356, 1430), (376, 1426)], 1.4, 1.0)], 0.7, blur=0.2)
brush([([(354, 1436), (334, 1462)], 1.0, 0.8)], 0.65, blur=0.2)
# lantern
comp(A(ellipse_mask(378, 1432, 2.0, 2.0)), 1.0, erase=True, blur=0.7)
comp(A(ellipse_mask(378, 1432, 6, 6)), 1.0, erase=True, blur=3)
comp(A(ellipse_mask(340, 1474, 46, 10)), 0.18, blur=5)

# ------------------------------------------------------------------ reeds & rocks
rm = poly_mask([(-20, 1610), (-20, 1530), (40, 1516), (110, 1534), (180, 1560), (240, 1590), (246, 1610)])
paper(rm, blur=0.5)
wash(rm, 0.78, texture=0.4, blur=1.0)
brush([([(-10, 1530), (48, 1524), (120, 1546), (240, 1596)], 3.4, 1.6)], 0.6, texture=0.3, blur=0.8)
for _ in range(14):
    x = random.uniform(0, 230)
    y = random.uniform(1540, 1600)
    brush([([(x, y), (x + random.uniform(18, 50), y + random.uniform(-4, 4))], random.uniform(1.2, 2.6), 0.8)],
          0.18, erase=True, blur=0.8)

r = random.Random(193)
stems, heads = [], []
for i in range(38):
    x0 = r.uniform(-10, 220)
    y0 = 1608
    x1 = x0 + r.uniform(-30, 100)
    y1 = r.uniform(1240, 1460)
    cx1 = x0 + (x1 - x0) * 0.35 + r.uniform(-30, 30)
    cy1 = (y0 + y1) / 2
    stems.append(([(x0, y0), (cx1, cy1), (x1, y1)], r.uniform(2.2, 4.2), 0.6))
    heads.append(([(x1, y1), (x1 + r.uniform(-4, 4), y1 - r.uniform(18, 30))],
                  r.uniform(2.4, 3.6), 1.2))
brush(stems, 0.84, texture=0.2, blur=0.5)
brush(heads, 0.36, texture=0.25, blur=0.7)
for pts, w0, w1 in heads:
    hx, hy = pts[-1]
    for k in range(6):
        brush([([(hx, hy), (hx + r.uniform(-13, 13), hy - r.uniform(8, 22))], 0.8, 0.3)],
              0.30, blur=0.4)
for _ in range(40):
    x = r.uniform(0, 220)
    y = r.uniform(1350, 1560)
    brush([([(x, y), (x + r.uniform(18, 50), y - r.uniform(10, 28))], 1.4, 0.3)],
          r.uniform(0.3, 0.55), blur=0.4)

# ------------------------------------------------------------------ birds & splatter
for bx, by in [(360, 430), (392, 446), (424, 428), (456, 452), (488, 434)]:
    w = random.uniform(7, 10)
    brush([([(bx, by), (bx + w * 0.5, by - w * 0.5), (bx + w, by),
             (bx + w * 1.5, by - w * 0.5), (bx + w * 2, by)], 1.1, 1.0)],
          random.uniform(0.5, 0.7), blur=0.3)

r = random.Random(177)
for _ in range(60):
    x = r.uniform(0, 1050)
    y = r.uniform(200, 1500)
    if r.random() < 0.5 and not (850 < y < 1250):
        continue
    comp(A(ellipse_mask(x, y, r.uniform(0.5, 1.8), r.uniform(0.5, 1.8))),
         r.uniform(0.08, 0.18), blur=0.2)

# ------------------------------------------------------------------ finish
D = np.clip(D, 0, 1) ** 0.88
D *= (0.90 + 0.16 * N2)
D *= (0.96 + 0.08 * F)

# directional brush texture
def stripe(gh, gw, blur, seed):
    g = np.random.default_rng(seed).random((max(2, gh), max(2, gw))).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0


tv = stripe(int(H / (40 * S)), int(W / (3 * S)), 1.0, 41)
th = stripe(int(H / (3 * S)), int(W / (40 * S)), 1.0, 42)
tex = np.where(Y < 1160, 0.55 * tv + 0.45 * N2, th)
D *= (0.92 + 0.14 * tex)

Db = np.asarray(Image.fromarray((np.clip(D, 0, 1) * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(0.9 * S)), np.float32) / 255.0
gy, gx = np.gradient(Db)
edge = np.hypot(gx, gy)
edge = np.clip(edge * 2.8, 0, 1)
edge = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(1.2 * S)), np.float32) / 255.0
D = 1 - (1 - D) * (1 - 0.14 * edge)

img = background * (1 - D[..., None]) + INK * D[..., None]
grain = rng.normal(0, 1.5, (H, W, 1)).astype(np.float32)
img += grain
img *= (1 + 0.016 * (F[..., None] - 0.5))
img[..., 0] *= (1 + 0.010 * (N - 0.5))
img[..., 2] *= (1 - 0.008 * (N - 0.5))
yy, xx = np.mgrid[0:H, 0:W]
rad = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
img *= (1 - 0.05 * np.clip(rad - 0.55, 0, 1))[..., None]

# gentle hand-painted warp (text is applied afterwards, so it stays crisp)
dxx = (N - 0.5) * 7.5 * S + (N2 - 0.5) * 2.0 * S
dyy = (N - 0.5) * 5.0 * S + (N2 - 0.5) * 2.0 * S
out = np.empty_like(img)
Xp = np.arange(W, dtype=np.float32)[None, :]
Yp = np.arange(H, dtype=np.float32)[:, None]
for ys in range(0, H, 300):
    ye = min(H, ys + 300)
    sx = np.clip(Xp + dxx[ys:ye], 0, W - 1.001)
    sy = np.clip(Yp[ys:ye] + dyy[ys:ye], 0, H - 1.001)
    x0 = sx.astype(np.int32)
    y0 = sy.astype(np.int32)
    x1 = x0 + 1
    y1 = y0 + 1
    fx = (sx - x0)[..., None]
    fy = (sy - y0)[..., None]
    out[ys:ye] = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x1] * fx * (1 - fy) +
                  img[y1, x0] * (1 - fx) * fy + img[y1, x1] * fx * fy)
img = out
# subtle split tone: cool shadows, warm paper
lum = np.clip(img.mean(axis=2, keepdims=True) / 255.0, 0, 1)
tint = np.array([0.985, 0.995, 1.018], np.float32) * (1 - lum) + np.array([1.014, 1.0, 0.982], np.float32) * lum
img *= tint

base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")

# beacons
dr = ImageDraw.Draw(base)
for bx, by in [(1005, 836), (1145, 826), (280, 300)]:
    if bx == 280:
        continue
    dr.ellipse([bx * S - 1.4 * S, by * S - 1.4 * S, bx * S + 1.4 * S, by * S + 1.4 * S],
               fill=(176, 58, 40, 180))

# ------------------------------------------------------------------ calligraphy
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(layer)
title = "華基工業大廈"
font_title = ImageFont.truetype(r"C:\Windows\Fonts\FZSTK.TTF", int(62 * S))
for i, ch in enumerate(title):
    dr.text((1112 * S, (130 + i * 78) * S), ch, font=font_title, fill=(24, 23, 19, 225), anchor="ma")
font_ins = ImageFont.truetype(r"C:\Windows\Fonts\STKAITI.TTF", int(21 * S))
ins = "歲次丙午秋日寫於葵涌"
for i, ch in enumerate(ins):
    dr.text((1044 * S, (140 + i * 24.5) * S), ch, font=font_ins, fill=(30, 29, 24, 195), anchor="ma")

seal = Image.new("RGBA", (int(46 * S), int(46 * S)), (0, 0, 0, 0))
sd = ImageDraw.Draw(seal)
sd.rounded_rectangle([0, 0, 46 * S - 1, 46 * S - 1], radius=2 * S, fill=(168, 59, 42, 232))
sd.rectangle([3 * S, 3 * S, 43 * S, 43 * S], outline=(244, 237, 220, 170), width=max(1, int(1.1 * S)))
f_seal = ImageFont.truetype(r"C:\Windows\Fonts\STKAITI.TTF", int(17 * S))
sd.text((23 * S, 14 * S), "華", font=f_seal, fill=(244, 237, 220, 240), anchor="mm")
sd.text((23 * S, 32 * S), "基", font=f_seal, fill=(244, 237, 220, 240), anchor="mm")
seal = seal.rotate(-3, resample=Image.BICUBIC, expand=False)
layer.alpha_composite(seal, (int(1018 * S), int(410 * S)))

base.alpha_composite(layer)
out = base.convert("RGB")
out.save(PNG_PATH, quality=95)
out.resize((1200, 1600), Image.LANCZOS).save(PREVIEW_PATH)
print("saved", PNG_PATH)
