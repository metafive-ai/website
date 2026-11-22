# metafive.ai — site web

Site vitrine statique, une page, en français (`/`) et en anglais (`/en/`). Hébergé sur Cloudflare Pages.

## Structure

| Chemin | Rôle |
|---|---|
| `src/content.py` | **Tout le texte du site** (FR et EN), liens, liste des vidéos YouTube, textes de la page du calculateur |
| `src/courses.py` | Catalogue des formations (FR et EN) ; `PAGES` en fin de fichier donne l'adresse et le titre de recherche de chaque cours |
| `src/school.py` | Cours en écoles et universités |
| `src/build.py` | Génère `dist/` (24 pages, sitemap, `llms.txt`, données structurées schema.org) |
| `src/assets/` | CSS, JS (calculateur de la chaîne SLA → SLO → OLA, lecteur YouTube), polices IBM Plex Sans auto-hébergées, images |
| `src/static/` | Fichiers copiés tels quels : favicon, robots.txt, `_headers` (en-têtes de sécurité Cloudflare), 404 |
| `dist/` | Site généré, publié par Cloudflare Pages |

## Pages

| FR | EN | Contenu |
|---|---|---|
| `/` | `/en/` | Accueil : leadership, conseil, formation, lab, références |
| `/niveaux-de-service/` | `/en/service-levels/` | Calculateur SLA, SLO, OLA et budget d'erreur, avec les cinq formules |
| `/formations/` | `/en/training/` | Format, catalogue (une carte par cours), parcours, cours en écoles |
| `/formations/<cours>/` | `/en/training/<course>/` | Une page par cours (9 par langue) |

Ajouter un cours : l'ajouter à `courses` en FR et en EN dans `src/courses.py` avec le même `id`, puis à `PAGES`. La page, la carte du catalogue, le sitemap, `llms.txt` et les données structurées suivent. Une adresse publiée ne se renomme pas sans redirection (`src/static/_redirects`). Les anciens liens `/formations/#<id>` restent valables : ils mènent à la carte du cours.

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
- Les faits (dates, chiffres, certifications) viennent du dépôt privé `mlakhoua-rgb/personal` (ex-`cv`), qui est la source de vérité.
- Référencement : titres ≤ 60 caractères et descriptions ≤ 155 ; les données structurées et `llms.txt` sont générés à partir des mêmes textes que les pages et ne contiennent que des faits visibles sur le site (ni certification, ni prix, ni avis).

## Production (en service depuis le 2026-11-07)

- Cloudflare Pages, projet `metafive` (https://metafive.pages.dev), branche `main`, sans commande de build, dossier de sortie `dist`. Chaque push sur `main` est publié automatiquement : lancer `python3 src/build.py` et committer `dist/` avant de pousser.
- Domaine personnalisé : `www.metafive.ai` (actif, SSL) ; DNS chez Squarespace : `www` CNAME → `metafive.pages.dev`.
- `metafive.ai` → redirection permanente (301) vers `https://www.metafive.ai` (Squarespace Domain forwarding).
- MX et TXT Google Workspace inchangés.
- Application GitHub « Cloudflare Workers and Pages » installée sur l'organisation metafive-ai, limitée au repo `website`.
