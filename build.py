#!/usr/bin/env python3
"""Gerador do site talks4all.

Lê o conteúdo de content/ e escreve HTML estático, um conjunto de páginas por
idioma, na raiz do repositório (que é o que o GitHub Pages publica).

Uso: python3 build.py
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
FILES = ROOT / "files"

FONTS = (
    "https://fonts.googleapis.com/css2"
    "?family=Familjen+Grotesk:wght@400..700"
    "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..600"
    "&display=swap"
)


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def human_size(path: Path) -> str:
    if not path.exists():
        return ""
    size = path.stat().st_size
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB".replace(".", ",")
    return f"{size / 1024:.0f} KB"


def load_content() -> tuple[dict, list[dict]]:
    site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
    talks = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted((CONTENT / "talks").glob("*.json"))
    ]
    talks.sort(key=lambda t: t.get("order", 999))
    return site, talks


def head(site: dict, lang: str, title: str, description: str, path: str) -> str:
    """path é o caminho absoluto da página, com barra no fim."""
    locale = site["language_locales"][lang]
    url = site["url"] + path
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{site["language_locales"][code]}" '
        f'href="{site["url"]}{path.replace("/" + lang + "/", "/" + code + "/", 1)}">'
        for code in site["languages"]
    )
    return f"""<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{url}">
{alternates}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(site['name'])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:locale" content="{locale.replace('-', '_')}">
  <meta name="theme-color" content="#ffffff">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
"""


def masthead(site: dict, lang: str, path: str, t: dict) -> str:
    langs = []
    for code in site["languages"]:
        href = path.replace("/" + lang + "/", "/" + code + "/", 1)
        current = ' aria-current="true"' if code == lang else ""
        langs.append(
            f'<a href="{href}" lang="{site["language_locales"][code]}" '
            f'hreflang="{site["language_locales"][code]}"{current}>{code.upper()}</a>'
        )
    return f"""<a class="skip" href="#conteudo">{esc(t['skip_to_content'])}</a>
<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="wordmark" href="/{lang}/">talks<b>4</b>all</a>
    <nav class="langs" aria-label="{esc(t['language_heading'])}">
      {''.join(langs)}
    </nav>
  </div>
</header>
"""


def footer(site: dict, t: dict) -> str:
    speaker = site["speaker"]
    links = " ".join(
        f'<a href="{esc(l["url"])}">{esc(l["label"])}</a>' for l in speaker["links"]
    )
    return f"""<footer class="foot">
  <div class="wrap foot__inner">
    <p>{esc(speaker['name'])}</p>
    <p><a href="mailto:{esc(speaker['email'])}">{esc(speaker['email'])}</a></p>
    <p>{links}</p>
  </div>
</footer>
<script src="/assets/js/lang.js"></script>
</body>
</html>
"""


def render_home(site: dict, talks: list[dict], lang: str) -> str:
    t = site["i18n"][lang]
    path = f"/{lang}/"
    out = [head(site, lang, f"{site['name']}: {t['talks_heading']}", t["site_description"], path)]
    out.append(masthead(site, lang, path, t))
    out.append('<main id="conteudo">\n<div class="wrap">\n')

    out.append(f"""  <div class="hero">
    <h1 class="hero__title rise">{esc(t['home_title'])}</h1>
    <p class="hero__lede rise">{esc(t['home_lede'])}</p>
  </div>
""")

    rows = []
    for talk in talks:
        c = talk["i18n"][lang]
        status = t["status_upcoming"] if talk.get("status") == "upcoming" else t["status_past"]
        rows.append(f"""    <li><a class="talk" href="/{lang}/{talk['slug']}/">
      <div>
        <p class="talk__event">{esc(c['event'])}</p>
        <h3 class="talk__title">{esc(c['title'])}</h3>
        <p class="talk__tagline">{esc(c['tagline'])}</p>
      </div>
      <p class="talk__aside"><span class="talk__year">{esc(talk.get('year', ''))}</span>{esc(status)}</p>
    </a></li>""")

    out.append(f"""  <section aria-labelledby="palestras">
    <h2 class="section-title" id="palestras">{esc(t['talks_heading'])}</h2>
    <ol class="talks">
{chr(10).join(rows)}
    </ol>
  </section>
""")

    contacts = [f'<li><a href="mailto:{esc(site["speaker"]["email"])}">{esc(site["speaker"]["email"])}</a></li>']
    contacts += [f'<li><a href="{esc(l["url"])}">{esc(l["label"])}</a></li>' for l in site["speaker"]["links"]]

    out.append(f"""  <section aria-labelledby="quem">
    <h2 class="section-title" id="quem">{esc(t['speaker_heading'])}</h2>
    <div class="about">
      <div class="prose"><p>{esc(t['speaker_bio'])}</p></div>
      <ul class="contact">
{chr(10).join('        ' + c for c in contacts)}
      </ul>
    </div>
  </section>
</div>
</main>
""")
    out.append(footer(site, t))
    return "".join(out)


def render_talk(site: dict, talk: dict, lang: str) -> str:
    t = site["i18n"][lang]
    c = talk["i18n"][lang]
    path = f"/{lang}/{talk['slug']}/"
    description = c["summary"][0]

    out = [head(site, lang, f"{c['title']}: {c['event']}", description, path)]
    out.append(masthead(site, lang, path, t))
    out.append('<main id="conteudo">\n<div class="wrap">\n')

    out.append(f"""  <a class="backlink" href="/{lang}/">{esc(t['back_to_talks'])}</a>
  <div class="talk-hero">
    <p class="talk-hero__event rise">{esc(c['event'])}</p>
    <h1 class="talk-hero__title rise">{esc(c['title'])}</h1>
    <p class="talk-hero__tagline rise">{esc(c['tagline'])}</p>
  </div>
""")

    meta_pairs = [
        (t["meta_when"], c.get("when")),
        (t["meta_where"], c.get("where")),
        (t["meta_format"], c.get("format")),
        (t["meta_audience"], c.get("audience")),
        (t["meta_host"], c.get("host")),
    ]
    meta = "\n".join(
        f"    <div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>"
        for label, value in meta_pairs
        if value
    )
    out.append(f'  <dl class="meta">\n{meta}\n  </dl>\n')

    paragraphs = "\n".join(f"      <p>{esc(p)}</p>" for p in c["summary"])
    out.append(f"""  <section aria-labelledby="sobre">
    <h2 class="section-title" id="sobre">{esc(t['about_heading'])}</h2>
    <div class="prose">
{paragraphs}
    </div>
  </section>
""")

    if c.get("numbers"):
        items = "\n".join(
            f'      <li><b>{esc(n["value"])}</b><span>{esc(n["label"])}</span></li>'
            for n in c["numbers"]
        )
        out.append(f"""  <section aria-labelledby="numeros">
    <h2 class="section-title" id="numeros">{esc(t['numbers_heading'])}</h2>
    <ul class="numbers">
{items}
    </ul>
  </section>
""")

    if c.get("outline"):
        items = "\n".join(
            f'      <li><div><h3>{esc(o["title"])}</h3><p>{esc(o["text"])}</p></div></li>'
            for o in c["outline"]
        )
        out.append(f"""  <section aria-labelledby="roteiro">
    <h2 class="section-title" id="roteiro">{esc(t['outline_heading'])}</h2>
    <ol class="outline">
{items}
    </ol>
  </section>
""")

    out.append("</div>\n")

    if c.get("takeaways"):
        items = "\n".join(f"        <li>{esc(x)}</li>" for x in c["takeaways"])
        out.append(f"""<div class="takeaways-band">
  <section class="wrap" aria-labelledby="leva">
    <h2 class="section-title" id="leva">{esc(t['takeaways_heading'])}</h2>
    <ul class="takeaways">
{items}
    </ul>
  </section>
</div>
""")

    out.append('<div class="wrap">\n')

    if talk.get("downloads"):
        rows = []
        for d in talk["downloads"]:
            size = human_size(FILES / d["file"])
            rows.append(
                f'      <li><a href="/files/{esc(d["file"])}" download>'
                f'<span class="fmt">{esc(d["format"])}</span>'
                f'<span>{esc(d["label"][lang])}</span>'
                f'<span class="size">{esc(size)}</span></a></li>'
            )
        out.append(f"""  <section aria-labelledby="materiais">
    <h2 class="section-title" id="materiais">{esc(t['downloads_heading'])}</h2>
    <ul class="files">
{chr(10).join(rows)}
    </ul>
  </section>
""")

    if talk.get("resources"):
        rows = "\n".join(
            f'      <li><a href="{esc(r["url"])}" rel="noopener">{esc(r["name"])}</a>'
            f'<p>{esc(r["note"][lang])}</p></li>'
            for r in talk["resources"]
        )
        out.append(f"""  <section aria-labelledby="recursos">
    <h2 class="section-title" id="recursos">{esc(t['resources_heading'])}</h2>
    <ul class="links">
{rows}
    </ul>
  </section>
""")

    out.append("</div>\n</main>\n")
    out.append(footer(site, t))
    return "".join(out)


def render_gate(site: dict) -> str:
    """Página raiz: escolhe o idioma pelo navegador, com lista visível sem JS."""
    links = "\n".join(
        f'    <li><a href="/{code}/" lang="{site["language_locales"][code]}">'
        f'{esc(site["language_names"][code])}</a></li>'
        for code in site["languages"]
    )
    supported = ", ".join(f'"{code}"' for code in site["languages"])
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(site['name'])}</title>
  <meta name="description" content="{esc(site['i18n']['pt']['site_description'])}">
  <link rel="canonical" href="{site['url']}/pt/">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="/assets/css/site.css">
  <script>
    (function () {{
      var supported = [{supported}];
      var stored = null;
      try {{ stored = localStorage.getItem("talks4all:lang"); }} catch (e) {{}}
      var wanted = [stored].concat(navigator.languages || [navigator.language || ""]);
      for (var i = 0; i < wanted.length; i++) {{
        var code = String(wanted[i] || "").slice(0, 2).toLowerCase();
        if (supported.indexOf(code) !== -1) {{ location.replace("/" + code + "/"); return; }}
      }}
      location.replace("/{site['default_language']}/");
    }})();
  </script>
</head>
<body>
  <main class="gate">
    <h1 class="display">talks<b style="color:var(--gold-ink)">4</b>all</h1>
    <p>{esc(site['i18n']['pt']['choose_language'])}</p>
    <ul>
{links}
    </ul>
  </main>
</body>
</html>
"""


def render_404(site: dict) -> str:
    t = site["i18n"]["pt"]
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(t['not_found_title'])}</title>
  <meta name="robots" content="noindex">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
  <main class="gate">
    <h1 class="display">{esc(t['not_found_title'])}</h1>
    <p>{esc(t['not_found_text'])}</p>
    <ul><li><a href="/">{esc(t['not_found_link'])}</a></li></ul>
  </main>
</body>
</html>
"""


def render_sitemap(site: dict, talks: list[dict]) -> str:
    urls = [f"/{code}/" for code in site["languages"]]
    urls += [f"/{code}/{talk['slug']}/" for code in site["languages"] for talk in talks]
    entries = "\n".join(f"  <url><loc>{site['url']}{u}</loc></url>" for u in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("  ", path.relative_to(ROOT))


def main() -> None:
    site, talks = load_content()
    print(f"talks4all: {len(talks)} palestras, {len(site['languages'])} idiomas")

    for lang in site["languages"]:
        shutil.rmtree(ROOT / lang, ignore_errors=True)
        write(ROOT / lang / "index.html", render_home(site, talks, lang))
        for talk in talks:
            write(ROOT / lang / talk["slug"] / "index.html", render_talk(site, talk, lang))

    write(ROOT / "index.html", render_gate(site))
    write(ROOT / "404.html", render_404(site))
    write(ROOT / "sitemap.xml", render_sitemap(site, talks))
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    write(ROOT / ".nojekyll", "")


if __name__ == "__main__":
    main()
