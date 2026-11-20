# The Day's World -- Friday 20 November 2026
# Front-page newspaper image, drawn entirely with the Python standard
# library (no fonts, no image libraries: a hand-written 5x7 bitmap font
# and a small PNG encoder built on zlib). Deterministic: two runs write
# byte-identical files. Writes only to $MAKEFUN_OUTPUT_DIR/entry.png.
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font --
# 5x7 bitmap glyphs, rows top to bottom, '1' = ink. Uppercase, digits and
# the punctuation the page uses. All page text is upper-cased first.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
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
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}


def clean(text):
    """Normalise copy to the glyph set: upper-case, ASCII punctuation."""
    repl = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a3": "GBP ",
            "\u00e9": "E", "\u00fc": "U", "\u00b7": "|", "\u2022": "|"}
    out = []
    for ch in text:
        ch = repl.get(ch, ch)
        out.append(ch)
    s = "".join(out).upper()
    return "".join(ch if ch in FONT else " " for ch in s)


def text_w(text, scale):
    return len(clean(text)) * 6 * scale - scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns lines that all fit max_w. Never overflows."""
    words = clean(text).split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is hard-clipped, never spilled.
            while text_w(word, scale) > max_w and len(word) > 1:
                word = word[:-1]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas --
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o:o + 3] = bytes(col)

    def rect(self, x, y, w, h, col):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def hline(self, x, y, w, col, t=1):
        self.rect(x, y, w, t, col)

    def vline(self, x, y, h, col, t=1):
        self.rect(x, y, t, h, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, col, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, col)
                elif abs(d - r * r) <= r:
                    self.set(xx, yy, col)

    def triangle(self, pts, col):
        (x0, y0), (x1, y1), (x2, y2) = pts
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if den == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, col)

    def text(self, x, y, s, scale, col):
        s = clean(s)
        cx = x
        for ch in s:
            glyph = FONT[ch]
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, col)
            cx += 6 * scale
        return cx

    def text_centre(self, cx, y, s, scale, col):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, col)

    def text_right(self, x, y, s, scale, col):
        self.text(x - text_w(s, scale), y, s, scale, col)


# ----------------------------------------------------------------- png --
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)

# -------------------------------------------------------------- palette --
INK = (24, 24, 28)
PAPER = (250, 247, 238)
PAPER2 = (244, 238, 226)
NAVY = (18, 38, 66)
NAVY2 = (28, 58, 96)
RED = (178, 34, 34)
RED2 = (214, 69, 55)
GOLD = (198, 148, 44)
TEAL = (14, 110, 110)
GREEN = (34, 120, 64)
GREY = (96, 96, 100)
LGREY = (214, 210, 198)
WHITE = (255, 255, 255)
SKY = (126, 164, 196)
SKY2 = (88, 124, 160)
RIVER = (64, 98, 132)
SMOKE = (120, 120, 124)

CATCOL = {
    "EUROPE": NAVY2, "ASIA": TEAL, "CLIMATE": GREEN, "AMERICAS": RED,
    "MIDEAST": (146, 74, 28), "AFRICA": (122, 90, 20), "MARKETS": (96, 44, 110),
    "TECH": (30, 90, 140), "WORLD": NAVY, "CULTURE": (150, 40, 90),
}

# --------------------------------------------------------------- stories --
# Every figure below was verified against wire reporting of 20 Nov 2026
# (Reuters / AP / CNN / UN News / IMD / Sensor Tower / ICJ / Morningstar).
# Dates in brackets mark stories first reported on 19 Nov, carried by the
# 20 Nov wires; nothing here is invented.
HERO = {
    "cat": "KYIV UNDER FIRE",
    "head": "RUSSIA HITS THREE KYIV BRIDGES IN BIGGEST BARRAGE OF THE WAR",
    "deck": ("Overnight ballistic missiles struck the Podilskyi, Darnytskyi "
             "and Pivdennyi bridges across the Dnipro, hours after Putin "
             "vowed revenge for strikes on the Crimea bridge."),
    "facts": "110+ MISSILES FIRED  |  8 KILLED, 28 HURT  |  3 BRIDGES HIT",
    "source": "REUTERS - MAYOR KLITSCHKO",
}

LEADS = [
    {"cat": "CLIMATE", "icon": "leaf",
     "head": "COP31 ENDS IN DEADLOCK",
     "deck": ("Final day in Antalya: no deal as the draft drops all mention "
              "of fossil fuels. 21 issues open; talks set to run overtime."),
     "source": "AP - UN NEWS"},
    {"cat": "ASIA", "icon": "storm",
     "head": "CYCLONE AKVAN MAKES LANDFALL",
     "deck": ("Storm crosses India's east coast near Gopalpur at 70-80 kph, "
              "gusting to 90. Third cyclone in under a month; no deaths yet."),
     "source": "IMD - REUTERS"},
    {"cat": "EUROPE", "icon": "flag",
     "head": "UK AND EU AGREE RESET DEAL",
     "deck": ("Food checks to end, youth mobility capped at 100,000 a year, "
              "emissions trading linked. Food deal 'worth GBP 5.1bn a year'."),
     "source": "REUTERS"},
    {"cat": "WORLD", "icon": "summit",
     "head": "TRUMP, XI AND PUTIN MEET",
     "deck": ("First three-way summit in Shenzhen issues a peace declaration "
              "that omits Ukraine and Iran. Trump: Iran call can wait to 2027."),
     "source": "SCMP - AXIOS"},
    {"cat": "MARKETS", "icon": "chart",
     "head": "AI SELL-OFF DEEPENS",
     "deck": ("Asia heads for its worst week since 2020. Nikkei down 4.5%, "
              "Taiwan down 17% on the week; MSCI world falls a 7th day."),
     "source": "REUTERS"},
    {"cat": "CULTURE", "icon": "game",
     "head": "GTA VI: $2.36BN IN A DAY",
     "deck": ("Sensor Tower estimates 24.6m copies sold on launch day, 19 Nov, "
              "the biggest entertainment launch ever. Take-Two yet to confirm."),
     "source": "SENSOR TOWER"},
    {"cat": "WORLD", "icon": "gavel",
     "head": "ICJ: MYANMAR GUILTY OF GENOCIDE",
     "deck": ("World court rules 9-6 that Myanmar committed genocide against "
              "the Rohingya in 2017; orders reparations. A first for a state."),
     "source": "ICJ - 19 NOV RULING"},
    {"cat": "TECH", "icon": "ipo",
     "head": "ANTHROPIC IPO: $81BN, SHARES +17%",
     "deck": ("Largest IPO on record debuts on Nasdaq, valued past $2tn, but "
              "fails to stop the AI rout. Nvidia's earnings also fall flat."),
     "source": "REUTERS"},
    {"cat": "MIDEAST", "icon": "missile",
     "head": "HOUTHI MISSILE HITS RIYADH TOWER",
     "deck": ("Strike damages the PIF Tower, the kingdom's tallest building "
              "and home of its $900bn sovereign fund. No casualties reported."),
     "source": "REUTERS"},
]

# One-line briefs: headline (<=44 chars) + region tag. All verified.
BRIEFS = [
    ("MIDEAST", "ISRAELI TROOPS CROSS GAZA LINE"),
    ("AFRICA", "DRONE STRIKE KILLS 10 AT SUDAN MINE"),
    ("AFRICA", "SENEGAL BOAT CAPSIZES, DOZENS LOST"),
    ("AMERICAS", "BUKELE FILES FOR A THIRD TERM"),
    ("AMERICAS", "US AND VENEZUELA SIGN MILITARY DEAL"),
    ("EUROPE", "BERLIN BACKS UKRAINE, UK DRONES"),
    ("EUROPE", "KERCH BRIDGE HIT A THIRD TIME"),
    ("EUROPE", "EU TO SUMMON RUSSIAN ENVOY"),
    ("EUROPE", "POLAND PROBES OBJECTS NEAR BORDER"),
    ("EUROPE", "FRANCE: 4TH WEEKEND OF COST PROTESTS"),
    ("MIDEAST", "HERZOG TAPS EISENKOT FOR GOVERNMENT"),
    ("MIDEAST", "4 NATIONS URGE AID ACCESS TO GAZA"),
    ("AMERICAS", "US DETAILS $12BN VENEZUELAN OIL"),
    ("ASIA", "S. KOREA COURT FREES EX-PM HAN"),
    ("AMERICAS", "ARGENTINA BACKS DISABILITY LAW 71-0"),
    ("AMERICAS", "TRUMP PARDONS PETE ROSE"),
    ("AMERICAS", "SENATE REJECTS IRAN WAR POWERS"),
    ("AFRICA", "ETHIOPIA-ERITREA STRIKES AT BADME"),
    ("MARKETS", "GOLD, SILVER SLIDE TO 1-YEAR LOWS"),
    ("MARKETS", "NVIDIA SHEDS $2TN IN 6 WEEKS"),
    ("TECH", "SOFTBANK PLUNGES 14.6% IN TOKYO ROUT"),
    ("MIDEAST", "IRAN WAR, 9TH MONTH; HORMUZ ATTACKS"),
    ("AMERICAS", "HAITI RAID KILLS 34 GANG SUSPECTS"),
    ("EUROPE", "VILLEPIN TO SEEK FRENCH PRESIDENCY"),
]


# ----------------------------------------------------------------- icons --
def draw_icon(cv, kind, x, y, s, col):
    """Small flat pictograms, drawn from shapes, inside a colour chip."""
    if kind == "leaf":  # COP31: white leaf disc, green veins
        cv.circle(x + s // 2, y + s // 2, s // 2 - 2, WHITE)
        cv.line(x + 5, y + s - 6, x + s - 5, y + 6, col, 2)
        cv.line(x + s // 2, y + s // 2, x + s - 7, y + s // 2 + 3, col, 2)
        cv.line(x + s // 2 + 2, y + s // 2 - 2, x + s // 2 + 2, y + 8, col, 2)
    elif kind == "storm":  # cyclone: outline rings + rain
        for r in (s // 2 - 2, s // 3, s // 6):
            cv.circle(x + s // 2, y + s // 2 - 2, r, WHITE, fill=False)
        cv.line(x + 3, y + s - 6, x + 1, y + s - 1, WHITE, 2)
        cv.line(x + s // 2, y + s - 6, x + s // 2 - 2, y + s - 1, WHITE, 2)
        cv.line(x + s - 4, y + s - 6, x + s - 6, y + s - 1, WHITE, 2)
    elif kind == "flag":
        cv.vline(x + 6, y + 3, s - 6, WHITE, 3)
        cv.rect(x + 9, y + 4, s - 13, s // 2 - 2, WHITE)
        cv.rect(x + 9, y + 4, (s - 13) // 2, s // 2 - 2, RED2)
    elif kind == "summit":  # three leaders, one table
        for cx in (x + 7, x + s // 2, x + s - 8):
            cv.circle(cx, y + 9, 5, WHITE)
            cv.rect(cx - 6, y + 16, 12, s - 20, WHITE)
        cv.hline(x + 3, y + s - 6, s - 6, WHITE, 3)
    elif kind == "chart":  # falling market line
        cv.vline(x + 4, y + 4, s - 8, WHITE, 2)
        cv.hline(x + 4, y + s - 5, s - 8, WHITE, 2)
        cv.line(x + 7, y + 8, x + s // 2, y + s // 2, RED2, 3)
        cv.line(x + s // 2, y + s // 2, x + s - 6, y + s - 8, RED2, 3)
        cv.triangle([(x + s - 9, y + s - 11), (x + s - 3, y + s - 11),
                     (x + s - 6, y + s - 4)], RED2)
    elif kind == "game":  # controller
        cv.rect(x + 3, y + s // 3, s - 6, s // 2, WHITE)
        cv.circle(x + 9, y + s // 2 + 2, 3, col)
        cv.circle(x + s - 10, y + s // 2 - 1, 2, col)
        cv.circle(x + s - 10, y + s // 2 + 4, 2, col)
    elif kind == "gavel":
        cv.line(x + 6, y + s - 5, x + s - 8, y + 8, WHITE, 3)
        cv.rect(x + s - 14, y + 3, 11, 7, WHITE)
        cv.rect(x + 4, y + s - 8, 12, 4, WHITE)
    elif kind == "ipo":  # rising arrow
        cv.vline(x + 4, y + 4, s - 8, WHITE, 2)
        cv.hline(x + 4, y + s - 5, s - 8, WHITE, 2)
        cv.line(x + 7, y + s - 9, x + s // 2, y + 10, WHITE, 3)
        cv.line(x + s // 2, y + 10, x + s - 6, y + 14, WHITE, 3)
        cv.triangle([(x + s - 10, y + 6), (x + s - 3, y + 13),
                     (x + s - 10, y + 15)], WHITE)
    elif kind == "missile":
        cv.triangle([(x + s - 4, y + 5), (x + 6, y + s // 2),
                     (x + s - 4, y + s - 6)], WHITE)
        cv.line(x + 4, y + s // 2, x + s - 12, y + s // 2, WHITE, 2)
        cv.circle(x + s // 2, y + s // 2, 3, col)

# --------------------------------------------------------------- layout --
OVERFLOWS = []


def check(cond, msg):
    if not cond:
        OVERFLOWS.append(msg)


def masthead(cv):
    cv.rect(0, 0, W, 76, NAVY)
    cv.rect(0, 76, W, 4, GOLD)
    cv.text(20, 12, "THE DAY'S WORLD", 5, WHITE)
    cv.text_right(W - 20, 14, "FRIDAY 20 NOVEMBER 2026", 2, GOLD)
    cv.text_right(W - 20, 40, "34 STORIES | 7 REGIONS | ONE DAY", 1, WHITE)
    cv.text(20, 56, "ONE DAY. EVERY STORY THAT MATTERED.", 1, (176, 196, 220))


def hero_art(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y, w, 34, NAVY2)
    cv.circle(x + w - 34, y + 62, 15, GOLD)
    cv.circle(x + w - 34, y + 62, 9, (226, 178, 80))
    # skyline silhouettes
    for bx, bh in ((0, 46), (34, 62), (78, 40), (112, 70), (160, 52),
                   (206, 66), (248, 44), (292, 58), (330, 38)):
        cv.rect(x + bx, y + 112 - bh + 22, 30, bh + 40, NAVY)
    # river
    cv.rect(x, y + 134, w, h - 134, RIVER)
    cv.hline(x + 12, y + 148, 90, (120, 158, 182), 2)
    cv.hline(x + 200, y + 160, 120, (120, 158, 182), 2)
    # bridge: towers, deck, cables
    for tx in (x + 96, x + 246):
        cv.rect(tx, y + 62, 9, 76, INK)
    cv.hline(x + 8, y + 132, w - 16, INK, 5)
    for cx in (x + 20, x + 60, x + 140, x + 180, x + 210, x + 300, x + 330):
        cv.line(x + 100, y + 62, cx, y + 132, INK, 1)
        cv.line(x + 250, y + 62, cx, y + 132, INK, 1)
    # explosions on the deck
    for ex, ey in ((x + 150, y + 118), (x + 300, y + 122)):
        cv.circle(ex, ey, 16, RED2)
        cv.circle(ex, ey, 10, GOLD)
        cv.circle(ex, ey, 4, WHITE)
        for dx, dy in ((-20, -8), (20, -10), (-14, 12), (18, 10), (0, -22)):
            cv.line(ex, ey, ex + dx, ey + dy, GOLD, 2)
    # smoke
    for sx, sy, sr in ((x + 150, y + 92, 12), (x + 168, y + 82, 9),
                       (x + 300, y + 96, 11), (x + 316, y + 86, 8)):
        cv.circle(sx, sy, sr, SMOKE)
    cv.rect(x, y + h - 20, w, 20, INK)
    cv.text(x + 10, y + h - 14, "KYIV - THE DNIPRO AT DAWN", 1, WHITE)


def hero(cv):
    y = 84
    hero_art(cv, 20, y, 360, 180)
    tx = 396
    tw = W - 20 - tx
    # category tag
    tag = HERO["cat"]
    cv.rect(tx, y + 6, text_w(tag, 2) + 16, 24, RED)
    cv.text(tx + 8, y + 11, tag, 2, WHITE)
    lines = wrap(HERO["head"], tw, 3)
    check(len(lines) <= 2, "hero head lines=%d" % len(lines))
    yy = y + 40
    for ln in lines[:2]:
        cv.text(tx, yy, ln, 3, INK)
        yy += 25
    deck = wrap(HERO["deck"], tw, 2)
    check(len(deck) <= 4, "hero deck lines=%d" % len(deck))
    yy = y + 96
    for ln in deck[:4]:
        cv.text(tx, yy, ln, 2, (52, 52, 58))
        yy += 17
    facts = "110+ MISSILES | 8 KILLED, 28 HURT | 3 BRIDGES HIT"
    check(text_w(facts, 2) <= tw, "hero facts too wide")
    cv.text(tx, y + 170, facts, 2, RED)
    cv.text(tx, y + 190, "SOURCE: " + HERO["source"], 1, GREY)


def section_head(cv, y, label):
    cv.text(20, y, label, 2, NAVY)
    cv.hline(20 + text_w(label, 2) + 12, y + 8, W - 40 - text_w(label, 2) - 12,
             LGREY, 2)
    return y + 24


def lead_card(cv, x, y, w, h, item):
    col = CATCOL[item["cat"]]
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 4, col)
    cv.rect(x, y + 4, w, 1, LGREY)
    cv.rect(x, y + h - 1, w, 1, LGREY)
    cv.rect(x, y, 1, h, LGREY)
    cv.rect(x + w - 1, y, 1, h, LGREY)
    cv.rect(x + 10, y + 12, 36, 36, col)
    draw_icon(cv, item["icon"], x + 10, y + 12, 36, col)
    cv.text(x + 54, y + 16, item["cat"], 2, col)
    cv.text(x + 54, y + 34, "20 NOV 2026", 1, GREY)
    head = wrap(item["head"], w - 20, 2)
    check(len(head) <= 2, "lead head overflow: %s" % item["head"])
    yy = y + 56
    for ln in head[:2]:
        cv.text(x + 10, yy, ln, 2, INK)
        yy += 17
    deck = wrap(item["deck"], w - 20, 1)
    check(len(deck) <= 3, "lead deck overflow: %s (%d lines)"
          % (item["head"], len(deck)))
    yy = y + 94
    for ln in deck[:3]:
        cv.text(x + 10, yy, ln, 1, (62, 62, 68))
        yy += 10
    cv.text(x + 10, y + h - 14, "SOURCE: " + item["source"], 1, GREY)


def leads(cv):
    y = section_head(cv, 272, "THE DAY'S LEADS")
    cw = 320
    gap = 12
    for i, item in enumerate(LEADS):
        row, col = divmod(i, 3)
        x = 20 + col * (cw + gap)
        yy = y + row * (140 + 8)
        lead_card(cv, x, yy, cw, 140, item)
    return y + 3 * 140 + 2 * 8


def briefs(cv, y):
    y = section_head(cv, y + 8, "MORE OF THE DAY - IN BRIEF")
    colw = 484
    for i, (cat, head) in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        x = 20 + col * (colw + 16)
        yy = y + row * 19
        ccol = CATCOL[cat]
        chip_w = len(cat) * 6 + 10
        cv.rect(x, yy, chip_w, 13, ccol)
        cv.text(x + 5, yy + 3, cat, 1, WHITE)
        avail = colw - chip_w - 8
        check(text_w(head, 2) <= avail,
              "brief too wide: %s (%d > %d)" % (head, text_w(head, 2), avail))
        cv.text(x + chip_w + 8, yy, head, 2, INK)
    return y + 12 * 19


def footer(cv):
    cv.hline(20, 1004, W - 40, LGREY, 1)
    cv.text(20, 1009,
            "DATE CHECK - 20 NOV 2026: EVERY STORY ABOVE HAPPENED OR WAS "
            "FIRST REPORTED THAT DAY. SOURCES: REUTERS, AP, CNN, UN NEWS, "
            "IMD, SENSOR TOWER, ICJ, MORNINGSTAR.", 1, GREY)


def main():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    hero(cv)
    y = leads(cv)
    briefs(cv, y)
    footer(cv)
    if OVERFLOWS:
        for msg in OVERFLOWS:
            print("OVERFLOW: " + msg)
        raise SystemExit(1)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    write_png(cv, path)
    print("wrote " + path)


if __name__ == "__main__":
    main()
