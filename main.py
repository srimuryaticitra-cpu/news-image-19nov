#!/usr/bin/env python3
"""News image for Thursday 19 November 2026.

Draws a one-page newspaper front page in pure Python 3.13 stdlib:
a fixed 1024x1024 RGB canvas, a hand-built 5x7 bitmap font, simple
vector shapes (flags, skyline, tanker, cyclone, dome), and a small
PNG encoder (zlib + CRC32). No network, no clock, no randomness:
running it twice writes byte-identical output.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

CREAM = (247, 242, 231)
WHITE = (255, 255, 255)
INK = (20, 20, 24)
NAVY = (18, 36, 61)
NAVY2 = (28, 56, 92)
RED = (179, 32, 44)
GOLD = (212, 160, 60)
TEAL = (14, 110, 110)
ORANGE = (232, 110, 40)
SKY = (120, 180, 220)
GREY = (90, 92, 96)
LIGHT = (232, 226, 214)

# 5x7 bitmap font: each glyph is 7 rows of 5 chars, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "00100", "00100"),
    ',': ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ';': ("00000", "00100", "00000", "00000", "00100", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def norm_char(ch):
    if ch in FONT:
        return ch
    if ch == '\u2013' or ch == '\u2014':
        return '-'
    if ch == '\u2019':
        return "'"
    if ch == '\u20ac':
        return 'E'
    return ' '


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(px, x, y, text, scale, color):
    """Draw upper-case bitmap text; returns width drawn."""
    cx = x
    for raw in text:
        ch = norm_char(raw.upper())
        glyph = FONT[ch]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px[cx + col * scale + dx, y + row * scale + dy] = color
        cx += 6 * scale
    return cx - x - scale


def draw_text_center(px, cx, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(px, cx - w // 2, y, text, scale, color)
    return w


def wrap_lines(text, max_chars):
    words = text.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(px, x, y, text, scale, color, max_chars, line_h):
    cy = y
    for line in wrap_lines(text, max_chars):
        draw_text(px, x, cy, line, scale, color)
        cy += line_h
    return cy


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def __setitem__(self, pos, color):
        x, y = pos
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            row = bytes(color) * w
            self.buf[base:base + w * 3] = row

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def border(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def disc(self, cx, cy, r, color):
        self.circle(cx, cy, r, color)

    def triangle(self, x1, y1, x2, y2, x3, y3, color):
        # Filled triangle by scanlines (deterministic, integer math).
        pts = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            lo, hi = min(xa, xb), max(xa, xb)
            if hi >= lo:
                self.rect(lo, y, hi - lo + 1, 1, color)


def png_bytes(canvas):
    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def flag_usa(c, x, y, w, h):
    c.rect(x, y, w, h, WHITE)
    for i in range(7):
        if i % 2 == 0:
            c.rect(x, y + i * h // 13, w, h // 13 + 1, RED)
    c.rect(x, y, w * 2 // 5, h * 7 // 13, NAVY)
    for r in range(4):
        for col in range(5):
            c.rect(x + 6 + col * 14, y + 5 + r * 9, 3, 3, WHITE)


def flag_china(c, x, y, w, h):
    c.rect(x, y, w, h, (222, 41, 16))
    c.disc(x + w // 5, y + h // 4, 10, GOLD)
    for sx, sy in ((w * 2 // 5, h // 6), (w // 2, h // 3),
                   (w // 2, h // 2), (w * 2 // 5, h * 2 // 3)):
        c.disc(x + sx, y + sy, 4, GOLD)


def flag_russia(c, x, y, w, h):
    c.rect(x, y, w, h // 3, WHITE)
    c.rect(x, y + h // 3, w, h // 3, (0, 57, 166))
    c.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)
    c.border(x, y, w, h, INK, 1)


def build():
    c = Canvas(W, H, CREAM)
    # --- Masthead -------------------------------------------------------
    c.rect(0, 0, W, 132, NAVY)
    c.rect(0, 132, W, 6, GOLD)
    draw_text_center(c, W // 2, 14, "THE WORLD TODAY", 3, GOLD)
    draw_text_center(c, W // 2, 52, "THURSDAY 19 NOVEMBER 2026", 4, WHITE)
    draw_text_center(c, W // 2, 102, "ONE DAY  -  ONE PAGE  -  THE WORLD IN BRIEF", 2, (180, 195, 215))

    # --- LEAD: Shenzhen summit ----------------------------------------
    lx, ly, lw, lh = 12, 148, 648, 288
    c.rect(lx, ly, lw, lh, WHITE)
    c.border(lx, ly, lw, lh, NAVY, 3)
    c.rect(lx, ly, lw, 34, RED)
    draw_text(c, lx + 14, ly + 8, "LEAD STORY  -  SHENZHEN, CHINA", 2, WHITE)
    draw_text(c, lx + 16, ly + 50, "TRUMP, XI & PUTIN", 5, NAVY)
    draw_text(c, lx + 16, ly + 92, "MEET IN SHENZHEN", 5, NAVY)
    draw_para(c, lx + 16, ly + 142,
              "First trilateral summit, on the sidelines of APEC. "
              "The war in Iran tops the agenda.", 2, INK, 44, 22)
    # Three flags side by side, labelled.
    fy = ly + 208
    for fx, flag, label in ((lx + 16, flag_usa, "USA"),
                            (lx + 236, flag_china, "CHINA"),
                            (lx + 456, flag_russia, "RUSSIA")):
        flag(c, fx, fy, 176, 52)
        c.border(fx, fy, 176, 52, INK, 1)
        draw_text_center(c, fx + 88, fy + 58, label, 2, GREY)

    # --- GTA VI panel ----------------------------------------------------
    gx, gy, gw, gh = 672, 148, 340, 288
    c.rect(gx, gy, gw, gh, (24, 16, 48))
    for i, col in enumerate(((255, 120, 60), (255, 80, 120),
                             (150, 60, 180), (60, 40, 120))):
        c.rect(gx, gy + 40 + i * 34, gw, 34, col)
    c.disc(gx + gw // 2, gy + 118, 46, (255, 220, 120))
    c.rect(gx, gy + 118, gw, 6, (255, 220, 120))
    # Palm silhouettes.
    for px0 in (gx + 36, gx + gw - 36):
        c.rect(px0 - 3, gy + 150, 6, 70, INK)
        c.triangle(px0 - 34, gy + 158, px0 + 34, gy + 158, px0, gy + 176, INK)
        c.triangle(px0 - 28, gy + 148, px0 + 28, gy + 148, px0, gy + 164, INK)
    c.rect(gx, gy + 218, gw, 70, (16, 10, 36))
    draw_text_center(c, gx + gw // 2, gy + 14, "GAMES", 2, (255, 220, 120))
    draw_text_center(c, gx + gw // 2, gy + 228, "GTA VI IS HERE", 3, WHITE)
    draw_text_center(c, gx + gw // 2, gy + 258,
                     "GAMERS ENTER VICE CITY", 2, (255, 200, 140))
    # small line under sun handled above; add years line
    draw_text(c, gx + 14, gy + 196, "AFTER 13 YEARS", 2, WHITE)

    # --- GULF panel ------------------------------------------------------
    ux, uy, uw, uh = 12, 448, 1000, 196
    c.rect(ux, uy, uw, uh, WHITE)
    c.border(ux, uy, uw, uh, NAVY, 3)
    c.rect(ux, uy, uw, 34, NAVY)
    draw_text(c, ux + 14, uy + 8, "WAR  -  THE GULF", 2, WHITE)
    # Sea + tanker drawing on the left.
    c.rect(ux + 14, uy + 48, 300, 132, (16, 90, 130))
    c.rect(ux + 14, uy + 48, 300, 10, (90, 170, 200))
    c.rect(ux + 60, uy + 110, 210, 34, (40, 40, 44))
    c.rect(ux + 90, uy + 88, 40, 24, (200, 60, 40))
    c.rect(ux + 150, uy + 96, 90, 16, (220, 220, 220))
    draw_text(c, ux + 24, uy + 156, "STRAIT OF HORMUZ", 2, WHITE)
    draw_text(c, ux + 340, uy + 52, "GULF ON EDGE", 4, RED)
    draw_para(c, ux + 340, uy + 100,
              "Iran widens strikes to Kuwait, hitting Ali Al Salem base. "
              "A tanker is hit in Hormuz: 11 crew hurt, 1 missing. "
              "Oil flow halves to 8.5m barrels a day.", 2, INK, 42, 22)

    # --- Bottom row: four panels ----------------------------------------
    panels = [
        ("USA", "JEFFRIES", "HISTORY", NAVY,
         "First Black Speaker. Peltola wins Alaska. Senate 56-44."),
        ("INDIA", "CYCLONE", "AKVAN", TEAL,
         "May hit land between Machilipatnam and Puri."),
        ("EUROPE", "EU LOAN", "EUR 45BN", (30, 80, 160),
         "EU proposes EUR 45bn loan for Ukraine."),
        ("SPACE", "VOYAGER 1", "LIGHT-DAY", (90, 50, 140),
         "Voyager 1 reaches light-day milestone."),
    ]
    pw, ph, py = 244, 252, 656
    for i, (kicker, h1, h2, col, body) in enumerate(panels):
        x = 12 + i * (pw + 8)
        c.rect(x, py, pw, ph, WHITE)
        c.border(x, py, pw, ph, NAVY, 2)
        c.rect(x, py, pw, 30, col)
        draw_text(c, x + 10, py + 7, kicker, 2, WHITE)
        draw_text(c, x + 10, py + 44, h1, 3, NAVY)
        draw_text(c, x + 10, py + 70, h2, 3, NAVY)
        if i == 0:
            # Capitol dome.
            c.rect(x + 82, py + 142, 80, 6, NAVY)
            c.rect(x + 88, py + 118, 68, 26, NAVY)
            c.disc(x + 122, py + 118, 24, NAVY)
            c.rect(x + 120, py + 90, 4, 8, NAVY)
        elif i == 1:
            # Cyclone spiral: concentric rings.
            for r, cc in ((30, TEAL), (21, (40, 150, 150)), (12, (120, 200, 200))):
                c.circle(x + 122, py + 132, r, cc)
            c.disc(x + 122, py + 132, 6, TEAL)
        elif i == 2:
            # EU stars ring with 45 in the middle.
            for k in range(8):
                ang = k * math.pi / 4
                sx = int(x + 122 + 30 * math.cos(ang))
                sy = int(py + 132 + 30 * math.sin(ang))
                c.disc(sx, sy, 4, GOLD)
            draw_text_center(c, x + 122, py + 124, "45", 3, NAVY)
        else:
            # Star + orbit.
            c.disc(x + 122, py + 132, 10, GOLD)
            c.circle(x + 122, py + 132, 32, GREY)
            c.disc(x + 156, py + 118, 5, RED)
        draw_para(c, x + 10, py + 178, body, 2, INK, 19, 18)

    # --- Footer: Nvidia ---------------------------------------------------
    c.rect(0, 920, W, 104, NAVY)
    c.rect(0, 920, W, 4, GOLD)
    draw_text_center(c, W // 2, 936, "TECH  -  NVIDIA", 2, GOLD)
    draw_text_center(c, W // 2, 962,
                     "HUANG STEPS DOWN  -  KRESS ACTING CEO", 3, WHITE)
    draw_text_center(c, W // 2, 994,
                     "NVIDIA HALTS H-SERIES CHIP SHIPMENTS TO CHINA", 2,
                     (180, 195, 215))
    return c


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
