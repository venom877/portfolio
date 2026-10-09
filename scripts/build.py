#!/usr/bin/env python3
"""Generate assets/*.svg and README.md from data/profile.json. Standard library only."""
import base64, html, json, random, textwrap
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

CW, CH = 250, 240            # small card size
PW = CW * 2 + 15             # wide card (same height, spans two columns)
STEP_SECS = 4                # seconds each "How I work" step stays visible

BASE_CSS = """
:root{--card:#fff;--stroke:#e9e9e9;--ink:#0d0d0d;--mute:#bdbdbd;--sub:#8c8c8c;--accent:#f26a00;--pill:#f3f3f3;--btn:#0d0d0d;--btnink:#fff}
@media (prefers-color-scheme:dark){:root{--card:#161b22;--stroke:#2a313c;--ink:#f0f3f6;--mute:#4b535e;--sub:#8b949e;--accent:#ff8a2a;--pill:#21262d;--btn:#f0f3f6;--btnink:#0d1117}}
text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;fill:var(--ink)}
.card{fill:var(--card);stroke:var(--stroke);stroke-width:1.5}
.pill{fill:var(--pill)}
.sub{fill:var(--sub)}
.mute{fill:var(--mute)}
.acc{fill:var(--accent)}
"""

def esc(s): return html.escape(str(s), quote=True)
def tw(s, size, k=0.52): return len(s) * size * k   # rough text width

def data_uri(rel):
    p = ROOT / rel if rel else None
    if not p or not p.exists(): return None
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(p.suffix[1:].lower(), "png")
    return f"data:image/{mime};base64," + base64.b64encode(p.read_bytes()).decode()

def svg(w, h, body, label, css="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>'
            f'<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>')

def card(w, h, inner, label, css="", defs="", dashed=False):
    defs += f'<clipPath id="clip"><rect width="{w}" height="{h}" rx="24"/></clipPath>'
    dash = ' stroke-dasharray="6 6"' if dashed else ''
    body = (f'<rect class="card"{dash} x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="24"/>'
            f'<g clip-path="url(#clip)">{inner}</g>')
    return svg(w, h, body, label, css, defs)

def pill(x, y, text):
    w = tw(text, 12, 0.56) + 24
    return (f'<rect class="pill" x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13"/>'
            f'<text x="{x+12}" y="{y+17}" font-size="12">{esc(text)}</text>')

def image(uri, x, y, w, h, rx, cid, fallback):
    if uri:
        return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
                f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fallback}"/>'

# ---------------------------------------------------------------- hero
def hero():
    W, H = 820, 300
    b = []
    b.append('<path d="M20 8 L37 37 Q39 42 33 42 H7 Q1 42 3 37 Z" fill="none" stroke="var(--ink)" stroke-width="4" stroke-linejoin="round"/>')
    b.append('<circle cx="50" cy="45" r="3.5" class="acc"/>')
    b.append(f'<text x="64" y="43" font-size="15" text-decoration="underline">{esc(D["email"])}</text>')
    s = 42; y1 = 135
    pre = "Hi, I’m"
    ax = tw(pre, s, 0.5) + 16
    b.append(f'<text x="0" y="{y1}" font-size="{s}" font-weight="600" letter-spacing="-1.5">{pre}</text>')
    uri = data_uri(D.get("avatar"))
    b.append(image(uri, ax, y1 - 50, 64, 64, 18, "av", "#d9d9d9"))
    if not uri:
        initials = "".join(p[0] for p in D["name"].split()[:2])
        b.append(f'<text x="{ax+32}" y="{y1-10}" font-size="24" font-weight="600" text-anchor="middle" style="fill:#666">{esc(initials)}</text>')
    b.append(f'<text x="{ax+64+14}" y="{y1}" font-size="{s}" font-weight="600" letter-spacing="-1.5">{esc(D["name"])}!</text>')
    y2 = y1 + 60
    b.append(f'<text x="0" y="{y2}" font-size="{s}" font-weight="600" letter-spacing="-1.5">'
             f'<tspan class="mute">{esc(D.get("intro", "I’m a"))} </tspan><tspan>{esc(D["role"])}</tspan><tspan class="mute"> at</tspan></text>')
    y3 = y2 + 60
    comp = D["company"] + "."
    b.append(f'<text x="0" y="{y3}" font-size="{s}" font-weight="600" letter-spacing="-1.5" class="acc">{esc(comp)}</text>')
    px = tw(comp, s, 0.5) + 28
    pw = tw(D["status"], 14) + 52
    b.append(f'<rect x="{px}" y="{y3-38}" width="{pw:.0f}" height="40" rx="20" fill="none" stroke="var(--stroke)" stroke-width="1.5"/>')
    b.append(f'<circle cx="{px+22}" cy="{y3-18}" r="9" fill="#2ee59d" opacity=".3"/><circle cx="{px+22}" cy="{y3-18}" r="5" fill="#2ee59d"/>')
    b.append(f'<text x="{px+38}" y="{y3-13}" font-size="14">{esc(D["status"])}</text>')
    return svg(W, H, "".join(b), f'{D["name"]}, {D["role"]} at {D["company"]}')

def cta():
    W, H = 820, 70
    l1, l2 = D["cta_lines"]
    label = D.get("cta_label", "Book a call")
    bw = tw(label, 17, 0.55) + 56
    b = (f'<rect x="0" y="6" width="{bw:.0f}" height="52" rx="26" fill="var(--btn)"/>'
         f'<text x="{bw/2:.0f}" y="38" font-size="17" font-weight="500" text-anchor="middle" style="fill:var(--btnink)">{esc(label)}</text>'
         f'<text x="{bw+22:.0f}" y="29" font-size="18">{esc(l1)}</text><text x="{bw+22:.0f}" y="53" font-size="18">{esc(l2)}</text>')
    return svg(W, H, b, label)

# ---------------------------------------------------------------- cards
def timeline_card(label, items, aria):
    """states: done (filled) | current (accent glow) | scheduled (accent ring) | progress (dashed ring)"""
    b = [pill(16, 16, label)]
    items = items[:4]; y0 = 84
    last = y0 + (len(items) - 1) * 44
    b.append(f'<line x1="28" y1="{y0-5}" x2="28" y2="{last-5}" stroke="var(--ink)" stroke-width="1.5"/>')
    for i, it in enumerate(items):
        y = y0 + i * 44; cy = y - 5; st = it.get("state", "done")
        if st == "current":
            dot = f'<circle cx="28" cy="{cy}" r="9" class="acc" opacity=".25"/><circle cx="28" cy="{cy}" r="5" class="acc"/>'
        elif st == "scheduled":
            dot = f'<circle cx="28" cy="{cy}" r="5" fill="var(--card)" stroke="var(--accent)" stroke-width="2"/>'
        elif st == "progress":
            dot = f'<circle cx="28" cy="{cy}" r="5" fill="var(--card)" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="2.5 2"/>'
        else:
            dot = f'<circle cx="28" cy="{cy}" r="5" fill="var(--ink)"/>'
        b.append(dot)
        b.append(f'<text x="46" y="{y}" font-size="13.5" font-weight="500">{esc(it["title"])}</text>')
        b.append(f'<text x="46" y="{y+16}" font-size="11" class="sub">{esc(it["meta"])}</text>')
    return card(CW, CH, "".join(b), aria)

def experience(): return timeline_card("My Experience", D["experience"], "Experience")
def certs(): return timeline_card("Certifications & education", D["certs"], "Certifications and education")

def music():
    m = D["music"]; c = (m.get("covers") or []) + [None] * 3
    colors = ["#c9c9c9", "#e8a33d", "#6b4a3a"]
    b = [pill(16, 16, "My music playlist")]
    b.append(f'<g transform="rotate(-8 50 130)">{image(data_uri(c[0]), 14, 82, 82, 82, 10, "m1", colors[0])}</g>')
    b.append(f'<g transform="rotate(8 200 130)">{image(data_uri(c[2]), 158, 82, 82, 82, 10, "m3", colors[2])}</g>')
    b.append(image(data_uri(c[1]), 79, 56, 100, 100, 12, "m2", colors[1]))
    b.append('<rect x="79" y="56" width="100" height="100" rx="12" fill="none" stroke="var(--card)" stroke-width="3"/>')
    b.append(f'<text x="{CW/2}" y="190" font-size="14" font-weight="500" text-anchor="middle">{esc(m["title"])}</text>')
    t = "Play on Spotify"; x0 = CW / 2 - (tw(t, 10.5) + 14) / 2
    b.append(f'<path d="M{x0} 203 L{x0} 213 L{x0+8} 208 Z" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-linejoin="round"/>')
    b.append(f'<text x="{x0+14}" y="212" font-size="10.5" class="sub">{t}</text>')
    return card(CW, CH, "".join(b), "Music playlist")

def reading():
    r = D["reading"]
    b = [pill(16, 16, "What I’m reading")]
    lines = textwrap.wrap(r["title"], 20)[:2]
    for i, ln in enumerate(lines):
        b.append(f'<text x="16" y="{68+i*16}" font-size="13" font-weight="500">{esc(ln)}</text>')
    b.append(f'<text x="16" y="{68+len(lines)*16+2}" font-size="10" class="sub">{esc(r["author"])}</text>')
    uri = data_uri(r.get("cover"))
    if uri:
        b.append(image(uri, 62, 120, 126, 150, 10, "bk", "#f26a00"))
    else:
        b.append('<rect x="60" y="116" width="130" height="150" rx="14" class="pill"/>')
        b.append('<rect x="88" y="132" width="70" height="140" rx="3" fill="#f26a00"/>')
        b.append(f'<text transform="translate(142 146) rotate(90)" font-size="34" font-weight="700" letter-spacing="-1" style="fill:#fff">{esc(r.get("spine_text","book"))}</text>')
    return card(CW, CH, "".join(b), "Currently reading")

def map_card():
    m = D["map"]; rnd = random.Random(m["city"])
    roads = []
    for i in range(16):
        y = i * 14 - 10; a = rnd.uniform(-14, 14)
        roads.append(f'<path d="M-10 {y} L{CW+10} {y+a:.1f}" />')
    for i in range(14):
        x = i * 19 - 10; a = rnd.uniform(-18, 18)
        roads.append(f'<path d="M{x} -10 L{x+a:.1f} 190" />')
    for _ in range(6):
        x1, y1, x2, y2 = rnd.randint(0, CW), rnd.randint(0, 120), rnd.randint(0, CW), rnd.randint(0, 160)
        roads.append(f'<path d="M{x1} {y1} Q{rnd.randint(0,CW)} {rnd.randint(0,160)} {x2} {y2}" stroke-width="2.2"/>')
    defs = ('<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="var(--card)" stop-opacity="0"/><stop offset=".55" stop-color="var(--card)"/></linearGradient>')
    b = [f'<g stroke="var(--mute)" stroke-width="1" fill="none" opacity=".8">{"".join(roads)}</g>',
         f'<rect x="0" y="100" width="{CW}" height="{CH-100}" fill="url(#fade)"/>',
         '<rect x="12" y="12" width="52" height="30" rx="15" fill="var(--card)"/>',
         '<text x="38" y="32" font-size="12" text-anchor="middle">Map</text>',
         f'<text x="{CW/2}" y="190" font-size="21" letter-spacing="6" text-anchor="middle">{esc(m["city"])}</text>',
         f'<text x="{CW/2}" y="208" font-size="9" letter-spacing="4" text-anchor="middle" class="sub">{esc(m["country"])}</text>',
         f'<text x="{CW/2}" y="224" font-size="7.5" letter-spacing="1.5" text-anchor="middle" class="mute">{esc(m["coords"])}</text>']
    return card(CW, CH, "".join(b), f'Map: {m["city"]}', defs=defs)

def process():
    steps = D["process"]; n = len(steps); total = n * STEP_SECS
    css = (f".step,.act{{opacity:0;animation:cyc {total}s linear infinite}}"
           f"@keyframes cyc{{0%{{opacity:0}}1.5%{{opacity:1}}{100/n-1.5:.1f}%{{opacity:1}}{100/n:.1f}%{{opacity:0}}100%{{opacity:0}}}}"
           "@media (prefers-reduced-motion:reduce){.step,.act{animation:none}.s0,.a0{opacity:1}}")
    b = [pill(16, 16, D.get("process_label", "How I work"))]
    for i, s in enumerate(steps):
        g = [f'<text x="24" y="92" font-size="16" font-weight="600">{i+1:02d} {esc(s["title"])}</text>']
        for j, ln in enumerate(textwrap.wrap(s["text"], 80)[:4]):
            g.append(f'<text x="24" y="{116+j*16}" font-size="11.5" class="sub">{esc(ln)}</text>')
        b.append(f'<g class="step s{i}" style="animation-delay:{i*STEP_SECS}s">{"".join(g)}</g>')
    bx, bw = 16, PW - 32; sw = bw / n
    b.append(f'<rect x="{bx}" y="180" width="{bw}" height="44" rx="22" class="pill"/>')
    for i in range(n):
        x = bx + i * sw; cx = x + sw / 2
        b.append(f'<text x="{cx}" y="207" font-size="11.5" text-anchor="middle">Step {i+1:02d}</text>')
        b.append(f'<g class="act a{i}" style="animation-delay:{i*STEP_SECS}s">'
                 f'<rect x="{x+4}" y="184" width="{sw-8}" height="36" rx="18" fill="var(--btn)"/>'
                 f'<text x="{cx}" y="207" font-size="11.5" text-anchor="middle" style="fill:var(--btnink)">Step {i+1:02d}</text></g>')
    return card(PW, CH, "".join(b), D.get("process_label", "How I work"), css=css)

# ---------------------------------------------------------------- new cards
def chip(x, y, text, hl=False):
    w = tw(text, 11, 0.55) + 18
    st = ' stroke="var(--accent)" stroke-width="1.2"' if hl else ""
    return (f'<rect class="pill" x="{x:.0f}" y="{y}" width="{w:.0f}" height="22" rx="11"{st}/>'
            f'<text x="{x+9:.0f}" y="{y+15}" font-size="11">{esc(text)}</text>'), w

def skills():
    b = [pill(16, 16, "Skills")]
    y, x0, maxx = 60, 88, PW - 16
    for g in D["skills"]:
        b.append(f'<text x="16" y="{y+15}" font-size="11" class="sub">{esc(g["group"])}</text>')
        x = x0
        for it in g["items"]:
            c, w = chip(x, y, it, g.get("highlight"))
            if x + w > maxx:
                x = x0; y += 26; c, w = chip(x, y, it, g.get("highlight"))
            b.append(c); x += w + 6
        y += 34
    if y > CH: print("warning: skills card overflows, drop an item or a group")
    return card(PW, CH, "".join(b), "Skills")

def countdown():
    c = D["countdown"]; d = date.fromisoformat(c["date"]); days = (d - date.today()).days
    big, size = (str(days), 76) if days > 0 else (("Today", 48) if days == 0 else ("Done", 48))
    small = f'days until {c["label"]}' if days > 0 else (c["label"] + (" exam day" if days == 0 else " exam taken"))
    b = [pill(16, 16, "Exam countdown"),
         f'<text x="{CW/2}" y="140" font-size="{size}" font-weight="600" letter-spacing="-3" text-anchor="middle" class="acc">{big}</text>',
         f'<text x="{CW/2}" y="168" font-size="13" text-anchor="middle">{esc(small)}</text>',
         f'<text x="{CW/2}" y="188" font-size="11" text-anchor="middle" class="sub">{d.strftime("%d %b %Y")}</text>',
         f'<text x="{CW/2}" y="222" font-size="9" text-anchor="middle" class="mute">Updated daily by GitHub Actions</text>']
    return card(CW, CH, "".join(b), f"{days} days until {c['label']}")

def findme():
    b = [pill(16, 16, "Find me")]
    rows = [("GitHub", D["github"]), ("Email", D["email"]), ("Location", D["location"])]
    for i, (k, v) in enumerate(rows):
        y = 84 + i * 48
        b.append(f'<text x="20" y="{y}" font-size="10.5" class="sub">{k}</text>')
        b.append(f'<text x="20" y="{y+18}" font-size="13" font-weight="500">{esc(v)}</text>')
    return card(CW, CH, "".join(b), "Contact links")

def project_card(p):
    planned = p.get("status") == "planned"
    labels = {"shipped": "Shipped", "in-progress": "In progress", "planned": "Planned"}
    b = [pill(16, 16, labels.get(p["status"], p["status"]))]
    y = 68
    for ln in textwrap.wrap(p["title"], 22, max_lines=2, placeholder="…"):
        b.append(f'<text x="18" y="{y}" font-size="15" font-weight="600">{esc(ln)}</text>'); y += 20
    y += 4
    for ln in textwrap.wrap(p["text"], 36, max_lines=5, placeholder="…"):
        b.append(f'<text x="18" y="{y}" font-size="11" class="sub">{esc(ln)}</text>'); y += 15
    x = 16
    for t in p.get("tech", [])[:4]:
        c, w = chip(x, CH - 38, t)
        if x + w > CW - 12: break
        b.append(c); x += w + 5
    return card(CW, CH, "".join(b), p["title"], dashed=planned)

# ---------------------------------------------------------------- readme
# Each row is a list of (card name, width). 32% + 32% + 32% or 32% + 66% fits GitHub's README width.
LAYOUT = [
    [("experience", "32%"), ("certs", "32%"), ("map", "32%")],
    [("countdown", "32%"), ("skills", "66%")],
    [("process", "66%"), ("findme", "32%")],
]
LINKS = {"findme": D.get("github_url"), "music": D.get("music", {}).get("url"), "reading": D.get("reading", {}).get("url")}

def readme(card_names):
    img = lambda f, w, alt: f'<img src="assets/{f}.svg" width="{w}" alt="{esc(alt)}">'
    link = lambda url, inner: f'<a href="{esc(url)}">{inner}</a>' if url else inner
    def row(items):
        return '<p align="center">' + " ".join(link(u, img(n, w, n)) for n, w, u in items) + "</p>"
    out = ['<div align="center">', "",
           img("hero", "100%", f'{D["name"]}, {D["role"]} at {D["company"]}'), "",
           link(D.get("cta_url"), img("cta", "100%", D.get("cta_label", "Contact"))), ""]
    for r in LAYOUT:
        items = [(n, w, LINKS.get(n)) for n, w in r if n in card_names]
        if items: out += [row(items), ""]
    projects = D.get("projects", [])
    if projects:
        out += ['<h3 align="center">Projects</h3>', ""]
        for i in range(0, len(projects), 3):
            items = [(f"project-{j+1}", "32%", projects[j].get("url")) for j in range(i, min(i + 3, len(projects)))]
            out += [row(items), ""]
    out += [f'<sub><a href="mailto:{esc(D["email"])}">{esc(D["email"])}</a></sub>', "", "</div>", ""]
    return "\n".join(out)

if __name__ == "__main__":
    for f in OUT.glob("*.svg"): f.unlink()          # drop cards for removed projects
    cards = {"hero": hero(), "cta": cta(), "experience": experience(), "certs": certs(), "map": map_card(),
             "countdown": countdown(), "skills": skills(), "process": process(), "findme": findme()}
    if "music" in D: cards["music"] = music()
    if "reading" in D: cards["reading"] = reading()
    for i, p in enumerate(D.get("projects", [])): cards[f"project-{i+1}"] = project_card(p)
    for name, content in cards.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
    (ROOT / "README.md").write_text(readme(set(cards)), encoding="utf-8")
    print("Built:", ", ".join(cards), "+ README.md")
