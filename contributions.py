"""Draw assets/contributions.svg: the GitHub contribution calendar for the last year,
recoloured in the departure-board amber theme.

Run:  GITHUB_TOKEN=... python3 contributions.py     (refreshed daily by .github/workflows/charts.yml)
      python3 contributions.py saved.json           (offline, from a saved GraphQL response)
"""
import datetime as dt, json, os, sys, urllib.request
from html import escape as e

USERNAME = "Yug912"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "contributions.svg")

BG, PANEL, TILE = "#0b0c0e", "#131418", "#1c1d22"
AMBER, WHITE, GREY = "#FFB000", "#F2F0E8", "#7c7f87"
FONT = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Courier New',monospace"
LEVELS = {"NONE": TILE, "FIRST_QUARTILE": "#4a3610", "SECOND_QUARTILE": "#8a6a1f",
          "THIRD_QUARTILE": "#c98c00", "FOURTH_QUARTILE": AMBER}

QUERY = ("query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{"
         "totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}")


def fetch(saved=None):
    if saved:
        with open(saved) as f:
            data = json.load(f)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN is not set")
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"u": USERNAME}}).encode(),
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                     "User-Agent": "profile-readme-chart"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal):
    weeks = cal["weeks"]
    W, H = 1200, 330
    cell, gap = 16, 4
    pitch = cell + gap
    x0 = (W - (len(weeks) * pitch - gap)) / 2 + 24      # leave room for weekday labels
    y0 = 124

    def board(w, title, right):
        return (f'<rect x="0" y="0" width="{w}" height="64" fill="{PANEL}"/>'
                f'<circle cx="36" cy="32" r="7" fill="{AMBER}" class="blink"/>'
                f'<text x="56" y="41" font-size="24" fill="{AMBER}" letter-spacing="6">{e(title)}</text>'
                f'<text x="{w-32}" y="40" font-size="15" fill="{GREY}" text-anchor="end" letter-spacing="3">{e(right)}</text>')

    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
         f'<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath><g clip-path="url(#c)">',
         board(W, "FLIGHT HISTORY", f"{cal['totalContributions']} CONTRIBUTIONS · LAST 12 MONTHS")]

    # month labels: at the first week whose first day falls in a new month
    last_month = None
    for i, wk in enumerate(weeks):
        d = dt.date.fromisoformat(wk["contributionDays"][0]["date"])
        if d.month != last_month:
            if last_month is not None or d.day <= 7:
                if i < len(weeks) - 2:
                    b.append(f'<text x="{x0 + i*pitch:.1f}" y="{y0-14}" font-size="13" fill="{GREY}" letter-spacing="2">{d:%b}</text>'.replace(f">{d:%b}<", f">{d:%b}<".upper()))
            last_month = d.month
    for row, lab in ((1, "MON"), (3, "WED"), (5, "FRI")):
        b.append(f'<text x="{x0-12:.1f}" y="{y0 + row*pitch + 12}" font-size="12" fill="{GREY}" text-anchor="end" letter-spacing="1">{lab}</text>')

    # cells; the most recent day gets a blinking outline
    last_day = weeks[-1]["contributionDays"][-1]["date"]
    for i, wk in enumerate(weeks):
        for day in wk["contributionDays"]:
            d = dt.date.fromisoformat(day["date"])
            row = (d.weekday() + 1) % 7            # Sunday = row 0, as on GitHub
            x, y = x0 + i * pitch, y0 + row * pitch
            n = day["contributionCount"]
            tip = f'{n} contribution{"s" if n != 1 else ""} on {d:%b %d, %Y}'
            b.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                     f'fill="{LEVELS.get(day["contributionLevel"], TILE)}"><title>{tip}</title></rect>')
            if day["date"] == last_day:
                b.append(f'<rect x="{x-2:.1f}" y="{y-2}" width="{cell+4}" height="{cell+4}" rx="4" fill="none" stroke="{WHITE}" stroke-width="1.5" class="blink"/>')

    # legend
    ly = y0 + 7 * pitch + 22
    b.append(f'<line x1="40" y1="{ly-6}" x2="{W-40}" y2="{ly-6}" stroke="#25272d"/>')
    b.append(f'<rect x="42" y="{ly+11}" width="{cell}" height="{cell}" rx="3" fill="none" stroke="{WHITE}" stroke-width="1.5" class="blink"/>'
             f'<text x="{42+cell+12}" y="{ly+24}" font-size="13" fill="{GREY}" letter-spacing="2">TODAY</text>')
    lx = W - 40 - 5 * pitch - 60
    b.append(f'<text x="{lx-12}" y="{ly+24}" font-size="13" fill="{GREY}" text-anchor="end" letter-spacing="2">LESS</text>')
    for k, col in enumerate(LEVELS.values()):
        b.append(f'<rect x="{lx + k*pitch}" y="{ly+11}" width="{cell}" height="{cell}" rx="3" fill="{col}"/>')
    b.append(f'<text x="{lx + 5*pitch + 6}" y="{ly+24}" font-size="13" fill="{GREY}" letter-spacing="2">MORE</text>')
    b.append("</g>")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}" font-weight="700">\n<style>\n'
            "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.15}}\n"
            ".blink{animation:blink 1.2s steps(1) infinite}\n</style>\n"
            + "\n".join(b) + "\n</svg>\n")


def main():
    cal = fetch(sys.argv[1] if len(sys.argv) > 1 else None)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(render(cal))
    print(f"wrote {OUT}: {cal['totalContributions']} contributions")


if __name__ == "__main__":
    sys.exit(main())
