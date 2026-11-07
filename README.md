# metafive.ai — site web

Site vitrine statique, une page, en français (`/`) et en anglais (`/en/`). Hébergé sur Cloudflare Pages.

## Structure

| Chemin | Rôle |
|---|---|
| `src/content.py` | **Tout le texte du site** (FR et EN), liens, liste des vidéos YouTube |
| `src/build.py` | Génère `dist/` (pages FR et EN, sitemap) |
| `src/assets/` | CSS, JS (calculateur de la chaîne SLA → SLO → OLA, lecteur YouTube), polices IBM Plex Sans auto-hébergées, images |
| `src/static/` | Fichiers copiés tels quels : favicon, robots.txt, `_headers` (en-têtes de sécurité Cloudflare), 404 |
| `dist/` | Site généré, publié par Cloudflare Pages |

## Modifier le site

```bash
# 1. modifier src/content.py (ou le CSS/JS)
python3 src/build.py      # régénère dist/
git add -A && git commit -m "…" && git push   # Cloudflare redéploie automatiquement
```

## Ajouter une vidéo YouTube

Dans `src/content.py`, ajouter une entrée à `VIDEOS` :

```python
VIDEOS = [
    {"id": "dQw4w9WgXcQ", "title_fr": "Du SLI au SLO — épisode 1", "title_en": "From SLI to SLO — episode 1",
     "duration": "12 min", "thumb": "/assets/img/videos/ep1.jpg"},
]
```

La section « Vidéos » apparaît automatiquement. Rien n'est chargé depuis YouTube avant le clic du visiteur : les vidéos passent par youtube-nocookie.com, il n'y a donc pas besoin de bandeau cookies. La vignette (`thumb`) est une image locale, facultative.

## Cloudflare Pages

- Production branch : `main`
- Framework preset : None
- Build command : *(vide)*. `dist/` est versionné.
- Build output directory : `dist`

## DNS (le domaine reste chez son registrar actuel)

- `www` → CNAME vers `<projet>.pages.dev` (domaine personnalisé déclaré dans Cloudflare Pages)
- `metafive.ai` (apex) → redirection 301 vers `https://www.metafive.ai`
- **Ne pas toucher** aux enregistrements MX (`smtp.google.com`) ni TXT (SPF, google-site-verification) : ils portent la messagerie Google Workspace.

## Principes

- Aucun cookie, aucun outil de mesure d'audience, aucune ressource tierce chargée par défaut (RGPD).
- Les faits (dates, chiffres, certifications) viennent du dépôt privé `mlakhoua-rgb/cv`, qui est la source de vérité.

## Production (en service depuis le 2026-11-07)

- Cloudflare Pages, projet `metafive` (https://metafive.pages.dev), branche `main`, sans commande de build, dossier de sortie `dist`. Chaque push sur `main` est publié automatiquement : lancer `python3 src/build.py` et committer `dist/` avant de pousser.
- Domaine personnalisé : `www.metafive.ai` (actif, SSL) ; DNS chez Squarespace : `www` CNAME → `metafive.pages.dev`.
- `metafive.ai` → redirection permanente (301) vers `https://www.metafive.ai` (Squarespace Domain forwarding).
- MX et TXT Google Workspace inchangés.
- Application GitHub « Cloudflare Workers and Pages » installée sur l'organisation metafive-ai, limitée au repo `website`.
