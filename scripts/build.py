#!/usr/bin/env python3
"""Static site generator. Converts markdown posts to HTML."""

import hashlib
import os
import re
import shutil
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "posts"
PAGES_DIR = ROOT / "content" / "pages"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
SITE_DIR = ROOT / "site"

# Posts are in English unless the filename says otherwise: 2026-10-02-slug.de.md is the
# German version of 2026-10-02-slug.md and is served at /posts/2026/10/slug/de/.
DEFAULT_LANG = "en"
LANG_NAMES = {"en": "English", "de": "Deutsch", "fr": "Français", "es": "Español", "it": "Italiano"}
LABELS = {
    "en": {"revised": "revised", "epistemic": "epistemic status", "contents": "contents",
           "cite": "cite as", "bibtex": "bibtex"},
    "de": {"revised": "überarbeitet", "epistemic": "epistemischer Status", "contents": "Inhalt",
           "cite": "zitieren als", "bibtex": "bibtex"},
}


def load_config():
    """Load site config from environment or .env file."""
    env_path = ROOT / ".env"
    config = {
        "url": "http://localhost:8000",
        "title": "My Blog",
        "subtitle": "",
        "author": "Author",
        "repo": "https://github.com/jo-tud/blog",
    }
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip()
            if key == "SITE_URL":
                config["url"] = val.rstrip("/")
            elif key == "SITE_TITLE":
                config["title"] = val
            elif key == "SITE_SUBTITLE":
                config["subtitle"] = val
            elif key == "SITE_AUTHOR":
                config["author"] = val
    # Override from env vars
    config["url"] = os.environ.get("SITE_URL", config["url"]).rstrip("/")
    config["title"] = os.environ.get("SITE_TITLE", config["title"])
    config["subtitle"] = os.environ.get("SITE_SUBTITLE", config["subtitle"])
    config["author"] = os.environ.get("SITE_AUTHOR", config["author"])
    config["repo"] = os.environ.get("SITE_REPO", config["repo"]).rstrip("/")
    return config


def prefix_root_links(html, base_path):
    """Prefix root-relative links (href="/...", src="/...") with the site's base path.

    Needed when the site is served from a subpath, e.g. jo-tud.github.io/blog/.
    """
    if not base_path:
        return html
    return re.sub(r'((?:href|src)=")/(?!/)', rf"\g<1>{base_path}/", html)


def sparse_strip(seed, cols, rows=3, gap=10, r=1.2, cls="sparse"):
    """Inline SVG: a faint grid of dots with a single highlighted one (the "reward").

    The reward is derived from `seed`, so every post gets its own pattern. It never sits
    in the middle row or the middle third of the columns: a reward that shows up where
    you would expect it is not a sparse one.
    """
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16)
    candidates = [
        i for i in range(cols * rows)
        if not (rows % 2 and i // cols == rows // 2)
        and not (cols / 3 <= i % cols < 2 * cols / 3)
    ]
    hit = candidates[h % len(candidates)]
    w, ht = cols * gap, rows * gap
    dots = []
    for i in range(cols * rows):
        x, y = (i % cols) * gap + gap / 2, (i // cols) * gap + gap / 2
        mark = ' class="hit"' if i == hit else ""
        rad = r * 2.4 if i == hit else r
        dots.append(f'<circle cx="{x:g}" cy="{y:g}" r="{rad:g}"{mark}/>')
    return (f'<svg class="{cls}" viewBox="0 0 {w} {ht}" width="{w}" height="{ht}" '
            f'aria-hidden="true">{"".join(dots)}</svg>')


def footnotes_to_sidenotes(html):
    """Copy each footnote next to its reference as a sidenote.

    The footnote list at the end stays in place; CSS shows sidenotes on wide screens
    and the list on narrow ones.
    """
    notes = {}
    for num, body in re.findall(r'<li id="fn:([^"]+)">\s*(.*?)\s*</li>', html, re.DOTALL):
        body = re.sub(r'&#160;<a class="footnote-backref"[^>]*>.*?</a>', "", body)
        body = re.sub(r"</p>\s*<p>", "<br>", body)
        notes[num] = re.sub(r"</?p>", "", body).strip()

    def insert(m):
        num = m.group(1)
        if num not in notes:
            return m.group(0)
        return (f'{m.group(0)}<span class="sidenote"><span class="sn-num">{m.group(2)}</span> '
                f"{notes[num]}</span>")

    return re.sub(r'<sup id="fnref:([^"]+)"><a class="footnote-ref" href="[^"]*">([^<]*)</a></sup>',
                  insert, html)


def parse_post(filepath):
    """Parse a markdown file with YAML frontmatter."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return None
    meta = yaml.safe_load(match.group(1))
    body = match.group(2)

    # Parse date
    date = meta.get("date")
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    elif isinstance(date, datetime):
        pass
    else:
        date = datetime(date.year, date.month, date.day)

    # Language suffix in the filename (slug.de.md), overridable with `lang:`
    stem = filepath.stem
    lang = DEFAULT_LANG
    m = re.match(r"^(.*)\.([a-z]{2})$", stem)
    if m:
        stem, lang = m.group(1), m.group(2)
    lang = meta.get("lang", lang)

    # Generate slug from filename
    slug = stem
    # Strip date prefix if present (e.g., 2026-03-01-title -> title)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)

    # Convert markdown to HTML
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "footnotes",
            "toc",
            "smarty",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False},
            "toc": {"permalink": "¶", "permalink_class": "anchor", "permalink_title": "Link to this section"},
        },
    )
    html = md.convert(body)
    html = footnotes_to_sidenotes(html)

    # Wrap tables in scrollable container for mobile
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

    revised = meta.get("revised")
    if revised and not isinstance(revised, str):
        revised = revised.strftime("%Y-%m-%d")

    categories = meta.get("categories", [])
    if isinstance(categories, str):
        categories = [c.strip() for c in categories.split(",")]

    return {
        "title": meta.get("title", slug),
        "date": date,
        "date_str": date.strftime("%Y-%m-%d"),
        "rss_date": format_datetime(date),
        "year": date.strftime("%Y"),
        "month": date.strftime("%m"),
        "slug": slug,
        "description": meta.get("description", ""),
        "categories": categories,
        "html": html,
        "draft": meta.get("draft", False),
        # Optional reader-facing metadata; each is only shown when set
        "revised": revised,
        "epistemic": meta.get("epistemic"),
        "toc": md.toc if meta.get("toc") else "",
        "source": filepath.name,
        "key": stem,
        "lang": lang,
        "lang_name": LANG_NAMES.get(lang, lang),
        "motif": sparse_strip(slug, cols=36, cls="sparse motif"),
    }


def build():
    """Build the static site."""
    config = load_config()

    # Clean output
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Copy static assets
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, SITE_DIR / "static")

    # Load and parse posts
    posts = []
    for f in CONTENT_DIR.glob("*.md"):
        post = parse_post(f)
        if post and not post["draft"]:
            posts.append(post)
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Group language versions of the same post. The English version (or, if there is
    # none, the first one) is the primary: it gets the plain URL and is the one listed.
    groups = {}
    for post in posts:
        groups.setdefault(post["key"], []).append(post)
    for versions in groups.values():
        versions.sort(key=lambda p: (p["lang"] != DEFAULT_LANG, p["lang"]))
        primary = versions[0]
        base = f"posts/{primary['year']}/{primary['month']}/{primary['slug']}/"
        for v in versions:
            v["path"] = base if v is primary else f"{base}{v['lang']}/"
            v["versions"] = versions
    translations = posts
    posts = [p for p in posts if p is p["versions"][0]]

    # Collect all categories
    all_categories = sorted({cat for post in posts for cat in post["categories"]})

    # Parse static pages (impressum, about, etc.)
    pages = []
    if PAGES_DIR.exists():
        md_parser = markdown.Markdown(
            extensions=["fenced_code", "tables", "smarty"],
        )
        for f in sorted(PAGES_DIR.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
            if not match:
                continue
            meta = yaml.safe_load(match.group(1))
            md_parser.reset()
            pages.append({
                "title": meta.get("title", f.stem),
                "slug": meta.get("slug", f.stem),
                # nav: false keeps a page out of the header (e.g. Impressum: footer only)
                "nav": meta.get("nav", True),
                "lang": meta.get("lang", DEFAULT_LANG),
                "html": md_parser.convert(match.group(2)),
            })

    # Set up Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    # Links use the URL's path as base ("" at a domain root, "/blog" on a project page);
    # the full URL is only needed for RSS and canonical links
    base_path = urlparse(config["url"]).path.rstrip("/")
    for item in translations + pages:
        item["html"] = prefix_root_links(item["html"], base_path)
    site = {"url": base_path, "absolute_url": config["url"], "title": config["title"], "subtitle": config["subtitle"], "author": config["author"],
            "repo": config["repo"], "mark": sparse_strip(config["title"], cols=5, gap=8, r=1.5)}
    common = {"site": site, "categories": all_categories, "pages": pages}

    # Generate index
    tpl = env.get_template("index.html")
    html = tpl.render(posts=posts, **common)
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")

    # Generate individual posts
    tpl = env.get_template("post.html")
    for post in translations:
        post_dir = SITE_DIR / post["path"]
        post_dir.mkdir(parents=True, exist_ok=True)
        html = tpl.render(
            post=post,
            lang=post["lang"],
            t=LABELS.get(post["lang"], LABELS[DEFAULT_LANG]),
            canonical_url=f"{config['url'].rstrip('/')}/{post['path']}",
            **common,
        )
        (post_dir / "index.html").write_text(html, encoding="utf-8")

    # Generate category pages
    tpl = env.get_template("category.html")
    for cat in all_categories:
        cat_posts = [p for p in posts if cat in p["categories"]]
        cat_dir = SITE_DIR / "categories" / cat.lower()
        cat_dir.mkdir(parents=True, exist_ok=True)
        html = tpl.render(
            category=cat,
            posts=cat_posts,
            active_category=cat,
            **common,
        )
        (cat_dir / "index.html").write_text(html, encoding="utf-8")

    # Generate static pages
    tpl = env.get_template("page.html")
    for page in pages:
        page_dir = SITE_DIR / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        html = tpl.render(page=page, lang=page["lang"], **common)
        (page_dir / "index.html").write_text(html, encoding="utf-8")

    # Generate RSS feed
    tpl = env.get_template("feed.xml")
    xml = tpl.render(posts=posts[:20], **common)
    (SITE_DIR / "feed.xml").write_text(xml, encoding="utf-8")

    # Generate Pygments CSS for code highlighting
    light_css = HtmlFormatter(style="default").get_style_defs(".highlight")
    dark_css = HtmlFormatter(style="monokai").get_style_defs("[data-theme='dark'] .highlight")
    auto_dark_css = HtmlFormatter(style="monokai").get_style_defs(":root:not([data-theme='light']) .highlight")
    highlight_css = (
        f"{light_css}\n\n"
        f"@media (prefers-color-scheme: dark) {{\n{auto_dark_css}\n}}\n\n"
        f"{dark_css}\n"
    )
    (SITE_DIR / "highlight.css").write_text(highlight_css, encoding="utf-8")

    print(f"Built {len(posts)} posts, {len(all_categories)} categories")
    print(f"Output: {SITE_DIR}")


if __name__ == "__main__":
    build()
