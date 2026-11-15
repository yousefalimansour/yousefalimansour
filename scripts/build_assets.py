#!/usr/bin/env python3
"""Builds the animated SVG graphics used by the profile README (hero banner, event-flow
diagram, tech stack, footer, link buttons).

Edit the text in this file (for example the typed phrases in hero()) and regenerate with:

    python scripts/build_assets.py assets scripts/icons

The logos in scripts/icons come from Simple Icons (CC0).
"""
import math
import random
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
ICONS = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

FG = "#e6edf3"
MUTED = "#9da7b3"
DIM = "#7d8590"
CYAN, BLUE, VIOLET, PINK, GREEN = "#22d3ee", "#60a5fa", "#a78bfa", "#f472b6", "#34d399"


def n(x, d=2):
    s = f"{x:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("", "-0"):
        return "0"
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def css(s):
    return s.replace("@SANS", SANS).replace("@MONO", MONO)


def icon_path(name):
    t = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', t).group(1)


def text_w(s, size, bold=False):
    w = 0.0
    for ch in s:
        if ch in "iljI.,:;'|!":
            w += 0.27
        elif ch == " ":
            w += 0.28
        elif ch in "ftr":
            w += 0.36
        elif ch in "mwMW":
            w += 0.86
        elif ch.isupper():
            w += 0.66
        elif ch.isdigit():
            w += 0.56
        elif ch in "#+&":
            w += 0.64
        elif ch in "·-/":
            w += 0.36
        else:
            w += 0.54
    return w * size * (1.06 if bold else 1.0)


def card_defs(w, h, rx=22):
    return (
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0f1e"/><stop offset=".55" stop-color="#0d1117"/>'
        '<stop offset="1" stop-color="#140f2a"/></linearGradient>'
    )


def card_border(w, h, rx=22):
    return (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .5}" '
        'fill="none" stroke="#30363d" stroke-width="1.5"/>'
    )


GLOW = (
    '<filter id="gl" x="-150%" y="-150%" width="400%" height="400%">'
    '<feGaussianBlur stdDeviation="3.2" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)

REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def name_gradient(x1, x2, dur=7):
    span = x2 - x1
    return (
        f'<linearGradient id="ng" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x2}" y2="0" spreadMethod="reflect">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".35" stop-color="{BLUE}"/>'
        f'<stop offset=".7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{span * 2} 0" '
        f'dur="{dur}s" repeatCount="indefinite"/></linearGradient>'
    )


def ellipse_path(cx, cy, rx, ry, rot):
    a = math.radians(rot)
    x1, y1 = cx + rx * math.cos(a), cy + rx * math.sin(a)
    x2, y2 = cx - rx * math.cos(a), cy - rx * math.sin(a)
    return (
        f"M{n(x1)} {n(y1)}A{rx} {ry} {rot} 1 1 {n(x2)} {n(y2)}"
        f"A{rx} {ry} {rot} 1 1 {n(x1)} {n(y1)}Z"
    )


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 400
    rnd = random.Random(11)
    cx, cy = 942, 205

    stars = []
    for _ in range(48):
        x, y = rnd.uniform(16, W - 16), rnd.uniform(12, H - 12)
        r = rnd.choice([0.7, 0.9, 1.1, 1.4, 1.7])
        stars.append(
            f'<circle cx="{n(x, 1)}" cy="{n(y, 1)}" r="{r}" '
            f'style="animation-duration:{n(rnd.uniform(2.4, 5.6), 1)}s;animation-delay:-{n(rnd.uniform(0, 5), 1)}s"/>'
        )

    comet_rows = [
        (46, 9, 0, 1, 0.5, 150), (112, 13, 4, 2, 0.38, 110), (178, 7.5, 2, 3, 0.3, 90),
        (252, 11, 7, 1, 0.3, 130), (306, 8.5, 5, 2, 0.42, 160), (366, 12, 1, 3, 0.38, 120),
    ]
    comets = [
        f'<rect class="comet" x="-180" y="{y}" width="{w}" height="2" rx="1" fill="url(#cm{c})" opacity="{op}" '
        f'style="animation-duration:{d}s;animation-delay:-{dl}s"/>'
        for (y, d, dl, c, op, w) in comet_rows
    ]

    orbits = [
        (115, 50, -20, 14, [("API", CYAN, 0), ("Redis", "#ff7b72", 7)]),
        (165, 78, 14, 22, [("Kafka", FG, 2), (".NET", VIOLET, 9.3), ("Docker", "#58a6ff", 16.6)]),
        (208, 108, -6, 30, [("Python", "#ffd43b", 4), ("Go", CYAN, 14), ("AWS", "#ff9900", 24)]),
    ]
    orbit_svg, chip_svg = [], []
    dot_colors = [CYAN, PINK, VIOLET]
    for i, (rx, ry, rot, dur, chips) in enumerate(orbits):
        d = ellipse_path(cx, cy, rx, ry, rot)
        orbit_svg.append(f'<path class="orb" d="{d}" style="animation-duration:{8 + i * 4}s"/>')
        orbit_svg.append(
            f'<circle r="2.8" fill="{dot_colors[i]}" filter="url(#gl)">'
            f'<animateMotion dur="{n(dur / 2.5, 1)}s" repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="1;0" keyTimes="0;1" path="{d}"/></circle>'
        )
        for label, color, phase in chips:
            tl = len(label) * 9.6
            w = tl + 28
            chip_svg.append(
                f'<g><animateMotion dur="{dur}s" begin="-{phase}s" repeatCount="indefinite" path="{d}"/>'
                f'<rect x="{n(-w / 2)}" y="-16" width="{n(w)}" height="32" rx="16" fill="#0d1117" fill-opacity=".92" '
                f'stroke="{color}" stroke-opacity=".8" stroke-width="1.2"/>'
                f'<text class="chip" y="5.6" text-anchor="middle" fill="{color}" textLength="{n(tl)}" '
                f'lengthAdjust="spacingAndGlyphs">{esc(label)}</text></g>'
            )

    # typewriter
    phrases = [
        "Backend Software Engineer",
        "Event-Driven & Distributed Systems",
        "Python · C# / .NET · Go",
        "AWS Certified Cloud Practitioner",
        "AI Agents & RAG Pipelines",
    ]
    P = 4.6
    T = P * len(phrases)
    cw, x0 = 14.4, 30
    typed = []
    cursor = [(0.0, x0)]
    for i, ph in enumerate(phrases):
        ws, L = i * P, len(ph)
        dt = min(0.06, 1.7 / L)
        t0 = ws + 0.3
        hold_end = ws + 3.45
        ddt = min(0.025, 0.7 / L)
        for k, ch in enumerate(ph):
            ta = t0 + k * dt
            td = hold_end + (L - 1 - k) * ddt
            cursor.append((ta, x0 + (k + 1) * cw))
            if ch != " ":
                typed.append(
                    f'<text x="{n(x0 + k * cw)}" opacity="0">{esc(ch)}'
                    f'<animate attributeName="opacity" dur="{n(T)}s" repeatCount="indefinite" calcMode="discrete" '
                    f'values="0;1;0" keyTimes="0;{n(ta / T, 5)};{n(td / T, 5)}"/></text>'
                )
        for k in range(L - 1, -1, -1):
            cursor.append((hold_end + (L - 1 - k) * ddt, x0 + k * cw))
    cur_vals = ";".join(n(x) for _, x in cursor)
    cur_times = ";".join(n(t / T, 5) for t, _ in cursor)

    style = css(
        """
.stars circle{fill:#fff;opacity:.14;animation:tw 4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.1}50%{opacity:.9}}
.comet{animation:fly 9s linear infinite}
@keyframes fly{from{transform:translateX(0)}to{transform:translateX(1560px)}}
.blob{animation:d1 17s ease-in-out infinite alternate}
.b2{animation-name:d2;animation-duration:21s}
.b3{animation-name:d3;animation-duration:14s}
@keyframes d1{from{transform:translate(0,0)}to{transform:translate(130px,60px)}}
@keyframes d2{from{transform:translate(0,0)}to{transform:translate(-150px,-70px)}}
@keyframes d3{from{transform:translate(0,0)}to{transform:translate(90px,80px)}}
.orb{fill:none;stroke:#fff;stroke-opacity:.16;stroke-width:1.2;stroke-dasharray:3 7;animation:dash 8s linear infinite}
@keyframes dash{to{stroke-dashoffset:-100}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 3.6s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(.86);opacity:.75}50%{transform:scale(1.12);opacity:1}}
.ping{fill:none;stroke-width:1.5;transform-box:fill-box;transform-origin:center;animation:ping 3.6s ease-out infinite}
.p2{animation-delay:-1.8s}
@keyframes ping{0%{transform:scale(1);opacity:.75}100%{transform:scale(3.2);opacity:0}}
.chip{font:700 16px @MONO}
.core{font:700 22px @MONO;fill:#e6edf3}
.pill{font:700 13px @MONO;fill:#7ee787}
.halo{transform-box:fill-box;transform-origin:center;animation:halo 1.8s ease-out infinite}
@keyframes halo{0%{transform:scale(.6);opacity:.7}100%{transform:scale(2.1);opacity:0}}
.hi{font:400 26px @SANS;fill:#9da7b3}
.name{font:800 62px @SANS;letter-spacing:-.5px}
.ty text{font:500 24px @MONO;fill:#e6edf3}
.ty .pr{fill:#22d3ee;font-weight:700}
.cur{animation:blink 1s steps(1) infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
.meta{font:400 16px @SANS;fill:#9da7b3}
.in{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.i2{animation-delay:.12s}.i3{animation-delay:.24s}.i4{animation-delay:.36s}.i5{animation-delay:.48s}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
"""
        + REDUCED
    )

    label = (
        "Yousef Ali Mansour — Backend Software Engineer. Event-driven and distributed systems, "
        "Python, C# / .NET and Go, AWS Certified Cloud Practitioner. Open to opportunities."
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
{card_defs(W, H)}
{name_gradient(70, 670)}
<radialGradient id="ga"><stop offset="0" stop-color="{CYAN}" stop-opacity=".34"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="gb"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".4"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="gc"><stop offset="0" stop-color="{PINK}" stop-opacity=".22"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<radialGradient id="cg"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".55"/><stop offset=".55" stop-color="{CYAN}" stop-opacity=".16"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="cm1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<linearGradient id="cm2"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="cm3"><stop offset="0" stop-color="{PINK}" stop-opacity="0"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="1.3" cy="1.3" r="1.3" fill="#fff"/></pattern>
<radialGradient id="mkg" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="430"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="mk"><rect width="{W}" height="{H}" fill="url(#mkg)"/></mask>
{GLOW}
</defs>
<style>{style}</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<circle class="blob b1" cx="160" cy="40" r="320" fill="url(#ga)"/>
<circle class="blob b2" cx="1040" cy="400" r="360" fill="url(#gb)"/>
<circle class="blob b3" cx="600" cy="-60" r="280" fill="url(#gc)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".1" mask="url(#mk)"/>
<g class="stars">{''.join(stars)}</g>
<g>{''.join(comets)}</g>
<g>
<circle class="pulse" cx="{cx}" cy="{cy}" r="96" fill="url(#cg)"/>
{''.join(orbit_svg)}
<circle class="ping" cx="{cx}" cy="{cy}" r="38" stroke="{VIOLET}"/>
<circle class="ping p2" cx="{cx}" cy="{cy}" r="38" stroke="{CYAN}"/>
<circle cx="{cx}" cy="{cy}" r="38" fill="#0d1117" stroke="url(#ring)" stroke-width="2.5"/>
<text class="core" x="{cx}" y="{cy + 7.5}" text-anchor="middle">&lt;/&gt;</text>
{''.join(chip_svg)}
</g>
<g class="in">
<rect x="70" y="62" width="254" height="30" rx="15" fill="#2ea043" fill-opacity=".14" stroke="#3fb950" stroke-opacity=".5"/>
<circle class="halo" cx="89" cy="77" r="5" fill="#3fb950"/>
<circle cx="89" cy="77" r="4.5" fill="#3fb950"/>
<text class="pill" x="105" y="81.6" textLength="200" lengthAdjust="spacingAndGlyphs">OPEN TO OPPORTUNITIES</text>
</g>
<g class="in i2"><text class="hi" x="70" y="146">Hi there, I'm</text></g>
<g class="in i3">
<text class="name" x="68" y="212" fill="url(#ng)" textLength="602" lengthAdjust="spacingAndGlyphs">Yousef Ali Mansour</text>
<rect x="70" y="232" width="96" height="4" rx="2" fill="url(#ng)"/>
</g>
<g class="in i4"><g class="ty" transform="translate(70 286)">
<text class="pr" x="0">&gt;</text>
{''.join(typed)}
<rect class="cur" x="{x0}" y="-21" width="12" height="27" rx="1.5" fill="{CYAN}">
<animate attributeName="x" dur="{n(T)}s" repeatCount="indefinite" calcMode="discrete" values="{cur_vals}" keyTimes="{cur_times}"/>
</rect>
</g></g>
<g class="in i5">
<path d="M80 327a6.2 6.2 0 0 1 6.2 6.2c0 4.6-6.2 10.3-6.2 10.3s-6.2-5.7-6.2-10.3A6.2 6.2 0 0 1 80 327zm0 3.9a2.3 2.3 0 1 0 0 4.6 2.3 2.3 0 0 0 0-4.6z" fill="{CYAN}" fill-rule="evenodd"/>
<text class="meta" x="96" y="341">Mansoura, Egypt</text>
<circle cx="236" cy="335.5" r="2" fill="#484f58"/>
<path d="M266 329l-11 5.2 11 5.2 11-5.2zM259.5 338.4v3.4c0 1.5 2.9 2.7 6.5 2.7s6.5-1.2 6.5-2.7v-3.4L266 341.5z" fill="{VIOLET}"/>
<text class="meta" x="286" y="341">Computer Science @ Mansoura University</text>
</g>
</g>
{card_border(W, H)}
</svg>
"""
    (OUT / "hero.svg").write_text(svg, encoding="utf-8")


# ----------------------------------------------------------------------- pipeline
def pipeline():
    W, H = 1200, 322
    nodes = [
        ("Clients", ["Web · Mobile", "Services"], CYAN),
        ("REST APIs", ["DRF · FastAPI", "ASP.NET Core"], BLUE),
        ("Apache Kafka", ["Event bus", "Pub/Sub topics"], VIOLET),
        ("Stream Workers", ["Flink · Celery", "Async jobs"], PINK),
        ("Data Layer", ["PostgreSQL · Redis", "SQL Server"], GREEN),
    ]
    NW, NH, GAP, X0, Y0 = 180, 114, 60, 30, 80
    P = 3.0
    arrive = [2.2, 0.8, 1.8, 2.8, 0.8]
    seg = [(0, 0.8), (1.0, 1.8), (2.0, 2.8), (0, 0.8)]
    edge_labels = ["HTTP", "publish", "consume", "persist"]
    ym = Y0 + NH / 2

    def packet(color, path, s, e):
        if s == 0:
            mot = f'keyPoints="0;1;1" keyTimes="0;{n(e / P, 4)};1"'
            op = f'values="1;0" keyTimes="0;{n(e / P, 4)}"'
        else:
            mot = f'keyPoints="0;0;1;1" keyTimes="0;{n(s / P, 4)};{n(e / P, 4)};1"'
            op = f'values="0;1;0" keyTimes="0;{n(s / P, 4)};{n(e / P, 4)}"'
        return (
            f'<circle r="4.6" fill="{color}" filter="url(#gl)" opacity="0">'
            f'<animateMotion dur="{P}s" repeatCount="indefinite" calcMode="linear" {mot} path="{path}"/>'
            f'<animate attributeName="opacity" dur="{P}s" repeatCount="indefinite" calcMode="discrete" {op}/></circle>'
        )

    parts = []
    for i, (title, subs, color) in enumerate(nodes):
        x = X0 + i * (NW + GAP)
        parts.append(
            f'<rect x="{x}" y="{Y0}" width="{NW}" height="{NH}" rx="14" fill="#111927" stroke="#2b3442" stroke-width="1.2"/>'
            f'<rect class="fl" x="{x}" y="{Y0}" width="{NW}" height="{NH}" rx="14" fill="{color}" fill-opacity=".1" '
            f'stroke="{color}" stroke-width="2" style="animation-delay:-{n(P - arrive[i])}s"/>'
            f'<rect x="{x + 18}" y="{Y0 + 18}" width="30" height="4" rx="2" fill="{color}"/>'
            f'<text class="num" x="{x + NW - 18}" y="{Y0 + 25}" text-anchor="end" fill="{color}">0{i + 1}</text>'
            f'<text class="tt" x="{x + 18}" y="{Y0 + 56}">{esc(title)}</text>'
            f'<text class="sb" x="{x + 18}" y="{Y0 + 80}">{esc(subs[0])}</text>'
            f'<text class="sb" x="{x + 18}" y="{Y0 + 100}">{esc(subs[1])}</text>'
        )
    for i in range(4):
        x1 = X0 + i * (NW + GAP) + NW
        x2 = x1 + GAP
        color = nodes[i][2]
        parts.append(
            f'<path class="ln" d="M{x1 + 5} {n(ym)}H{x2 - 9}"/>'
            f'<path d="M{x2 - 9} {n(ym - 4.5)}L{x2 - 1} {n(ym)}L{x2 - 9} {n(ym + 4.5)}Z" fill="#6e7681"/>'
            f'<text class="el" x="{n((x1 + x2) / 2)}" y="{n(ym - 12)}" text-anchor="middle">{edge_labels[i]}</text>'
            + packet(color, f"M{x1 + 2} {n(ym)}H{x2 - 4}", *seg[i])
        )
    # real-time path: workers -> clients
    xs = X0 + 3 * (NW + GAP) + NW / 2
    xe = X0 + NW / 2
    yb = Y0 + NH
    ret = f"M{n(xs)} {yb + 3}V{yb + 54}Q{n(xs)} {yb + 68} {n(xs - 14)} {yb + 68}H{n(xe + 14)}Q{n(xe)} {yb + 68} {n(xe)} {yb + 54}V{yb + 10}"
    parts.append(
        f'<path class="ln" d="{ret}"/>'
        f'<path d="M{n(xe - 4.5)} {yb + 10}L{n(xe)} {yb + 2}L{n(xe + 4.5)} {yb + 10}Z" fill="#6e7681"/>'
        f'<text class="el" x="{n((xs + xe) / 2)}" y="{yb + 90}" text-anchor="middle">real-time push · WebSockets + Redis pub/sub</text>'
        + packet(PINK, ret, 0, 2.2)
    )

    style = css(
        """
.tt{font:700 18.5px @SANS;fill:#e6edf3}
.sb{font:400 14.5px @SANS;fill:#9da7b3}
.num{font:700 13px @MONO;opacity:.85}
.el{font:500 13px @MONO;fill:#8b949e}
.hd{font:500 15px @MONO;fill:#8b949e}
.lv{font:600 13.5px @MONO;fill:#7ee787}
.ln{fill:none;stroke:#6e7681;stroke-width:1.5;stroke-dasharray:5 6;animation:march .9s linear infinite}
@keyframes march{to{stroke-dashoffset:-22}}
.fl{opacity:0;animation:flash 3s linear infinite}
@keyframes flash{0%{opacity:0}5%{opacity:1}34%{opacity:0}100%{opacity:0}}
.halo{transform-box:fill-box;transform-origin:center;animation:halo 1.8s ease-out infinite}
@keyframes halo{0%{transform:scale(.6);opacity:.7}100%{transform:scale(2.1);opacity:0}}
"""
        + REDUCED
    )
    label = (
        "Animated architecture diagram: clients call REST APIs (Django REST Framework, FastAPI, ASP.NET Core), "
        "which publish events to Apache Kafka; stream workers (Apache Flink, Celery) consume them, persist to "
        "PostgreSQL, Redis and SQL Server, and push real-time updates back to clients over WebSockets."
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
{card_defs(W, H)}
{GLOW}
</defs>
<style>{style}</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<text class="hd" x="32" y="46">// event-driven by design: one request, end to end</text>
<circle class="halo" cx="1040" cy="41" r="4.5" fill="#3fb950"/>
<circle cx="1040" cy="41" r="4" fill="#3fb950"/>
<text class="lv" x="1052" y="46">live event flow</text>
{''.join(parts)}
</g>
{card_border(W, H)}
</svg>
"""
    (OUT / "pipeline.svg").write_text(svg, encoding="utf-8")


# -------------------------------------------------------------------------- stack
def stack():
    W = 1200
    rows = [
        ("Languages", [
            ("Python", "python", "#4b9cd3"), ("C#", "txt:C#", "#b38cf5"), ("Go", "go", "#00add8"),
            ("TypeScript", "typescript", "#4a94e0"), ("JavaScript", "javascript", "#f7df1e"),
            ("C++", "cplusplus", "#659ad2"),
        ]),
        ("Backend", [
            ("Django", "django", "#44b78b"), ("Django REST", "dot", "#ff6b5e"), ("FastAPI", "fastapi", "#05c2ab"),
            ("ASP.NET Core", "dotnet", "#a78bfa"), ("WebSockets", "socketdotio", FG),
        ]),
        ("Events & Streaming", [
            ("Apache Kafka", "apachekafka", FG), ("Apache Flink", "apacheflink", "#e6526f"),
            ("Celery", "celery", "#6cc57c"), ("Redis", "redis", "#ff4438"),
        ]),
        ("Data", [
            ("PostgreSQL", "postgresql", "#7c9cf0"), ("SQL Server", "txt:SQL", "#f0635a"),
            ("SQLite", "sqlite", "#6cb6e8"),
        ]),
        ("Cloud & DevOps", [
            ("AWS", "txt:AWS", "#ff9900"), ("Docker", "docker", "#2496ed"), ("Linux", "linux", "#fcc624"),
            ("Git", "git", "#f05032"), ("GitHub Actions", "githubactions", "#4c9bff"),
        ]),
        ("AI Engineering", [
            ("RAG Pipelines", "dot", PINK), ("LLM Agents", "dot", VIOLET), ("Vector Search", "dot", CYAN),
        ]),
        ("Testing & UI", [
            ("Pytest", "pytest", "#0a9edc"), ("Postman", "postman", "#ff6c37"), ("React", "react", "#61dafb"),
            ("Next.js", "nextdotjs", FG),
        ]),
    ]
    RH, CH, TOP, CX0 = 60, 42, 30, 262
    H = TOP * 2 + (len(rows) - 1) * RH + CH
    parts = []
    names = []
    for ri, (cat, chips) in enumerate(rows):
        y = TOP + ri * RH
        ymid = y + CH / 2
        parts.append(f'<text class="cat" x="40" y="{n(ymid + 4.5)}">{esc(cat.upper())}</text>')
        if ri:
            parts.append(f'<path d="M40 {n(y - 9)}H{W - 40}" stroke="#21262d" stroke-width="1"/>')
        x = CX0
        for ci, (label, icon, color) in enumerate(chips):
            names.append(label)
            tw = text_w(label, 17, bold=True)
            w = 15 + 20 + 10 + tw + 17
            delay = 8 - (ci * 0.22 + ri * 0.5)
            g = [
                f'<rect x="{n(x)}" y="{y}" width="{n(w)}" height="{CH}" rx="10" fill="#161b22" stroke="#30363d"/>',
                f'<rect class="gw" x="{n(x)}" y="{y}" width="{n(w)}" height="{CH}" rx="10" fill="{color}" fill-opacity=".1" '
                f'stroke="{color}" stroke-width="1.5" style="animation-delay:-{n(delay)}s"/>',
            ]
            ix, iy = x + 15, y + (CH - 20) / 2
            if icon == "dot":
                g.append(f'<circle cx="{n(ix + 10)}" cy="{n(iy + 10)}" r="9" fill="{color}" opacity=".2"/>')
                g.append(f'<circle cx="{n(ix + 10)}" cy="{n(iy + 10)}" r="4.8" fill="{color}"/>')
            elif icon.startswith("txt:"):
                t = icon[4:]
                fs = 11.5 if len(t) <= 2 else 8.4
                g.append(f'<rect x="{n(ix - 1)}" y="{n(iy - 1)}" width="22" height="22" rx="5.5" fill="{color}" fill-opacity=".2"/>')
                g.append(
                    f'<text x="{n(ix + 10)}" y="{n(iy + 10 + fs * .36)}" text-anchor="middle" fill="{color}" '
                    f'style="font:800 {fs}px {SANS}">{esc(t)}</text>'
                )
            else:
                g.append(f'<path transform="translate({n(ix)} {n(iy)}) scale(.8333)" fill="{color}" d="{icon_path(icon)}"/>')
            g.append(f'<text class="lb" x="{n(x + 45)}" y="{n(ymid + 6)}">{esc(label)}</text>')
            parts.append("".join(g))
            x += w + 12
        assert x < W - 30, (cat, x)

    style = css(
        """
.cat{font:700 13px @MONO;fill:#8b949e;letter-spacing:1.4px}
.lb{font:600 17px @SANS;fill:#e6edf3}
.gw{opacity:0;animation:gw 8s linear infinite}
@keyframes gw{0%{opacity:0}3%{opacity:1}13%{opacity:0}100%{opacity:0}}
"""
        + REDUCED
    )
    label = "Tech stack: " + ", ".join(names) + "."
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
{card_defs(W, H)}
</defs>
<style>{style}</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{''.join(parts)}
</g>
{card_border(W, H)}
</svg>
"""
    (OUT / "stack.svg").write_text(svg, encoding="utf-8")


# ------------------------------------------------------------------------- footer
def footer():
    W, H = 1200, 170

    def wave(y, amp, wl):
        d = f"M0 {y}q{n(wl / 4)} {-amp} {n(wl / 2)} 0"
        d += f"t{n(wl / 2)} 0" * (int((W + wl) / (wl / 2)) + 1)
        return d + f"V{H + 10}H0Z"

    waves = [
        (118, 16, 600, 11, CYAN, 0.16),
        (128, 20, 800, 16, VIOLET, 0.2),
        (140, 12, 480, 8, PINK, 0.15),
    ]
    wsvg, wcss = [], []
    for i, (y, amp, wl, dur, color, op) in enumerate(waves):
        wsvg.append(f'<path class="w{i}" d="{wave(y, amp, wl)}" fill="{color}" opacity="{op}"/>')
        wcss.append(
            f".w{i}{{animation:w{i} {dur}s linear infinite}}"
            f"@keyframes w{i}{{to{{transform:translateX(-{wl}px)}}}}"
        )
    style = css(
        """
.q{font:600 23px @SANS}
.s{font:500 13px @MONO;fill:#7d8590}
"""
        + "".join(wcss)
        + REDUCED
    )
    label = "Building systems that scale, systems that stream, systems that last."
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
{card_defs(W, H)}
{name_gradient(260, 940, 6)}
</defs>
<style>{style}</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{''.join(wsvg)}
<text class="q" x="600" y="58" text-anchor="middle" fill="url(#ng)">{esc(label)}</text>
<text class="s" x="600" y="88" text-anchor="middle">thanks for stopping by · let's build something together</text>
</g>
{card_border(W, H)}
</svg>
"""
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


# ------------------------------------------------------------------------ buttons
def buttons():
    H = 46
    li = (
        '<rect x="0" y="0" width="20" height="20" rx="4.5" fill="#3b9bf5"/>'
        '<circle cx="5.6" cy="5.4" r="1.75" fill="#0d1117"/>'
        '<rect x="4.1" y="8.3" width="3" height="7.9" fill="#0d1117"/>'
        '<path d="M9.1 8.3h2.9v1.2c.5-.9 1.5-1.5 2.8-1.5 2.2 0 3.1 1.4 3.1 3.6v4.6h-3v-4.1c0-1-.4-1.6-1.3-1.6s-1.5.6-1.5 1.7v4h-3z" fill="#0d1117"/>'
    )
    mail = (
        '<rect x="1" y="3.5" width="18" height="13" rx="2.6" fill="none" stroke="#ff7b72" stroke-width="1.8"/>'
        '<path d="M2.2 5.4l7.8 5.7 7.8-5.7" fill="none" stroke="#ff7b72" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    leet = f'<path transform="scale(.8333)" fill="#ffa116" d="{icon_path("leetcode")}"/>'
    cv = (
        '<path d="M5 1.5h7l4 4V17a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 4 17V3A1.5 1.5 0 0 1 5.5 1.5z" fill="none" stroke="#34d399" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M7.3 10h5.4M7.3 13.4h5.4" stroke="#34d399" stroke-width="1.8" stroke-linecap="round"/>'
    )
    items = [
        ("btn-linkedin", "LinkedIn", "#3b9bf5", li),
        ("btn-email", "Email", "#ff7b72", mail),
        ("btn-leetcode", "LeetCode", "#ffa116", leet),
        ("btn-resume", "Résumé", "#34d399", cv),
    ]
    for i, (fname, label, color, icon) in enumerate(items):
        tw = text_w(label, 16, bold=True)
        W = round(18 + 20 + 11 + tw + 22)
        style = css(
            """
.t{font:700 16px @SANS;fill:#e6edf3}
.sh{animation:sh 4.8s ease-in-out infinite}
@keyframes sh{0%,55%{transform:translateX(-90px)}85%,100%{transform:translateX(%Wpx)}}
.bd{animation:bd 4.8s ease-in-out infinite}
@keyframes bd{0%,50%,100%{stroke-opacity:.45}75%{stroke-opacity:1}}
"""
            + REDUCED
        ).replace("%W", str(W + 40))
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
<clipPath id="c"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="11"/></clipPath>
<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>{style}</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="11" fill="#0d1117"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="11" fill="{color}" fill-opacity=".1"/>
<g clip-path="url(#c)"><rect class="sh" x="0" y="0" width="60" height="{H}" fill="url(#s)" transform="skewX(-18)" style="animation-delay:-{n(4.8 - i * 0.35)}s"/></g>
<rect class="bd" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="11" fill="none" stroke="{color}" stroke-width="1.5" style="animation-delay:-{n(4.8 - i * 0.35)}s"/>
<g transform="translate(18 13)">{icon}</g>
<text class="t" x="49" y="28.6">{esc(label)}</text>
</svg>
"""
        (OUT / f"{fname}.svg").write_text(svg, encoding="utf-8")


hero()
pipeline()
stack()
footer()
buttons()
for p in sorted(OUT.glob("*.svg")):
    print(f"{p.name:22s} {p.stat().st_size:7d} bytes")
