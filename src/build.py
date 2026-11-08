#!/usr/bin/env python3
"""Build the static site into ../dist (FR at /, EN at /en/)."""
import html, math, os, shutil, datetime
import content as C
import courses as K
import school as S

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


def shell(T, path, other_path, title, description, body, active=""):
    """Common <head>, header, contact and footer for every page."""
    legal = "".join(f"<p>{e(x)}</p>" for x in T["legal"])
    lang = T["lang"]
    home = T["path"]
    canonical = C.SITE + path
    alt = C.SITE + other_path
    nav = "".join(
        f'<a href="{(h if path == home or not h.startswith("#") else home + h)}"'
        f'{" aria-current=\"page\"" if h == active else ""}>{e(t)}</a>' for h, t in T["nav"])
    ld = ('{"@context":"https://schema.org","@type":"ProfessionalService","name":"Metafive.ai",'
          f'"url":"{C.SITE}","email":"{C.EMAIL}","areaServed":"FR",'
          '"address":{"@type":"PostalAddress","addressLocality":"Courbevoie","addressCountry":"FR"},'
          '"founder":{"@type":"Person","name":"Mohamed Ben Lakhoua","jobTitle":"Infrastructure & Cloud Architect",'
          f'"sameAs":["{C.LINKEDIN}","{C.GITHUB}"]}}}}')
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
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{C.SITE}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14212B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/ibm-plex-sans-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
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
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def page(T):
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
    ai_steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in T["ai_steps"])
    ai_guard = "".join(f"<li>{e(x)}</li>" for x in T["ai_guard"])

    seg = "".join(
        f'<input type="radio" name="sla" id="sla-{v.replace(".", "-")}" value="{v}"{" checked" if v == DEFAULT_SLA else ""}>'
        f'<label for="sla-{v.replace(".", "-")}">{sla_label(v, lang)}</label>' for v in SLA_CHOICES)
    rows = ""
    for k, name, desc in T["panel_rows"]:
        extra = f' {e(T["so"])} <span data-budget-year>{e(r["budget_year"])} {e(T["per_year"])}</span>.' if k == "budget" else ""
        rows += (f'<li data-k="{k}"><span class="k">{e(name)}</span><span class="v" data-v="{k}">{values[k]}</span>'
                 f'<span class="d">{e(desc)}{extra}</span></li>')
    steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in T["steps"])
    domains = "".join(
        f'<article class="domain"><h3>{e(a)}</h3><p class="domain-p">{e(b)}</p>'
        f'<ul class="domain-list">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"
        f'<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in tags) + "</ul></article>"
        for a, b, items, tags in T["domains"])
    KT = K.FR if lang == "fr" else K.EN
    ST = S.FR if lang == "fr" else S.EN
    modules = "".join(
        f'<li><a href="{KT["path"]}#{c["id"]}"><span class="m-h"><strong>{e(c["title"])}</strong><em>{e(c["duration"])}</em></span>'
        f'<span>{e(c["tagline"])}</span></a></li>' for c in KT["courses"])
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
        f'<a class="door" href="{h}"><span class="door-k">{e(k)}</span><span class="door-t">{e(t)}</span></a>'
        for h, k, t in T["doors"])
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
<section class="hero"><div class="wrap">
  <div>
    <h1>{e(T["hero_h1"])}</h1>
    <p class="hero-p">{e(T["hero_p"])}</p>
    <div class="hero-actions">
      <a class="btn" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
      <a class="btn btn--ghost" href="#leadership">{e(T["hero_cta2"])}</a>
    </div>
    <p class="sig"><img src="/assets/img/mohamed-ben-lakhoua.webp" alt="" width="52" height="52">{e(T["sig"])}</p>
  </div>
  <div class="panel panel--proof">
    <h2 class="panel-title">{e(T["hero_panel_title"])}</h2>
    <dl class="proof-figures">{figures}</dl>
    <p class="panel-envs">{e(T["hero_panel_envs"])}</p>
  </div>
</div>
<div class="wrap doors-wrap"><nav class="doors" aria-label="{e(T["doors_label"])}">{doors}</nav></div>
</section>

<section class="section" id="leadership" aria-labelledby="leadership-h"><div class="wrap">
  <div class="section-head"><h2 id="leadership-h">{e(T["lead_h2"])}</h2><p class="lead">{e(T["lead_p"])}</p></div>
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
  <div class="lvl">
    <div class="panel" data-panel data-per-month="{e(T["per_month"])}" data-per-year="{e(T["per_year"])}">
      <h3 class="panel-title">{e(T["panel_title"])}</h3>
      <fieldset><legend>{e(T["panel_pick"])}</legend><div class="seg">{seg}</div></fieldset>
      <ol class="chain" aria-live="polite">{rows}</ol>
      <p class="panel-note">{e(T["panel_note"])}</p>
    </div>
    <div class="lvl-arch">
      <h3>{e(T["arch_h3"])}</h3><p class="lvl-sub">{e(T["arch_p"])}</p>
      <div class="arch">
        <div class="rail rail--up" aria-hidden="true"><span>{e(T["arch_up"])}</span></div>
        <div class="layers">{arch}</div>
        <div class="rail rail--down" aria-hidden="true"><span>{e(T["arch_down"])}</span></div>
      </div>
    </div>
  </div>
  <div class="calc">
    <div class="calc-head"><h3>{e(T["calc_h3"])}</h3><p>{e(T["calc_p"])} <strong class="lv" data-v="sla">{e(r["sla"])}</strong></p></div>
    <dl class="formulas">{calc}</dl>
  </div>
</div></section>

<section class="section section--ink" id="ia" aria-labelledby="ia-h"><div class="wrap">
  <div class="section-head"><p class="eyebrow eyebrow--ink">{e(T["eyebrow_conseil"])}</p><h2 id="ia-h">{e(T["ai_h2"])}</h2><p class="lead">{e(T["ai_p"])}</p></div>
  <ol class="steps steps--ink">{ai_steps}</ol>
  <div class="guard"><h3>{e(T["ai_guard_h3"])}</h3><ul>{ai_guard}</ul></div>
</div></section>

<section class="section" id="formation" aria-labelledby="formation-h"><div class="wrap">
  <div class="section-head"><h2 id="formation-h">{e(T["train_h2"])}</h2><p class="lead">{e(T["train_intro"])}</p></div>
  <div class="train">
    <div><ul class="modules">{modules}</ul>
    <p class="train-cta"><a class="btn" href="{KT["path"]}#entreprise">{e(T["train_cta"])}</a></p>
    <div class="school-teaser"><h3>{e(ST["home_h3"])}</h3><p>{e(ST["home_p"])}</p>
    <p><a class="btn btn--ghost" href="{KT["path"]}#cours">{e(ST["home_cta"])}</a></p></div></div>
    <aside class="proof"><h3>{e(T["train_proof_h3"])}</h3><ul>{proof}</ul></aside>
  </div>
</div></section>
{videos}
<section class="section section--tint" id="trading" aria-labelledby="trading-h"><div class="wrap">
  <div class="section-head"><h2 id="trading-h">{e(T["trading_h2"])}</h2><p class="lead">{e(T["trading_p"])}</p></div>
  <div class="tblocks">{tblocks}</div>
  <div class="tres"><h3>{e(T["trading_res_h3"])}</h3><p>{e(T["trading_res_p"])}</p>
    <dl class="fmt tres-k">{"".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["trading_res"])}</dl>
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


def course_page(T, KT):
    L = KT["labels"]
    fmt = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in KT["format"])
    index = "".join(f'<li><a href="#{c["id"]}">{e(c["title"])}</a><span>{e(c["duration"])}</span></li>' for c in KT["courses"])
    titles = {c["id"]: c["title"] for c in KT["courses"]}
    items = ""
    for c in KT["courses"]:
        prog = "".join(
            f'<div class="prog-part"><h4>{e(h)}</h4><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></div>"
            for h, xs in c["program"])
        ul = lambda xs: "<ul>" + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>"
        refs = "".join(f"<li>{e(x)}</li>" for x in c["refs"])
        items += f"""
<article class="course" id="{c["id"]}" aria-labelledby="{c["id"]}-h">
  <header class="course-head"><h2 id="{c["id"]}-h">{e(c["title"])}</h2><p>{e(c["tagline"])}</p>
    <div class="course-why"><span>{e(L["why"])}</span>{e(c["why"])}</div></header>
  <div class="course-body">
    <dl class="course-meta">
      <div><dt>{e(L["duration"])}</dt><dd class="course-dur">{e(c["duration"])}</dd></div>
      <div><dt>{e(L["audience"])}</dt><dd>{e(c["audience"])}</dd></div>
      <div><dt>{e(L["prereq"])}</dt><dd>{e(c["prereq"])}</dd></div>
      <div><dt>{e(L["refs"])}</dt><dd><ul class="tags">{refs}</ul></dd></div>
    </dl>
    <div class="course-main">
      <h3>{e(L["objectives"])}</h3>{ul(c["objectives"])}
      <h3>{e(L["program"])}</h3><div class="prog">{prog}</div>
      <div class="course-two">
        <div><h3>{e(L["labs"])}</h3>{ul(c["labs"])}</div>
        <div><h3>{e(L["deliverables"])}</h3>{ul(c["deliverables"])}</div>
      </div>
      <p class="course-top"><a href="#catalogue">{e(L["top"])}</a></p>
    </div>
  </div>
</article>"""
    paths = "".join(
        f'<div class="track"><h3>{e(name)}</h3><p>{e(desc)}</p><ol>'
        + "".join(f'<li><a href="#{i}">{e(titles[i])}</a></li>' for i in ids) + "</ol></div>"
        for name, desc, ids in KT["paths"])
    ST = S.FR if KT is K.FR else S.EN
    sdoors = "".join(
        f'<a class="door" href="{h}"><span class="door-k">{e(k)}</span><span class="door-t">{e(t)}</span></a>'
        for h, k, t in ST["doors"])
    how = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in ST["how"])
    groups = "".join(
        f'<article class="sgroup"><h4>{e(n)}</h4><p>{e(d)}</p><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></article>"
        for n, d, xs in ST["groups"])
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
  <ol class="cindex">{index}</ol>
</div></section>

<div class="wrap courses">{items}</div>

<section class="section" id="parcours" aria-labelledby="parcours-h"><div class="wrap">
  <div class="section-head"><h2 id="parcours-h">{e(KT["paths_h2"])}</h2><p class="lead">{e(KT["paths_intro"])}</p></div>
  <div class="tracks">{paths}</div>
</div></section>

<section class="section section--tint" id="cours" aria-labelledby="cours-h"><div class="wrap">
  <div class="section-head"><h2 id="cours-h">{e(ST["h2"])}</h2><p class="lead">{e(ST["intro"])}</p></div>
  <h3 class="h3-gap">{e(ST["how_h3"])}</h3>
  <dl class="fmt">{how}</dl>
  <h3 class="h3-gap">{e(ST["groups_h3"])}</h3>
  <div class="sgroups">{groups}</div>
  <p class="muted school-note">{e(ST["note"])}</p>
  <div class="school-cta"><h3>{e(ST["cta_h3"])}</h3><p>{e(ST["cta_p"])}</p>
    <p><a class="btn" href="mailto:{C.EMAIL}">{e(ST["cta_mail"])} {C.EMAIL}</a></p></div>
</div></section>
"""
    nav_active = KT["path"]
    return shell(T, KT["path"], KT["other_path"], KT["title"], KT["description"], body, active=nav_active)


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(DIST, "assets"))
    shutil.copytree(os.path.join(HERE, "static"), DIST, dirs_exist_ok=True)
    for T in (C.FR, C.EN):
        out = os.path.join(DIST, T["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page(T))
    for T, KT in ((C.FR, K.FR), (C.EN, K.EN)):
        out = os.path.join(DIST, KT["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(course_page(T, KT))
    today = datetime.date.today().isoformat()
    open(os.path.join(DIST, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'<url><loc>{C.SITE}/</loc><lastmod>{today}</lastmod></url>\n'
        f'<url><loc>{C.SITE}/en/</loc><lastmod>{today}</lastmod></url>\n'
        f'<url><loc>{C.SITE}{K.FR["path"]}</loc><lastmod>{today}</lastmod></url>\n'
        f'<url><loc>{C.SITE}{K.EN["path"]}</loc><lastmod>{today}</lastmod></url>\n</urlset>\n')
    print("built", DIST)


if __name__ == "__main__":
    main()
