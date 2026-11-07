#!/usr/bin/env python3
"""Build the static site into ../dist (FR at /, EN at /en/)."""
import html, math, os, shutil, datetime
import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(os.path.dirname(HERE), "dist")
e = html.escape
SLA_CHOICES = ["99.5", "99.9", "99.95", "99.99"]
DEFAULT_SLA = "99.9"


def pct(x, lang):
    digits = 4 if x >= 99.995 else 3
    s = f"{x:.{digits}f}".rstrip("0").rstrip(".")
    return (s.replace(".", ",") + " %") if lang == "fr" else s + "%"


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
    return dict(sla=pct(sla, lang), slo=pct(slo, lang), budget=dur(bs * 43200, lang),
                budget_year=dur(bs * 525600, lang), ola=pct(math.pow(slo / 100, 1 / 3) * 100, lang))


def sla_label(v, lang):
    return (v.replace(".", ",") + " %") if lang == "fr" else v + "%"


def page(T):
    lang = T["lang"]
    r = compute(float(DEFAULT_SLA), lang)
    values = {"sla": r["sla"], "slo": r["slo"],
              "budget": f'{r["budget"]}<small>{e(T["per_month"])}</small>',
              "ola": r["ola"], "sli": "≥ " + r["slo"], "cap": "&gt; " + r["slo"]}
    canonical = C.SITE + T["path"]
    alt = C.SITE + T["other_path"]

    nav = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in T["nav"])
    seg = "".join(
        f'<input type="radio" name="sla" id="sla-{v.replace(".", "-")}" value="{v}"{" checked" if v == DEFAULT_SLA else ""}>'
        f'<label for="sla-{v.replace(".", "-")}">{sla_label(v, lang)}</label>' for v in SLA_CHOICES)
    rows = ""
    for k, name, desc in T["panel_rows"]:
        extra = f' {e(T["so"])} <span data-budget-year>{e(r["budget_year"])} {e(T["per_year"])}</span>.' if k == "budget" else ""
        rows += (f'<li data-k="{k}"><span class="k">{e(name)}</span><span class="v" data-v="{k}">{values[k]}</span>'
                 f'<span class="d">{e(desc)}{extra}</span></li>')
    steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in T["steps"])
    offers = "".join(f'<div class="offer"><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["offers"])
    modules = "".join(f"<li><strong>{e(a)}</strong><span>{e(b)}</span></li>" for a, b in T["modules"])
    proof = "".join(f"<li>{e(x)}</li>" for x in T["train_proof"])
    figures = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in T["figures"])
    envs = "".join(f"<li>{e(x)}</li>" for x in T["envs"])
    certs = "".join(f"<li>{e(x)}</li>" for x in T["certs"])
    about = "".join(f"<p>{e(x)}</p>" for x in T["about_p"])
    links = "".join(f'<a href="{e(u)}" rel="noopener">{e(t)}</a>' for t, u in T["about_links"])
    legal = "".join(f"<p>{e(x)}</p>" for x in T["legal"])

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
<title>{e(T["title"])}</title>
<meta name="description" content="{e(T["description"])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="{lang}" href="{canonical}">
<link rel="alternate" hreflang="{"en" if lang == "fr" else "fr"}" href="{alt}">
<link rel="alternate" hreflang="x-default" href="{C.SITE}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(T["title"])}">
<meta property="og:description" content="{e(T["description"])}">
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
  <a class="brand" href="{T["path"]}"><span class="brand-mark" aria-hidden="true"></span>Metafive<span class="brand-tld">.ai</span></a>
  <nav class="nav" aria-label="{"Sections" if lang == "en" else "Sections"}">{nav}</nav>
  <a class="lang" href="{T["other_path"]}" hreflang="{"en" if lang == "fr" else "fr"}" lang="{"en" if lang == "fr" else "fr"}" title="{e(T["other_name"])}">{T["other_label"]}</a>
  <a class="btn btn--small" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
</div></header>

<main id="main">
<section class="hero"><div class="wrap">
  <div>
    <h1>{e(T["hero_h1"])}</h1>
    <p class="hero-p">{e(T["hero_p"])}</p>
    <div class="hero-actions">
      <a class="btn" href="{C.CALENDLY}" rel="noopener">{e(T["cta_book"])}</a>
      <a class="btn btn--ghost" href="#chaine">{e(T["hero_cta2"])}</a>
    </div>
    <p class="sig"><img src="/assets/img/mohamed-ben-lakhoua.webp" alt="" width="52" height="52">{e(T["sig"])}</p>
  </div>
  <div class="panel" data-panel data-per-month="{e(T["per_month"])}" data-per-year="{e(T["per_year"])}">
    <h2 class="panel-title">{e(T["panel_title"])}</h2>
    <fieldset><legend>{e(T["panel_pick"])}</legend><div class="seg">{seg}</div></fieldset>
    <ol class="chain" aria-live="polite">{rows}</ol>
    <p class="panel-note">{e(T["panel_note"])}</p>
  </div>
</div></section>

<section class="section" id="chaine" aria-labelledby="chaine-h"><div class="wrap">
  <div class="section-head"><h2 id="chaine-h">{e(T["method_h2"])}</h2><p class="lead">{e(T["method_p"])}</p></div>
  <ol class="steps">{steps}</ol>
</div></section>

<section class="section" id="conseil" aria-labelledby="conseil-h"><div class="wrap">
  <div class="section-head"><h2 id="conseil-h">{e(T["consult_h2"])}</h2><p class="lead">{e(T["consult_intro"])}</p></div>
  <dl class="offers">{offers}</dl>
</div></section>

<section class="section" id="formation" aria-labelledby="formation-h"><div class="wrap">
  <div class="section-head"><h2 id="formation-h">{e(T["train_h2"])}</h2><p class="lead">{e(T["train_intro"])}</p></div>
  <div class="train">
    <ul class="modules">{modules}</ul>
    <aside class="proof"><h3>{e(T["train_proof_h3"])}</h3><ul>{proof}</ul></aside>
  </div>
</div></section>
{videos}
<section class="section" id="references" aria-labelledby="references-h"><div class="wrap">
  <div class="section-head"><h2 id="references-h">{e(T["refs_h2"])}</h2><p class="lead">{e(T["refs_intro"])}</p></div>
  <dl class="figures">{figures}</dl>
  <div class="refs-cols">
    <div><h3>{e(T["envs_h3"])}</h3><ul class="plain">{envs}</ul></div>
    <div><h3>{e(T["certs_h3"])}</h3><ul class="plain">{certs}</ul></div>
  </div>
</div></section>

<section class="section" id="apropos" aria-labelledby="apropos-h"><div class="wrap about">
  <picture><source srcset="/assets/img/mohamed-ben-lakhoua.webp" type="image/webp"><img src="/assets/img/mohamed-ben-lakhoua.jpg" alt="Mohamed Ben Lakhoua" width="640" height="640" loading="lazy"></picture>
  <div class="about-text"><h2 id="apropos-h">{e(T["about_h2"])}</h2><div style="margin-top:1.25rem">{about}</div><div class="links">{links}</div></div>
</div></section>
</main>

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


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(DIST, "assets"))
    shutil.copytree(os.path.join(HERE, "static"), DIST, dirs_exist_ok=True)
    for T in (C.FR, C.EN):
        out = os.path.join(DIST, T["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page(T))
    today = datetime.date.today().isoformat()
    open(os.path.join(DIST, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'<url><loc>{C.SITE}/</loc><lastmod>{today}</lastmod></url>\n'
        f'<url><loc>{C.SITE}/en/</loc><lastmod>{today}</lastmod></url>\n</urlset>\n')
    print("built", DIST)


if __name__ == "__main__":
    main()
