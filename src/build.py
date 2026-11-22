#!/usr/bin/env python3
"""Build the static site into ../dist (FR at /, EN at /en/)."""
import html, json, math, os, re, shutil, datetime, hashlib
import content as C
import courses as K
import school as S
import trading_data as TD

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(os.path.dirname(HERE), "dist")
e = html.escape
SLA_CHOICES = ["99.5", "99.9", "99.95", "99.99"]
DEFAULT_SLA = "99.9"


def pct(x, lang):
    digits = 4 if x >= 99.995 else 3
    s = f"{x:.{digits}f}".rstrip("0").rstrip(".")
    return (s.replace(".", ",") + " %") if lang == "fr" else s + "%"


def pct_up(x, lang):
    """A required level is rounded up, never down."""
    digits = 4 if x >= 99.995 else 3
    f = 10 ** digits
    return pct(math.ceil(x * f - 1e-9) / f, lang)


def dur(minutes, lang):
    if minutes < 60:
        m = f"{minutes:.1f}" if minutes < 10 else str(round(minutes))
        return (m.replace(".", ",") if lang == "fr" else m) + " min"
    h = int(minutes // 60); r = round(minutes - h * 60)
    if r == 60: h, r = h + 1, 0
    return f"{h} h {r:02d}"


def compute(sla, lang):
    b = 1 - sla / 100
    slo = 100 - b * 50
    bs = 1 - slo / 100
    link = pct_up(math.pow(slo / 100, 1 / 4) * 100, lang)   # 3 OLA + 1 UC in series
    return dict(sla=pct(sla, lang), slo=pct(slo, lang), budget=dur(bs * 43200, lang),
                budget_year=dur(bs * 525600, lang), budget_sla=dur(b * 43200, lang),
                ola=link, uc=link, link=link)


def sla_label(v, lang):
    return (v.replace(".", ",") + " %") if lang == "fr" else v + "%"


ORG_ID = C.SITE + "/#org"
PERSON_ID = C.SITE + "/#mohamed-ben-lakhoua"
ORG_DESC = {
    "fr": ("Conseil et formation indépendants en architecture cloud et infrastructure, niveaux de service, "
           "résilience et conformité des plateformes critiques."),
    "en": ("Independent consulting and training in cloud and infrastructure architecture, service levels, "
           "resilience and compliance for critical platforms."),
}


def ld_json(lang, extra=()):
    """Structured data: the person, the business and the site, plus page-specific nodes.
    Only facts visible on the site go here. No certifications, ratings or prices."""
    graph = [
        {"@type": "Person", "@id": PERSON_ID, "name": "Mohamed Ben Lakhoua",
         "jobTitle": "Infrastructure & Cloud Architect", "url": C.SITE + "/",
         "image": C.SITE + "/assets/img/mohamed-ben-lakhoua.jpg",
         "worksFor": {"@id": ORG_ID}, "knowsLanguage": ["fr", "en", "ar"],
         "knowsAbout": ["Cloud architecture", "Service Level Management", "Site Reliability Engineering", "FinOps",
                        "Business continuity", "Digital Operational Resilience Act (DORA)"],
         "sameAs": [C.LINKEDIN, C.GITHUB]},
        {"@type": "ProfessionalService", "@id": ORG_ID, "name": "Metafive.ai", "url": C.SITE + "/",
         "description": ORG_DESC[lang], "image": C.SITE + "/assets/img/og.jpg", "email": C.EMAIL,
         "founder": {"@id": PERSON_ID},
         "address": {"@type": "PostalAddress", "addressLocality": "Courbevoie", "addressCountry": "FR"},
         "areaServed": "FR", "availableLanguage": ["fr", "en", "ar"],
         "sameAs": ["https://github.com/metafive-ai"]},
        {"@type": "WebSite", "@id": C.SITE + "/#website", "url": C.SITE + "/", "name": "Metafive.ai",
         "inLanguage": ["fr", "en"], "publisher": {"@id": ORG_ID}},
    ]
    graph.extend(extra)
    out = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return out.replace("</", "<\\/")


def iso_days(duration):
    """'2 jours' / '1 day' -> 'P2D' / 'P1D'."""
    return "P%dD" % int(re.search(r"\d+", duration).group(0))


def breadcrumb_ld(pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": C.SITE + p} for i, (n, p) in enumerate(pairs, start=1)]}


def course_ld(c, lang, url):
    """Course data for a course page. Every value is on the page: no price, no rating, no accreditation."""
    return {"@type": "Course", "@id": url + "#course", "name": c["title"], "description": c["tagline"],
            "inLanguage": lang, "url": url, "timeRequired": iso_days(c["duration"]),
            "audience": {"@type": "Audience", "audienceType": c["audience"]},
            "coursePrerequisites": c["prereq"], "teaches": c["objectives"],
            "provider": {"@id": ORG_ID},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": ["Onsite", "Online"],
                                  "instructor": {"@id": PERSON_ID}}}


def shell(T, path, other_path, title, description, body, active="", ld_extra=()):
    """Common <head>, header, contact and footer for every page."""
    legal = "".join(f"<p>{e(x)}</p>" for x in T["legal"])
    lang = T["lang"]
    home = T["path"]
    canonical = C.SITE + path
    alt = C.SITE + other_path
    nav = "".join(
        f'<a href="{(h if path == home or not h.startswith("#") else home + h)}"'
        f'{" aria-current=\"page\"" if h == active else ""}>{e(t)}</a>' for h, t in T["nav"])
    ld = ld_json(lang, ld_extra)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="{lang}" href="{canonical}">
<link rel="alternate" hreflang="{"en" if lang == "fr" else "fr"}" href="{alt}">
<link rel="alternate" hreflang="x-default" href="{canonical if lang == "fr" else alt}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Metafive.ai">
<meta property="og:locale" content="{"fr_FR" if lang == "fr" else "en_GB"}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{C.SITE}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14212B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/ibm-plex-sans-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={asset_v("site.css")}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{e(T["skip"])}</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{home}"><span class="brand-mark" aria-hidden="true"></span>Metafive<span class="brand-tld">.ai</span></a>
  <nav class="nav" aria-label="{"Sections" if lang == "en" else "Sections"}">{nav}</nav>
  <a class="lang" href="{other_path}" hreflang="{"en" if lang == "fr" else "fr"}" lang="{"en" if lang == "fr" else "fr"}" title="{e(T["other_name"])}">{T["other_label"]}</a>
  <a class="btn btn--small" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
</div></header>

<main id="main">{body}</main>

<section class="contact" id="contact" aria-labelledby="contact-h"><div class="wrap">
  <h2 id="contact-h">{e(T["contact_h2"])}</h2>
  <p>{e(T["contact_p"])}</p>
  <div class="hero-actions">
    <a class="btn btn--light" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
    <a class="btn btn--ghost" href="mailto:{C.EMAIL}">{e(T["contact_email_label"])} · {C.EMAIL}</a>
  </div>
  <p class="where">{e(T["contact_where"])}</p>
</div></section>

<footer class="foot"><div class="wrap">
  <span>{e(T["copyright"])}</span>
  <details><summary>{e(T["legal_summary"])}</summary>{legal}</details>
</div></footer>
<script src="/assets/site.js?v={asset_v("site.js")}" defer></script>
</body>
</html>
"""




def asset_v(name):
    """Content hash for cache busting: /assets/* is cached 7 days by browsers."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", name)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:10]

def _fmt(x, lang, d=0):
    t = f"{x:,.{d}f}"
    return t.replace(",", "\u202f").replace(".", ",") if lang == "fr" else t


def chart_replay(T):
    """Bars: R per year of the replayed book (R only)."""
    lang = T["lang"]
    W, H, l, r, t, b = 520, 250, 44, 12, 28, 34
    ys = [(y, round(n * a)) for y, n, a in TD.REPLAY_YEARS]
    top = 150
    sx = (W - l - r) / len(ys)
    sy = lambda v: t + (H - t - b) * (1 - v / top)
    g = []
    for v in range(0, top + 1, 50):
        g.append(f'<line class="ch-grid" stroke="#D5DCE1" x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>'
                 f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{v}</text>')
    for i, (y, v) in enumerate(ys):
        x = l + i * sx + sx * 0.2
        w = sx * 0.6
        lab = str(y) + ("*" if y == 2026 else "")
        g.append(f'<rect class="ch-bar" fill="#0E7C66" x="{x:.1f}" y="{sy(v):.1f}" width="{w:.1f}" height="{sy(0)-sy(v):.1f}" rx="3"/>'
                 f'<text class="ch-val" font-size="14" font-weight="600" fill="#14212B" x="{x+w/2:.1f}" y="{sy(v)-7:.1f}" text-anchor="middle">+{v} R</text>'
                 f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{x+w/2:.1f}" y="{H-b+20}" text-anchor="middle">{lab}</text>')
    g.append(f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{l}" y="14">R</text>')
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{e(T["chart_replay_aria"])}">'
            + "".join(g) + "</svg>")


def chart_demo(T):
    """Cumulative R of the closed demo trades, trade by trade."""
    lang = T["lang"]
    W, H, l, r, t, b = 520, 250, 44, 16, 28, 34
    pts, cum = [(None, 0.0, None)], 0.0
    for when, sym, d, rr in TD.DEMO_TRADES:
        cum += rr
        pts.append((when, cum, rr))
    lo, hi = -2, 10
    n = len(pts) - 1
    sx = lambda i: l + (W - l - r) * i / n
    sy = lambda v: t + (H - t - b) * (1 - (v - lo) / (hi - lo))
    mo = T["months"]
    g = []
    for v in range(lo, hi + 1, 2):
        cls = "ch-zero" if v == 0 else "ch-grid"
        g.append(f'<line class="{cls}" stroke="#D5DCE1" x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>'
                 f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{v:+d}</text>'.replace("+0<", "0<"))
    path = " ".join(f'{"M" if i == 0 else "L"}{sx(i):.1f},{sy(v):.1f}' for i, (_, v, _) in enumerate(pts))
    g.append(f'<path class="ch-line" fill="none" stroke="#0E7C66" stroke-width="2.5" d="{path}"/>')
    seen = set()
    for i, (when, v, rr) in enumerate(pts[1:], start=1):
        cls = "ch-dot ch-dot--neg" if rr < 0 else "ch-dot"
        g.append(f'<circle class="{cls}" fill="{"#B45309" if rr < 0 else "#0E7C66"}" cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="4.5"><title>{_fmt(rr, lang, 2)} R</title></circle>')
        day = when[:10]
        if day not in seen:
            seen.add(day)
            m, dd = int(day[5:7]), int(day[8:10])
            lab = f"{dd} {mo[m-1]}" if lang == "fr" else f"{mo[m-1]} {dd}"
            g.append(f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{sx(i):.1f}" y="{H-b+20}" text-anchor="middle">{lab}</text>')
    last = pts[-1][1]
    g.append(f'<text class="ch-val" font-size="14" font-weight="600" fill="#14212B" x="{sx(n)-6:.1f}" y="{sy(last)-10:.1f}" text-anchor="end">{"+" if last >= 0 else ""}{_fmt(last, lang, 1)} R</text>')
    g.append(f'<text class="ch-ax" font-size="14" fill="#5B6B78" x="{l}" y="14">R</text>')
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{e(T["chart_demo_aria"])}">'
            + "".join(g) + "</svg>")


def trading_charts(T):
    rtot = sum(round(n * a) for _, n, a in TD.REPLAY_YEARS)
    wins = sum(1 for *_, rr in TD.DEMO_TRADES if rr > 0)
    dsum = sum(rr for *_, rr in TD.DEMO_TRADES)
    demo_cap = T["chart_demo_cap"].format(n=len(TD.DEMO_TRADES), w=wins, r=("+" if dsum >= 0 else "") + _fmt(dsum, T["lang"], 1))
    return f"""<div class="tcharts">
    <figure class="tchart"><h4>{e(T["chart_replay_h"])}</h4>{chart_replay(T)}
      <figcaption>{e(T["chart_replay_cap"])}</figcaption></figure>
    <figure class="tchart"><h4>{e(T["chart_demo_h"])}</h4>{chart_demo(T)}
      <figcaption>{e(demo_cap)}</figcaption></figure>
  </div>"""

CALC_COURSES = ("sre-slo", "service-level-management", "slo-ia")  # courses that use the calculator


def module_li(c):
    """One course as a row: title, duration, tagline, linked to its own page."""
    return (f'<li><a href="{c["path"]}"><span class="m-h"><strong>{e(c["title"])}</strong><em>{e(c["duration"])}</em></span>'
            f'<span>{e(c["tagline"])}</span></a></li>')


def levels_parts(T, h="h3"):
    """The commitment chain calculator, shared by the home page and its own page.
    Returns (panel + architecture, formulas). h = heading level of the block titles."""
    lang = T["lang"]
    r = compute(float(DEFAULT_SLA), lang)
    values = {"sla": r["sla"], "slo": r["slo"],
              "budget": f'{r["budget"]}<small>{e(T["per_month"])}</small>',
              "ola": r["ola"], "uc": r["uc"], "sli": "≥ " + r["slo"], "cap": "&gt; " + r["slo"]}
    live = {"sla": r["sla"], "slo": r["slo"], "budget_plain": r["budget"], "budget_sla": r["budget_sla"], "link": r["link"]}

    def fill(tpl):
        out = e(tpl)
        for k, v in live.items():
            out = out.replace("{" + k + "}", f'<span class="lv" data-v="{k}">{e(v)}</span>')
        return out

    # architecture: commitments bottom-up, OLA and UC side by side
    L = T["arch_layers"]
    lv = {"SLA": ("sla", r["sla"]), "SLO": ("slo", r["slo"]), "OLA": ("ola", r["ola"]), "UC": ("uc", r["uc"]),
          "SLI": ("sli", "≥ " + r["slo"])}

    def layer(item, cls=""):
        tag, ab, desc = item
        k, v = lv.get(ab, (None, None))
        val = f'<span class="lv" data-v="{k}">{e(v)}</span>' if k else ""
        return (f'<div class="layer{cls}"><span class="layer-tag">{e(tag)}</span>'
                f'<span class="layer-ab">{e(ab)}{val}</span><p>{e(desc)}</p></div>')
    arch = (layer(L[0], " layer--top") + layer(L[1]) +
            f'<div class="layer-split">{layer(L[2])}{layer(L[3], " layer--uc")}</div>' +
            layer(L[4]) + layer(L[5], " layer--base"))
    calc = "".join(
        f'<div class="formula" id="f-{k}"><dt>{e(name)}</dt><dd><code>{e(f)}</code><p>{e(d)}</p>'
        f'<p class="ex"><span>{e(T["ex_label"])}</span>{fill(T["calc_ex"][k])}</p></dd></div>'
        for k, name, f, d in T["calc"])
    seg = "".join(
        f'<input type="radio" name="sla" id="sla-{v.replace(".", "-")}" value="{v}"{" checked" if v == DEFAULT_SLA else ""}>'
        f'<label for="sla-{v.replace(".", "-")}">{sla_label(v, lang)}</label>' for v in SLA_CHOICES)
    rows = ""
    for k, name, desc in T["panel_rows"]:
        extra = f' {e(T["so"])} <span data-budget-year>{e(r["budget_year"])} {e(T["per_year"])}</span>.' if k == "budget" else ""
        rows += (f'<li data-k="{k}"><span class="k">{e(name)}</span><span class="v" data-v="{k}">{values[k]}</span>'
                 f'<span class="d">{e(desc)}{extra}</span></li>')
    lvl = f"""<div class="lvl">
    <div class="panel" data-panel data-per-month="{e(T["per_month"])}" data-per-year="{e(T["per_year"])}">
      <{h} class="panel-title">{e(T["panel_title"])}</{h}>
      <fieldset><legend>{e(T["panel_pick"])}</legend><div class="seg">{seg}</div></fieldset>
      <ol class="chain" aria-live="polite">{rows}</ol>
      <p class="panel-note">{e(T["panel_note"])}</p>
    </div>
    <div class="lvl-arch">
      <{h}>{e(T["arch_h3"])}</{h}><p class="lvl-sub">{e(T["arch_p"])}</p>
      <div class="arch">
        <div class="rail rail--up" aria-hidden="true"><span>{e(T["arch_up"])}</span></div>
        <div class="layers">{arch}</div>
        <div class="rail rail--down" aria-hidden="true"><span>{e(T["arch_down"])}</span></div>
      </div>
    </div>
  </div>"""
    formulas = f"""<div class="calc">
    <div class="calc-head"><{h}>{e(T["calc_h3"])}</{h}><p>{e(T["calc_p"])} <strong class="lv" data-v="sla">{e(r["sla"])}</strong></p></div>
    <dl class="formulas">{calc}</dl>
  </div>"""
    return lvl, formulas


def page(T):
    lang = T["lang"]
    lvl, _ = levels_parts(T)
    ai_steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in T["ai_steps"])
    ai_guard = "".join(f"<li>{e(x)}</li>" for x in T["ai_guard"])
    steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in T["steps"])
    domains = "".join(
        f'<article class="domain"><h3>{e(a)}</h3><p class="domain-p">{e(b)}</p>'
        f'<ul class="domain-list">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"
        f'<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in tags) + "</ul></article>"
        for a, b, items, tags in T["domains"])
    KT = K.FR if lang == "fr" else K.EN
    ST = S.FR if lang == "fr" else S.EN
    modules = "".join(module_li(c) for c in KT["courses"])
    proof = "".join(f"<li>{e(x)}</li>" for x in T["train_proof"])
    figures = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["figures"])
    envs = "".join(f"<li>{e(x)}</li>" for x in T["envs"])
    certs = "".join(f"<li>{e(x)}</li>" for x in T["certs"])
    stds = "".join(f"<li>{e(x)}</li>" for x in T["stds"])
    why = "".join(
        f'<div class="why"><dt>{e(a)}</dt><dd><p>{e(b)}</p><ul class="tags">'
        + "".join(f"<li>{e(t)}</li>" for t in tags) + "</ul></dd></div>" for a, b, tags in T["why"])
    about = "".join(f"<p>{e(x)}</p>" for x in T["about_p"])
    links = "".join(f'<a href="{e(u)}" rel="noopener">{e(t)}</a>' for t, u in T["about_links"])

    videos = ""
    if C.VIDEOS:
        items = ""
        for v in C.VIDEOS:
            title = v["title_" + lang]
            thumb = f'<img src="{e(v["thumb"])}" alt="" loading="lazy">' if v.get("thumb") else ""
            items += (f'<figure class="video"><div class="video-frame">{thumb}'
                      f'<button class="video-play" type="button" data-yt="{e(v["id"])}" data-title="{e(title)}">'
                      f'<span>{e(T["video_play"])}</span></button></div>'
                      f'<figcaption>{e(title)}<small>{e(v.get("duration", ""))}</small></figcaption></figure>')
        videos = (f'<section class="section" id="videos" aria-labelledby="videos-h"><div class="wrap">'
                  f'<div class="section-head"><h2 id="videos-h">{e(T["videos_h2"])}</h2><p class="lead">{e(T["videos_intro"])}</p></div>'
                  f'<div class="videos">{items}</div><p class="video-consent">{e(T["video_consent"])}</p></div></section>')

    doors = "".join(
        f'<a class="door" href="{h}"><span class="door-n">0{i}</span><span class="door-k">{e(k)}</span><span class="door-t">{e(t)}</span></a>'
        for i, (h, k, t) in enumerate(T["doors"], start=1))
    kick = lambda i, label: f'<p class="kicker kicker--accent">0{i} · {e(label)}</p>'

    roles = "".join(f"<li>{e(x)}</li>" for x in T["lead_roles"])
    tl = "".join(
        f'<li class="tl-item"><span class="tl-when">{e(when)}</span><div class="tl-body"><h4>{e(role)}</h4>'
        f'<p class="tl-org">{e(org)}</p><p class="tl-ctx">{e(ctx)}</p><ul>' + "".join(f"<li>{e(x)}</li>" for x in pts) + "</ul></div></li>"
        for when, role, org, ctx, pts in T["lead_tl"])
    bring = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["lead_bring"])
    cnav = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in T["conseil_nav"])
    eb = f'<p class="eyebrow">{e(T["eyebrow_conseil"])}</p>'
    tblocks = "".join(
        f'<div class="tblock"><h3>{e(h)}</h3><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></div>"
        for h, xs in T["trading_blocks"])
    body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-text">
    <p class="kicker kicker--ink">{e(T["hero_eyebrow"])}</p>
    <h1>{e(T["hero_h1"])}</h1>
    <p class="hero-p">{e(T["hero_p"])}</p>
    <div class="hero-actions">
      <a class="btn btn--accent" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
      <a class="btn btn--line" href="#leadership">{e(T["hero_cta2"])}</a>
    </div>
  </div>
  <figure class="hero-photo">
    <picture><source srcset="/assets/img/mohamed-ben-lakhoua.webp" type="image/webp"><img src="/assets/img/mohamed-ben-lakhoua.jpg" alt="Mohamed Ben Lakhoua" width="640" height="640"></picture>
    <figcaption><strong>Mohamed Ben Lakhoua</strong><span>{e(T["hero_caption"])}</span></figcaption>
  </figure>
</div>
<div class="hero-figs"><dl class="wrap figs">{figures}</dl></div>
</section>

<section class="ways" aria-labelledby="ways-h"><div class="wrap">
  <h2 id="ways-h" class="kicker">{e(T["doors_label"])}</h2>
  <nav class="doors" aria-label="{e(T["doors_label"])}">{doors}</nav>
</div></section>

<section class="section" id="leadership" aria-labelledby="leadership-h"><div class="wrap">
  <div class="section-head">{kick(1, T["doors"][0][1])}<h2 id="leadership-h">{e(T["lead_h2"])}</h2><p class="lead">{e(T["lead_p"])}</p></div>
  <div class="roles"><h3>{e(T["lead_roles_h3"])}</h3><ul>{roles}</ul></div>
  <div class="lead-grid">
    <div><h3 class="sub-h">{e(T["lead_tl_h3"])}</h3><ol class="tl">{tl}</ol></div>
    <div class="bring"><h3 class="sub-h">{e(T["lead_bring_h3"])}</h3><dl>{bring}</dl>
      <p class="lead-note">{e(T["lead_note"])}</p>
      <div class="hero-actions"><a class="btn" href="{C.CALENDLY}" rel="noopener">{e(T["lead_cta"])}</a>
      <a class="btn btn--ghost" href="{C.LINKEDIN}" rel="noopener">{e(T["lead_cta2"])}</a></div>
    </div>
  </div>
</div></section>

<section class="chapter" id="conseil" aria-labelledby="conseil-h"><div class="wrap">
  {kick(2, T["doors"][1][1])}
  <h2 id="conseil-h">{e(T["conseil_h2"])}</h2>
  <p class="lead">{e(T["conseil_p"])}</p>
  <nav class="chapter-nav" aria-label="{e(T["conseil_h2"])}">{cnav}</nav>
</div></section>

<section class="section" id="contexte" aria-labelledby="contexte-h"><div class="wrap">
  <div class="section-head">{eb}<h2 id="contexte-h">{e(T["why_h2"])}</h2><p class="lead">{e(T["why_p"])}</p></div>
  <dl class="whys">{why}</dl>
</div></section>

<section class="section" id="architecture" aria-labelledby="architecture-h"><div class="wrap">
  <div class="section-head">{eb}<h2 id="architecture-h">{e(T["exp_h2"])}</h2><p class="lead">{e(T["exp_p"])}</p></div>
  <div class="domains">{domains}</div>
</div></section>

<section class="section" id="methode" aria-labelledby="methode-h"><div class="wrap">
  <div class="section-head">{eb}<h2 id="methode-h">{e(T["method_h2"])}</h2><p class="lead">{e(T["method_p"])}</p></div>
  <ol class="steps">{steps}</ol>
</div></section>

<section class="section section--tint" id="niveaux" aria-labelledby="niveaux-h"><div class="wrap">
  <div class="section-head">{eb}<h2 id="niveaux-h">{e(T["lvl_h2"])}</h2><p class="lead">{e(T["lvl_p"])}</p></div>
  {lvl}
  <p class="calc-more"><a class="btn btn--ghost" href="{T["levels_path"]}">{e(T["levels_link"])}</a><span>{e(T["levels_link_p"])}</span></p>
</div></section>

<section class="section section--ink" id="ia" aria-labelledby="ia-h"><div class="wrap">
  <div class="section-head"><p class="eyebrow eyebrow--ink">{e(T["eyebrow_conseil"])}</p><h2 id="ia-h">{e(T["ai_h2"])}</h2><p class="lead">{e(T["ai_p"])}</p></div>
  <ol class="steps steps--ink">{ai_steps}</ol>
  <div class="guard"><h3>{e(T["ai_guard_h3"])}</h3><ul>{ai_guard}</ul></div>
</div></section>

<section class="section" id="formation" aria-labelledby="formation-h"><div class="wrap">
  <div class="section-head">{kick(3, T["doors"][2][1])}<h2 id="formation-h">{e(T["train_h2"])}</h2><p class="lead">{e(T["train_intro"])}</p></div>
  <div class="train">
    <div><ul class="modules">{modules}</ul>
    <p class="train-cta"><a class="btn" href="{KT["path"]}#entreprise">{e(T["train_cta"])}</a></p>
    <div class="school-teaser"><h3>{e(ST["home_h3"])}</h3><p>{e(ST["home_p"])}</p>
    <p><a class="btn btn--ghost" href="{KT["path"]}#cours">{e(ST["home_cta"])}</a></p></div></div>
    <aside class="proof"><h3>{e(T["train_proof_h3"])}</h3><ul>{proof}</ul></aside>
  </div>
</div></section>
{videos}
<section class="section section--ink section--lab" id="trading" aria-labelledby="trading-h"><div class="wrap">
  <div class="section-head"><p class="kicker kicker--ink">04 · {e(T["lab_label"])}</p><h2 id="trading-h">{e(T["trading_h2"])}</h2><p class="lead">{e(T["trading_p"])}</p></div>
  <div class="tblocks">{tblocks}</div>
  <div class="tres"><h3>{e(T["trading_res_h3"])}</h3><p>{e(T["trading_res_p"])}</p>
    <dl class="fmt tres-k">{"".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["trading_res"])}</dl>
    {trading_charts(T)}
    <p class="tres-note">{e(T["trading_res_note"])}</p></div>
  <p class="trading-reuse">{e(T["trading_reuse"])} <a href="{e(T["AC"])}" rel="noopener">{e(T["trading_link"])}</a></p>
  <p class="disclaimer">{e(T["trading_disclaimer"])}</p>
</div></section>

<section class="section" id="references" aria-labelledby="references-h"><div class="wrap">
  <div class="section-head"><h2 id="references-h">{e(T["refs_h2"])}</h2><p class="lead">{e(T["refs_intro"])}</p></div>
  <div class="refs-cols">
    <div><h3>{e(T["envs_h3"])}</h3><ul class="plain">{envs}</ul></div>
    <div><h3>{e(T["certs_h3"])}</h3><ul class="plain">{certs}</ul>
      <h3 class="h3-gap">{e(T["stds_h3"])}</h3><ul class="plain">{stds}</ul></div>
  </div>
</div></section>

<section class="section" id="apropos" aria-labelledby="apropos-h"><div class="wrap about">
  <picture><source srcset="/assets/img/mohamed-ben-lakhoua.webp" type="image/webp"><img src="/assets/img/mohamed-ben-lakhoua.jpg" alt="Mohamed Ben Lakhoua" width="640" height="640" loading="lazy"></picture>
  <div class="about-text"><h2 id="apropos-h">{e(T["about_h2"])}</h2><div style="margin-top:1.25rem">{about}</div><div class="links">{links}</div></div>
</div></section>
"""
    return shell(T, T["path"], T["other_path"], T["title"], T["description"], body)


def course_title(c):
    """<title> of a course page: the search title, with the brand when it still fits in 60 characters."""
    t = c["seo"].format(d=c["duration"])
    return t + " | Metafive.ai" if len(t) + 14 <= 60 else t


def course_description(c, lang):
    """Meta description: the tagline, plus the format when it fits in 155 characters."""
    d = c["duration"]
    tails = ((f" Formation intra-entreprise de {d}.", f" Formation de {d}.") if lang == "fr"
             else (f" In-house training, {d}.", f" {d.split()[0]}-day course."))
    for tail in tails:
        if len(c["tagline"]) + len(tail) <= 155:
            return c["tagline"] + tail
    return c["tagline"]


def catalogue_page(T, KT):
    """Training index: format, one card per course (each links to its own page), tracks, courses for schools."""
    L = KT["labels"]
    lang = T["lang"]
    fmt = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in KT["format"])
    by_id = {c["id"]: c for c in KT["courses"]}
    # each card keeps the id the course had on this page, so older links to /formations/#<id> still land on it
    cards = "".join(
        f'<li class="ccard" id="{c["id"]}"><p class="ccard-dur">{e(c["duration"])}</p>'
        f'<h3><a href="{c["path"]}">{e(c["title"])}</a></h3><p class="ccard-tag">{e(c["tagline"])}</p>'
        f'<span class="ccard-more" aria-hidden="true">{e(L["see"])} →</span></li>' for c in KT["courses"])
    paths = "".join(
        f'<div class="track"><h3>{e(name)}</h3><p>{e(desc)}</p><ol>'
        + "".join(f'<li><a href="{by_id[i]["path"]}">{e(by_id[i]["title"])}</a></li>' for i in ids) + "</ol></div>"
        for name, desc, ids in KT["paths"])
    ST = S.FR if KT is K.FR else S.EN
    sdoors = "".join(
        f'<a class="door" href="{h}"><span class="door-k">{e(k)}</span><span class="door-t">{e(t)}</span></a>'
        for h, k, t in ST["doors"])
    how = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in ST["how"])
    groups = "".join(
        f'<article class="sgroup"><h4>{e(n)}</h4><p>{e(d)}</p><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></article>"
        for n, d, xs in ST["groups"])
    ex_parts = "".join(
        f'<article class="sgroup"><h4>{e(n)}</h4><p>{e(d)}</p><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></article>"
        for n, d, xs in ST["ex_parts"])
    ex_cases = "".join(f"<li>{e(x)}</li>" for x in ST["ex_cases"])
    teach = "".join(f"<li>{e(x)}</li>" for x in ST["teach"])
    body = f"""
<section class="page-hero"><div class="wrap">
  <p class="crumb"><a href="{T["path"]}">{e(KT["back"])}</a></p>
  <h1>{e(ST["page_h1"])}</h1>
  <p class="hero-p">{e(ST["page_intro"])}</p>
  <nav class="doors doors--2" aria-label="{e(ST["page_h1"])}">{sdoors}</nav>
</div></section>

<section class="section section--tint" id="entreprise" aria-labelledby="entreprise-h"><div class="wrap">
  <div class="section-head"><h2 id="entreprise-h">{e(ST["ent_h2"])}</h2><p class="lead">{e(KT["intro"])}</p></div>
  <dl class="fmt">{fmt}</dl>
  <div class="assess"><h3>{e(KT["assess_h3"])}</h3><p>{e(KT["assess"])}</p><p class="muted">{e(KT["note"])}</p></div>
</div></section>

<section class="section" id="catalogue" aria-labelledby="catalogue-h"><div class="wrap">
  <h2 id="catalogue-h">{e(KT["index_h2"])}</h2>
  <ol class="ccards">{cards}</ol>
</div></section>

<section class="section section--tint" id="parcours" aria-labelledby="parcours-h"><div class="wrap">
  <div class="section-head"><h2 id="parcours-h">{e(KT["paths_h2"])}</h2><p class="lead">{e(KT["paths_intro"])}</p></div>
  <div class="tracks">{paths}</div>
</div></section>

<section class="section" id="cours" aria-labelledby="cours-h"><div class="wrap">
  <div class="section-head"><h2 id="cours-h">{e(ST["h2"])}</h2><p class="lead">{e(ST["intro"])}</p></div>
  <h3 class="h3-gap">{e(ST["how_h3"])}</h3>
  <dl class="fmt">{how}</dl>
  <h3 class="h3-gap">{e(ST["groups_h3"])}</h3>
  <div class="sgroups">{groups}</div>
  <p class="muted school-note">{e(ST["note"])}</p>
  <h3 class="h3-gap" id="exemple">{e(ST["ex_h3"])}</h3>
  <p class="school-ex-intro">{e(ST["ex_intro"])}</p>
  <div class="sgroups">{ex_parts}</div>
  <div class="school-ex">
    <div><h4>{e(ST["ex_cases_h4"])}</h4><ul>{ex_cases}</ul></div>
    <div><h4>{e(ST["ex_method_h4"])}</h4><p>{e(ST["ex_method"])}</p></div>
  </div>
  <aside class="proof school-teach"><h3>{e(ST["teach_h3"])}</h3><ul>{teach}</ul></aside>
  <div class="school-cta"><h3>{e(ST["cta_h3"])}</h3><p>{e(ST["cta_p"])}</p>
    <p><a class="btn" href="mailto:{C.EMAIL}">{e(ST["cta_mail"])} {C.EMAIL}</a></p></div>
</div></section>
"""
    # summary page: the list points at the course pages, which carry the full Course data
    catalogue = {"@type": "ItemList", "name": KT["index_h2"], "numberOfItems": len(KT["courses"]),
                 "itemListElement": [
                     {"@type": "ListItem", "position": i, "name": c["title"], "url": C.SITE + c["path"]}
                     for i, c in enumerate(KT["courses"], start=1)]}
    crumbs = breadcrumb_ld([(T["home_label"], T["path"]), (ST["page_h1"], KT["path"])])
    return shell(T, KT["path"], KT["other_path"], KT["title"], KT["description"], body, active=KT["path"],
                 ld_extra=[catalogue, crumbs])


def course_page(T, KT, c):
    """One course on its own address: why, facts, objectives, programme, labs, deliverables, format, tracks."""
    L = KT["labels"]
    lang = T["lang"]
    ST = S.FR if KT is K.FR else S.EN
    OT = K.EN if KT is K.FR else K.FR
    other = next(x for x in OT["courses"] if x["id"] == c["id"])
    by_id = {x["id"]: x for x in KT["courses"]}
    ul = lambda xs: "<ul>" + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>"
    prog = "".join(
        f'<div class="prog-part"><h3>{e(h)}</h3>{ul(xs)}</div>' for h, xs in c["program"])
    refs = "".join(f"<li>{e(x)}</li>" for x in c["refs"])
    fmt = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in KT["format"])
    tracks = "".join(
        f'<div class="track"><h3>{e(name)}</h3><p>{e(desc)}</p><ol>'
        + "".join((f'<li><strong aria-current="page">{e(by_id[i]["title"])}</strong></li>' if i == c["id"]
                   else f'<li><a href="{by_id[i]["path"]}">{e(by_id[i]["title"])}</a></li>') for i in ids)
        + "</ol></div>"
        for name, desc, ids in KT["paths"] if c["id"] in ids)
    others = "".join(
        f'<li><a href="{x["path"]}">{e(x["title"])}</a><span>{e(x["duration"])}</span></li>'
        for x in KT["courses"] if x["id"] != c["id"])
    tool = ""
    if c["id"] in CALC_COURSES:
        tool = (f'<aside class="tool-link"><h2>{e(L["calc_h"])}</h2><p>{e(L["calc_p"])}</p>'
                f'<p><a class="btn btn--ghost" href="{T["levels_path"]}">{e(L["calc_cta"])}</a></p></aside>')
    body = f"""
<section class="page-hero page-hero--course"><div class="wrap">
  <nav class="crumb" aria-label="{e(L["crumbs"])}"><a href="{T["path"]}">{e(T["home_label"])}</a><span aria-hidden="true">›</span><a href="{KT["path"]}#catalogue">{e(ST["page_h1"])}</a></nav>
  <p class="kicker kicker--accent">{e(L["kicker"])} · {e(c["duration"])}</p>
  <h1>{e(c["title"])}</h1>
  <p class="hero-p">{e(c["tagline"])}</p>
  <div class="hero-actions">
    <a class="btn btn--accent" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
    <a class="btn btn--ghost" href="mailto:{C.EMAIL}">{e(T["contact_email_label"])} · {C.EMAIL}</a>
  </div>
</div></section>

<div class="wrap courses courses--page">
<article class="course" aria-labelledby="why-h">
  <header class="course-head"><h2 class="course-why-h" id="why-h">{e(L["why"])}</h2><p>{e(c["why"])}</p></header>
  <div class="course-body">
    <dl class="course-meta">
      <div><dt>{e(L["duration"])}</dt><dd class="course-dur">{e(c["duration"])}</dd></div>
      <div><dt>{e(L["audience"])}</dt><dd>{e(c["audience"])}</dd></div>
      <div><dt>{e(L["prereq"])}</dt><dd>{e(c["prereq"])}</dd></div>
      <div><dt>{e(L["refs"])}</dt><dd><ul class="tags">{refs}</ul></dd></div>
    </dl>
    <div class="course-main">
      <h2>{e(L["objectives"])}</h2>{ul(c["objectives"])}
      <h2>{e(L["program"])}</h2><div class="prog">{prog}</div>
      <div class="course-two">
        <div><h2>{e(L["labs"])}</h2>{ul(c["labs"])}</div>
        <div><h2>{e(L["deliverables"])}</h2>{ul(c["deliverables"])}</div>
      </div>
    </div>
  </div>
</article>
{tool}
</div>

<section class="section section--tint" id="format" aria-labelledby="format-h"><div class="wrap">
  <h2 id="format-h">{e(L["format"])}</h2>
  <dl class="fmt">{fmt}</dl>
  <div class="assess"><p>{e(KT["assess"])}</p><p class="muted">{e(KT["note"])}</p></div>
</div></section>

<section class="section" id="parcours" aria-labelledby="parcours-h"><div class="wrap">
  <div class="section-head"><h2 id="parcours-h">{e(KT["paths_h2"])}</h2><p class="lead">{e(KT["paths_one"])}</p></div>
  <div class="tracks">{tracks}</div>
</div></section>

<section class="section section--tint" id="autres" aria-labelledby="autres-h"><div class="wrap">
  <h2 id="autres-h">{e(L["others"])}</h2>
  <ol class="cindex">{others}</ol>
  <p class="course-top"><a href="{KT["path"]}#catalogue">{e(L["top"])}</a></p>
</div></section>
"""
    url = C.SITE + c["path"]
    crumbs = breadcrumb_ld([(T["home_label"], T["path"]), (ST["page_h1"], KT["path"]), (c["title"], c["path"])])
    return shell(T, c["path"], other["path"], course_title(c), course_description(c, lang), body, active=KT["path"],
                 ld_extra=[course_ld(c, lang, url), crumbs])


def levels_page(T):
    """The commitment chain calculator on its own address: panel, architecture, the five formulas."""
    lang = T["lang"]
    KT = K.FR if lang == "fr" else K.EN
    lvl, formulas = levels_parts(T, "h2")
    by_id = {c["id"]: c for c in KT["courses"]}
    related = "".join(module_li(by_id[i]) for i in CALC_COURSES)
    repo = next(t for t, u in T["about_links"] if u == C.GITHUB_SLM)
    body = f"""
<section class="page-hero"><div class="wrap">
  <p class="crumb"><a href="{T["path"]}">{e(KT["back"])}</a></p>
  <p class="kicker kicker--accent">{e(T["levels_kicker"])}</p>
  <h1>{e(T["levels_h1"])}</h1>
  <p class="hero-p">{e(T["levels_intro"])}</p>
</div></section>

<section class="section section--tint section--tool" id="calculateur"><div class="wrap">
  {lvl}
</div></section>

<section class="section section--tool" id="formules"><div class="wrap">
  {formulas}
</div></section>

<section class="section section--tint" id="formations" aria-labelledby="formations-h"><div class="wrap">
  <div class="section-head"><h2 id="formations-h">{e(T["levels_more_h2"])}</h2><p class="lead">{e(T["levels_more_p"])}</p></div>
  <ul class="modules modules--wide">{related}</ul>
  <div class="links"><a href="{C.GITHUB_SLM}" rel="noopener">{e(repo)}</a><a href="{T["path"]}#methode">{e(T["levels_method"])}</a></div>
</div></section>
"""
    url = C.SITE + T["levels_path"]
    app = {"@type": "WebApplication", "@id": url + "#calculator", "name": T["levels_h1"], "url": url,
           "description": T["levels_description"], "applicationCategory": "BusinessApplication",
           "operatingSystem": "Any", "isAccessibleForFree": True, "inLanguage": lang,
           "creator": {"@id": PERSON_ID}, "publisher": {"@id": ORG_ID}}
    crumbs = breadcrumb_ld([(T["home_label"], T["path"]), (T["levels_h1"], T["levels_path"])])
    return shell(T, T["levels_path"], T["levels_other_path"], T["levels_title"], T["levels_description"], body,
                 ld_extra=[app, crumbs])


def llms_txt():
    """Plain-language description of the site for AI assistants (llms.txt convention).
    Generated from the same data as the pages so it cannot drift. Facts only."""
    T, KT = C.EN, K.EN
    courses = "\n".join(f'- [{c["title"]}]({C.SITE}{c["path"]}): {c["duration"]}. {c["tagline"]}' for c in KT["courses"])
    fmt = " ".join(f"{b}" for _, b in KT["format"])
    track = "\n".join(f"- {when}: {role}, {org}. {ctx}" for when, role, org, ctx, _ in T["lead_tl"])
    return f"""# Metafive.ai — Mohamed Ben Lakhoua

> Infrastructure & Cloud Architect based in Paris – La Défense (Courbevoie, France). Thirty years leading, designing and hardening critical platforms in Tunisia, Qatar, the United Arab Emirates, Germany and France. Independent consulting and training under the name Metafive.ai. Works in French, English and Arabic.

## What I do
- Consulting: cloud and hybrid architecture; resilience and compliance (business continuity, DORA, ISO 22301, ISO/IEC 27001 audit preparation); Service Level Management and operational excellence (the SLI → SLO → OLA → UC → SLA chain, SRE, ITIL); AI automation of IT operations with human sign-off.
- In-house training: {len(KT["courses"])} courses for IT teams in the 2026 catalogue, 1 to 3 days each.
- Courses for schools and universities: Bachelor's and Master's modules on IT service governance, infrastructure design, project steering, security and compliance.
- Technology leadership: open to CTO, VP Engineering / VP Platform and Director Infrastructure & Cloud roles.
- Lab: Metafive 360°, a personal research project on governing several AI agents, with algorithmic trading as the test bed. No investment advice, no signals, no third-party asset management.

## Training catalogue 2026
{courses}

Format: {fmt} The courses do not prepare for official certification exams and are not legal advice. Prices are not published.

## Track record
{track}

## Where and how
{T["contact_where"]}

## Contact
- Email: {C.EMAIL}
- Book a 30-minute call: {C.CALENDLY}
- LinkedIn: {C.LINKEDIN}

## Key pages
- Home, French: {C.SITE}{C.FR["path"]}
- Home, English: {C.SITE}{C.EN["path"]}
- Training and courses, French: {C.SITE}{K.FR["path"]}
- Training and courses, English: {C.SITE}{K.EN["path"]}
- SLA, SLO, OLA and error budget calculator, French: {C.SITE}{C.FR["levels_path"]}
- SLA, SLO, OLA and error budget calculator, English: {C.SITE}{C.EN["levels_path"]}

Each course has its own page in English (linked above) and in French, under {C.SITE}{K.FR["path"]}

## Open source
- Service Level Management reference: {C.GITHUB_SLM}
- agent-constitution, governance of AI coding agents: {T["AC"]}
"""


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(DIST, "assets"))
    shutil.copytree(os.path.join(HERE, "static"), DIST, dirs_exist_ok=True)
    pages = []   # (path, html), in sitemap order
    for T in (C.FR, C.EN):
        pages.append((T["path"], page(T)))
    for T in (C.FR, C.EN):
        pages.append((T["levels_path"], levels_page(T)))
    for T, KT in ((C.FR, K.FR), (C.EN, K.EN)):
        pages.append((KT["path"], catalogue_page(T, KT)))
        pages.extend((c["path"], course_page(T, KT, c)) for c in KT["courses"])
    assert len({p for p, _ in pages}) == len(pages), "two pages share one address"
    for path, html_ in pages:
        out = os.path.join(DIST, path.strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(html_)
    today = datetime.date.today().isoformat()
    open(os.path.join(DIST, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f'<url><loc>{C.SITE}{path}</loc><lastmod>{today}</lastmod></url>\n' for path, _ in pages)
        + '</urlset>\n')
    open(os.path.join(DIST, "llms.txt"), "w", encoding="utf-8").write(llms_txt())
    print("built", DIST, "-", len(pages), "pages")


if __name__ == "__main__":
    main()
