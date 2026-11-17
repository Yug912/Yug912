"""Generate departure-board themed SVGs for Yug912's GitHub profile.

Edit the DATA section and re-run:  python3 gen.py
"""
import os, random, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- DATA
NAME = "YUG THAKRAL"
TAGLINE = "COMPETITIVE PROGRAMMER · BUILDER"
TICKER = ("1990 PROBLEMS SOLVED   ★   LEETCODE KNIGHT · 1931   ★   500-DAY LEETCODE STREAK   ★   "
          "CODECLASH 25.2 WINNER   ★   FLIPKART GRID 8.0 SEMIFINALIST   ★   3★ CODECHEF   ★   "
          "NOW BOARDING: LEETHINT — AI HINT LADDER FOR LEETCODE   ★   ")

# flight, destination, description, via, gate, status, status_kind (live|work|done)
DEPARTURES = [
    ("YT 101", "LEETHINT",      "AI hint ladder for LeetCode",      "JS · GEMINI · CLOUDFLARE", "EXT", "LIVE",       "live"),
    ("YT 102", "PREBUY IQ",     "Travel inventory optimizer",       "PYTHON · ML",              "AI",  "REBUILDING", "work"),
    ("YT 103", "COOKQUEST",     "Recipe explorer with live search", "JAVASCRIPT · REST API",    "WEB", "ARRIVED",    "done"),
]

# event, organiser, project/team, status, kind
ARRIVALS = [
    ("CODECLASH 25.2",    "RPH · JIIT NOIDA",   "SOLO · 500+ CODERS",    "WINNER",        "win"),
    ("EXECUTE 26.3",      "KNUTH PROG. HUB",    "TEAM OF 3",             "1ST RUNNER-UP", "place"),
    ("EXECUTE 26.1",      "KNUTH PROG. HUB",    "TEAM · 100+ TEAMS",     "2ND RUNNER-UP", "place"),
    ("FLIPKART GRID 8.0", "FLIPKART",           "NATIONAL",              "SEMIFINALIST",  "place"),
    ("LEETCODE STREAK",   "LEETCODE",           "SHOWING UP DAILY",      "500 DAYS",      "win"),
    ("VOYAGEHACK 4.0",    "TBO.COM",            "PREBUY IQ · TEAM OF 2", "EN ROUTE",      "work"),
]

# label, value  ("" = not filled in yet -> shows dashes)
SCOREBOARD = [  # label, value, sub-label
    ("PROBLEMS SOLVED", "1990", "620 ACTIVE DAYS"),
    ("LEETCODE",        "1931", "KNIGHT · MAX 1944"),
    ("CODEFORCES",      "1355", "PUPIL · MAX 1424"),
    ("CODECHEF",        "1648", "3★ · MAX 1662"),
    ("CONTESTS",        "121",  "LC 41 · CF 62 · CC 18"),
]
SCORE_FOOT = "1186 LEETCODE · 591 CODEFORCES · 139 CODECHEF · 74 GFG   │   EASY 371 · MEDIUM 772 · HARD 116"

GATES = [("A1", "C++"), ("A2", "PYTHON"), ("A3", "JAVASCRIPT"), ("A4", "TYPESCRIPT"),
         ("B1", "DJANGO"), ("B2", "HTML / CSS"), ("B3", "GEMINI API"), ("B4", "CLOUDFLARE")]

# ---------------------------------------------------------------- STYLE
BG, PANEL, TILE = "#0d1117", "#161b22", "#21262d"
ACCENT, WHITE, GREY, LINE = "#58A6FF", "#E6EDF3", "#8B949E", "#30363d"
GREEN, ROW = "#3FB950", "#11161d"
VIOLET, PINK, CYAN, ORANGE, GOLD = "#A371F7", "#F778BA", "#39C5CF", "#F0883E", "#E3B341"
PALETTE = [ACCENT, VIOLET, PINK, CYAN, GREEN, ORANGE]   # cycled across rows, gates and scores
# per-platform colours on the scoreboard (brand-ish)
SCORE_COLORS = [WHITE, "#FFA116", "#58A6FF", "#D0A26B", VIOLET]
TICKER_FROM, TICKER_TO = "#58A6FF", "#A371F7"   # the one bright band: the moving ticker
FONT = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Courier New',monospace"
GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@%&"
random.seed(912)
e = html.escape


def svg(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}" font-weight="700">\n<style>\n'
            "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.15}}\n"
            ".blink{animation:blink 1.2s steps(1) infinite}\n"
            f"{css}</style>\n{body}\n</svg>\n")


def flap_tiles(text, x0, y0, tw, th, gap, fs, period, start, step, color=WHITE, scr=4, scr_dt=0.07, uid="t"):
    """Split-flap tiles that scramble then settle, looping every `period` seconds."""
    css, out = [], []
    for i, ch in enumerate(text):
        x = x0 + i * (tw + gap)
        if ch == " ":
            continue
        out.append(f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="4" fill="{TILE}"/>')
        out.append(f'<rect x="{x}" y="{y0}" width="{tw}" height="{th/2:.1f}" rx="4" fill="#ffffff" opacity=".035"/>')
        cx, cy = x + tw / 2, y0 + th / 2 + fs * 0.36
        s = start + i * step
        def pct(t): return max(0.0, min(100.0, t / period * 100))
        a, b = pct(s), pct(s + scr * scr_dt)
        # final glyph: hidden during its scramble window
        name = f"{uid}f{i}"
        css.append(f"@keyframes {name}{{0%,{max(a-0.01,0):.2f}%{{opacity:1}}{a:.2f}%,{b:.2f}%{{opacity:0}}"
                   f"{min(b+0.01,100):.2f}%,100%{{opacity:1}}}}.{name}{{animation:{name} {period}s linear infinite}}")
        out.append(f'<text class="{name}" x="{cx}" y="{cy:.1f}" font-size="{fs}" fill="{color}" text-anchor="middle">{e(ch)}</text>')
        for j in range(scr):
            g = random.choice(GLYPHS)
            sa, sb = pct(s + j * scr_dt), pct(s + (j + 1) * scr_dt)
            n = f"{uid}s{i}_{j}"
            css.append(f"@keyframes {n}{{0%,{max(sa-0.01,0):.2f}%{{opacity:0}}{sa:.2f}%,{sb:.2f}%{{opacity:1}}"
                       f"{min(sb+0.01,100):.2f}%,100%{{opacity:0}}}}.{n}{{opacity:0;animation:{n} {period}s linear infinite}}")
            out.append(f'<text class="{n}" x="{cx}" y="{cy:.1f}" font-size="{fs}" fill="{color}" text-anchor="middle">{e(g)}</text>')
    return "\n".join(out), "\n".join(css)


def ticker(text, y, w, fs, color, uid, speed=55, x_pad=0, h=None):
    cw = fs * 0.6
    tw = len(text) * cw
    dur = tw / speed
    css = (f"@keyframes {uid}{{from{{transform:translateX(0)}}to{{transform:translateX(-{tw:.1f}px)}}}}"
           f".{uid}{{animation:{uid} {dur:.1f}s linear infinite}}")
    reps = int(w // tw) + 2
    t = "".join(f'<text x="{x_pad + k*tw:.1f}" y="{y}" font-size="{fs}" fill="{color}" textLength="{tw:.1f}" '
                f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{e(text)}</text>' for k in range(reps))
    return f'<g class="{uid}">{t}</g>', css


def board_header(w, title, right, y=0):
    return (f'<linearGradient id="hg" gradientUnits="userSpaceOnUse" x1="56" x2="{56 + len(title) * 22}">'
            f'<stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
            f'<rect x="0" y="{y}" width="{w}" height="64" fill="{PANEL}"/>'
            f'<circle cx="36" cy="{y+32}" r="6" fill="{GREEN}" class="blink"/>'
            f'<text x="56" y="{y+41}" font-size="22" fill="url(#hg)" letter-spacing="6">{e(title)}</text>'
            f'<text x="{w-32}" y="{y+40}" font-size="15" fill="{GREY}" text-anchor="end" letter-spacing="3">{e(right)}</text>')


def status_cell(x, y, label, kind):
    col = {"live": GREEN, "work": ACCENT, "done": GREY, "win": GOLD, "place": VIOLET}[kind]
    cls = ' class="blink"' if kind in ("live", "work") else ""
    return (f'<circle cx="{x}" cy="{y-6}" r="6" fill="{col}"{cls}/>'
            f'<text x="{x+16}" y="{y}" font-size="{17 if len(label) < 12 else 15}" fill="{col}" letter-spacing="2">{e(label)}</text>')


# ---------------------------------------------------------------- HEADER
def header():
    W, H = 1200, 440
    body = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>', board_header(W, "NOW BOARDING", "TERMINAL GITHUB · PLATFORM 912")]
    body[1] = body[1].replace(f'<rect x="0" y="0" width="{W}" height="64"', f'<path d="M18 0 H{W-18} Q{W} 0 {W} 18 V64 H0 V18 Q0 0 18 0Z"').replace('fill="#131418"/>', f'fill="{PANEL}"/>', 1)
    css = []
    tw, gap = 82, 8
    x0 = (W - (len(NAME) * (tw + gap) - gap)) / 2
    t, c = flap_tiles(NAME, x0, 104, tw, 112, gap, 76, 12, 0.3, 0.12, uid="n")
    body.append(t); css.append(c)
    tw2, gap2 = 26, 4
    x1 = (W - (len(TAGLINE) * (tw2 + gap2) - gap2)) / 2
    t, c = flap_tiles(TAGLINE, x1, 246, tw2, 38, gap2, 22, 12, 1.8, 0.04, color=ACCENT, scr=3, uid="g")
    body.append(t); css.append(c)
    # info strip
    y = 330
    body.append(f'<line x1="40" y1="{y-18}" x2="{W-40}" y2="{y-18}" stroke="{LINE}" stroke-width="1.5"/>')
    cols = [("ORIGIN", "B.TECH CSE · JIIT NOIDA"), ("CREW", "TECH LEAD · RAPID PROG. HUB"), ("STATUS", None)]
    for k, (lab, val) in enumerate(cols):
        cx = 60 + k * 400
        body.append(f'<text x="{cx}" y="{y+4}" font-size="13" fill="{GREY}" letter-spacing="3">{lab}</text>')
        if val:
            body.append(f'<text x="{cx}" y="{y+30}" font-size="18" fill="{WHITE}" letter-spacing="1">{e(val)}</text>')
        else:
            body.append(status_cell(cx + 6, y + 30, "BOARDING NOW", "live"))
    # ticker bar
    body.append(f'<clipPath id="tk"><rect x="0" y="{H-52}" width="{W}" height="52"/></clipPath>')
    body.append(f'<linearGradient id="tkg" x1="0" x2="1"><stop offset="0" stop-color="{TICKER_FROM}"/><stop offset="1" stop-color="{TICKER_TO}"/></linearGradient>')
    body.append(f'<path d="M0 {H-52} H{W} V{H-18} Q{W} {H} {W-18} {H} H18 Q0 {H} 0 {H-18}Z" fill="url(#tkg)"/>')
    t, c = ticker(TICKER, H - 19, W, 19, BG, "tk1")
    body.append(f'<g clip-path="url(#tk)">{t}</g>'); css.append(c)
    open(f"{OUT}/header.svg", "w").write(svg(W, H, "\n".join(body), "\n".join(css)))


# ---------------------------------------------------------------- DEPARTURES
def departures():
    W, rowh = 1200, 78
    H = 64 + 44 + rowh * len(DEPARTURES) + 16
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath><g clip-path="url(#c)">',
         board_header(W, "DEPARTURES", "WHAT I'M BUILDING")]
    cols = [(40, "FLIGHT"), (170, "DESTINATION"), (560, "VIA"), (850, "GATE"), (960, "REMARKS")]
    for x, lab in cols:
        b.append(f'<text x="{x}" y="96" font-size="13" fill="{GREY}" letter-spacing="3">{lab}</text>')
    for i, (fl, dest, desc, via, gate, st, kind) in enumerate(DEPARTURES):
        y = 108 + i * rowh
        if i % 2 == 0:
            b.append(f'<rect x="0" y="{y}" width="{W}" height="{rowh}" fill="{ROW}"/>')
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}"/>')
        b.append(f'<text x="40" y="{y+46}" font-size="18" fill="{GREY}">{fl}</text>')
        b.append(f'<text x="170" y="{y+38}" font-size="26" fill="{PALETTE[i % len(PALETTE)]}" letter-spacing="2">{e(dest)}</text>')
        b.append(f'<text x="170" y="{y+62}" font-size="14" fill="{GREY}" font-weight="400">{e(desc)}</text>')
        b.append(f'<text x="560" y="{y+46}" font-size="15" fill="{WHITE}" letter-spacing="1">{e(via)}</text>')
        b.append(f'<rect x="846" y="{y+24}" width="64" height="30" rx="6" fill="{TILE}" stroke="{PALETTE[i % len(PALETTE)]}" stroke-opacity=".6"/>'
                 f'<text x="878" y="{y+45}" font-size="15" fill="{PALETTE[i % len(PALETTE)]}" text-anchor="middle">{gate}</text>')
        b.append(status_cell(970, y + 46, st, kind))
    b.append("</g>")
    open(f"{OUT}/departures.svg", "w").write(svg(W, H, "\n".join(b)))


# ---------------------------------------------------------------- ARRIVALS
def arrivals():
    W, rowh = 1200, 66
    H = 64 + 44 + rowh * len(ARRIVALS) + 16
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath><g clip-path="url(#c)">',
         board_header(W, "ARRIVALS", "TROPHIES AND MILESTONES")]
    for x, lab in [(40, "EVENT"), (380, "HOSTED BY"), (620, "CREW"), (960, "RESULT")]:
        b.append(f'<text x="{x}" y="96" font-size="13" fill="{GREY}" letter-spacing="3">{lab}</text>')
    for i, (ev, org, proj, st, kind) in enumerate(ARRIVALS):
        y = 108 + i * rowh
        if i % 2 == 0:
            b.append(f'<rect x="0" y="{y}" width="{W}" height="{rowh}" fill="{ROW}"/>')
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}"/>')
        b.append(f'<text x="40" y="{y+41}" font-size="22" fill="{WHITE}" letter-spacing="2">{e(ev)}</text>')
        b.append(f'<text x="380" y="{y+40}" font-size="16" fill="{GREY}" letter-spacing="1">{e(org)}</text>')
        b.append(f'<text x="620" y="{y+40}" font-size="16" fill="{GREY}" letter-spacing="1">{e(proj)}</text>')
        b.append(status_cell(970, y + 40, st, kind))
    b.append("</g>")
    open(f"{OUT}/arrivals.svg", "w").write(svg(W, H, "\n".join(b)))


# ---------------------------------------------------------------- SCOREBOARD
def scoreboard():
    W, H = 1200, 310
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath><g clip-path="url(#c)">',
         board_header(W, "SCOREBOARD", "VIA CODOLIO · NOV 2026")]
    css = []
    n = len(SCOREBOARD)
    cw = (W - 80) / n
    for k, (lab, val, sub) in enumerate(SCOREBOARD):
        cx = 40 + k * cw
        txt = (val or "----").upper()[:5]
        tw, gap = 44, 6
        total = len(txt) * (tw + gap) - gap
        x0 = cx + (cw - total) / 2
        col = SCORE_COLORS[k % len(SCORE_COLORS)]
        t, c = flap_tiles(txt, x0, 100, tw, 64, gap, 40, 12, 0.6 + k * 0.4, 0.1, color=col, uid=f"sc{k}")
        b.append(t); css.append(c)
        b.append(f'<text x="{cx+cw/2:.1f}" y="200" font-size="15" fill="{WHITE}" text-anchor="middle" letter-spacing="3">{e(lab)}</text>')
        b.append(f'<text x="{cx+cw/2:.1f}" y="224" font-size="12" fill="{col if k else ACCENT}" text-anchor="middle" letter-spacing="1">{e(sub)}</text>')
        if k:
            b.append(f'<line x1="{cx:.1f}" y1="96" x2="{cx:.1f}" y2="234" stroke="{LINE}"/>')
    b.append(f'<line x1="40" y1="258" x2="{W-40}" y2="258" stroke="{LINE}"/>')
    b.append(f'<text x="{W/2}" y="288" font-size="13" fill="{GREY}" letter-spacing="2" text-anchor="middle" xml:space="preserve">{e(SCORE_FOOT)}</text>')
    b.append("</g>")
    open(f"{OUT}/scoreboard.svg", "w").write(svg(W, H, "\n".join(b), "\n".join(css)))


# ---------------------------------------------------------------- GATES
def gates():
    W = 1200
    per = 4
    rows = (len(GATES) + per - 1) // per
    H = 64 + 30 + rows * 84 + 20
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath><g clip-path="url(#c)">',
         board_header(W, "GATES", "TOOLKIT · ALL GATES OPEN")]
    gw = (W - 80 - (per - 1) * 16) / per
    for i, (code, name) in enumerate(GATES):
        r, c = divmod(i, per)
        x, y = 40 + c * (gw + 16), 94 + r * 84
        b.append(f'<rect x="{x:.1f}" y="{y}" width="{gw:.1f}" height="64" rx="8" fill="{TILE}" stroke="{LINE}"/>')
        b.append(f'<line x1="{x+72:.1f}" y1="{y+14}" x2="{x+72:.1f}" y2="{y+50}" stroke="{LINE}"/>')
        b.append(f'<text x="{x+36:.1f}" y="{y+42}" font-size="22" fill="{PALETTE[i % len(PALETTE)]}" text-anchor="middle">{code}</text>')
        b.append(f'<text x="{x+92:.1f}" y="{y+41}" font-size="20" fill="{WHITE}">{e(name)}</text>')
        b.append(f'<text x="{x+gw-20:.1f}" y="{y+42}" font-size="22" fill="{GREY}" text-anchor="end">→</text>')
    b.append("</g>")
    open(f"{OUT}/gates.svg", "w").write(svg(W, H, "\n".join(b)))


# ---------------------------------------------------------------- FOOTER
def footer():
    W, H = 1200, 64
    msg = "THANK YOU FOR TRAVELLING WITH YUG   ·   MIND THE GAP BETWEEN IDEA AND DEPLOY   ·   NEXT DEPARTURE: YOUR REPO?   ·   "
    t, c = ticker(msg, 39, W, 17, BG, "ft", speed=45)
    body = (f'<linearGradient id="fg" x1="0" x2="1"><stop offset="0" stop-color="{TICKER_FROM}"/><stop offset="1" stop-color="{TICKER_TO}"/></linearGradient>'
            f'<rect width="{W}" height="{H}" rx="14" fill="url(#fg)"/>'
            f'<clipPath id="fc"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>'
            f'<g clip-path="url(#fc)">{t}</g>')
    open(f"{OUT}/footer.svg", "w").write(svg(W, H, body, c))


for f in (header, departures, arrivals, scoreboard, gates, footer):
    f()
print("written to", OUT)
