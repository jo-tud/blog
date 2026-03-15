#!/usr/bin/env python3
"""Static site generator. Converts markdown posts to HTML."""

import os
import re
import shutil
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

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


def load_config():
    """Load site config from environment or .env file."""
    env_path = ROOT / ".env"
    config = {
        "url": "https://example.github.io/jpblog",
        "title": "My Blog",
        "author": "Author",
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
            elif key == "SITE_AUTHOR":
                config["author"] = val
    # Override from env vars
    config["url"] = os.environ.get("SITE_URL", config["url"]).rstrip("/")
    config["title"] = os.environ.get("SITE_TITLE", config["title"])
    config["author"] = os.environ.get("SITE_AUTHOR", config["author"])
    return config


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

    # Generate slug from filename
    slug = filepath.stem
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
        },
    )
    html = md.convert(body)

    # Wrap tables in scrollable container for mobile
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

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
                "html": md_parser.convert(match.group(2)),
            })

    # Set up Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    # Use empty base path for links (root-relative) — full URL only needed for RSS
    site = {"url": "", "absolute_url": config["url"], "title": config["title"], "author": config["author"]}
    common = {"site": site, "categories": all_categories, "pages": pages}

    # Generate index
    tpl = env.get_template("index.html")
    html = tpl.render(posts=posts, **common)
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")

    # Generate individual posts
    tpl = env.get_template("post.html")
    for post in posts:
        post_dir = SITE_DIR / "posts" / post["year"] / post["month"] / post["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        html = tpl.render(
            post=post,
            canonical_url=f"{config['url'].rstrip('/')}/posts/{post['year']}/{post['month']}/{post['slug']}/",
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
        html = tpl.render(page=page, **common)
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
