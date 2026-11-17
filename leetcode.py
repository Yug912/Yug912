"""Draw assets/leetcode.svg: daily LeetCode submissions for the last 31 days,
styled to match the GitHub "FLIGHT LOG" activity graph in the README.

Run:  python3 leetcode.py          (refreshed daily by .github/workflows/leetcode.yml)
"""
import datetime as dt, json, math, os, sys, urllib.request

USERNAME = "YUG_THAKRAL_18"
DAYS = 31
TITLE = "LEETCODE LOG · LAST 31 DAYS"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "leetcode.svg")

BG, AMBER, WHITE = "#0b0c0e", "#FFB000", "#F2F0E8"
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"


def fetch_calendar(saved=None):
    """Return {date: submissions} from LeetCode's public profile calendar (UTC days).
    `saved` is an optional path to a GraphQL response saved earlier (for offline runs)."""
    if saved:
        with open(saved) as f:
            user = json.load(f)["data"]["matchedUser"]
    else:
        query = "query($u:String!){matchedUser(username:$u){userCalendar{submissionCalendar}}}"
        req = urllib.request.Request(
            "https://leetcode.com/graphql",
            data=json.dumps({"query": query, "variables": {"u": USERNAME}}).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "profile-readme-chart"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            user = json.load(r)["data"]["matchedUser"]
    if not user:
        raise SystemExit(f"LeetCode user {USERNAME!r} not found")
    raw = json.loads(user["userCalendar"]["submissionCalendar"])
    return {dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).date(): n for ts, n in raw.items()}


def nice_step(top):
    """Pick a round tick step that gives roughly 5-10 gridlines."""
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500):
        if top / s <= 10:
            return s
    return 1000


def render(days, counts):
    W, H = 1200, 420
    L, R, T, B = 90, 1160, 90, 330          # plot area
    step = nice_step(max(max(counts), 5))
    ymax = max(step * math.ceil(max(counts) / step), step * 2)
    n = len(counts)
    xs = [L + i * (R - L) / (n - 1) for i in range(n)]
    ys = [B - c / ymax * (B - T) for c in counts]

    out = [f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>',
           f'<text x="{W/2}" y="52" font-size="22" fill="{AMBER}" text-anchor="middle">{TITLE}</text>']

    # grid + y labels
    for k in range(0, ymax + 1, step):
        y = B - k / ymax * (B - T)
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="{AMBER}" stroke-opacity=".18" stroke-dasharray="3 3"/>')
        out.append(f'<text x="{L-12}" y="{y+5:.1f}" font-size="13" fill="{AMBER}" text-anchor="end">{k}</text>')
    for x, d in zip(xs, days):
        out.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{B}" stroke="{AMBER}" stroke-opacity=".18" stroke-dasharray="3 3"/>')
        out.append(f'<text x="{x:.1f}" y="{B+24}" font-size="13" fill="{AMBER}" text-anchor="middle">{d.day}</text>')
    out.append(f'<text x="{(L+R)/2}" y="{B+62}" font-size="14" fill="{AMBER}" text-anchor="middle">Days</text>')
    out.append(f'<text transform="translate(38 {(T+B)/2}) rotate(-90)" font-size="14" fill="{AMBER}" text-anchor="middle">Submissions</text>')

    # smooth curve (Catmull-Rom -> cubic Bezier), control points kept inside the plot
    def clamp(v): return min(max(v, T), B)
    path = f"M{xs[0]:.1f},{ys[0]:.1f}"
    for i in range(n - 1):
        x0, y0 = xs[max(i - 1, 0)], ys[max(i - 1, 0)]
        x1, y1, x2, y2 = xs[i], ys[i], xs[i + 1], ys[i + 1]
        x3, y3 = xs[min(i + 2, n - 1)], ys[min(i + 2, n - 1)]
        c1 = (x1 + (x2 - x0) / 6, clamp(y1 + (y2 - y0) / 6))
        c2 = (x2 - (x3 - x1) / 6, clamp(y2 - (y3 - y1) / 6))
        path += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {x2:.1f},{y2:.1f}"
    out.append(f'<path d="{path} L{xs[-1]:.1f},{B} L{xs[0]:.1f},{B}Z" fill="{AMBER}" fill-opacity=".1"/>')
    out.append(f'<path d="{path}" fill="none" stroke="{AMBER}" stroke-width="4" stroke-linejoin="round"/>')
    for x, y, d, c in zip(xs, ys, days, counts):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{WHITE}"><title>{d:%b %d}: {c}</title></circle>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}" font-weight="700">\n' + "\n".join(out) + "\n</svg>\n")


def main():
    cal = fetch_calendar(sys.argv[1] if len(sys.argv) > 1 else None)
    today = dt.datetime.now(dt.timezone.utc).date()
    days = [today - dt.timedelta(days=DAYS - 1 - i) for i in range(DAYS)]
    counts = [cal.get(d, 0) for d in days]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(render(days, counts))
    print(f"wrote {OUT}: {sum(counts)} submissions over {DAYS} days")


if __name__ == "__main__":
    sys.exit(main())
