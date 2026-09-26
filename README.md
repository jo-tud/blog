# Blog

A minimal, hand-coded static blog. Markdown in, HTML out.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Build the site
python scripts/build.py

# Local preview with auto-rebuild (http://localhost:8000)
python scripts/serve.py
```

## Workflow

Drafts live outside this repo (in Obsidian) until they are ready. This repo is public, so anything committed here is readable by everyone, even posts marked `draft: true`.

1. Write the post in Obsidian.
2. When it's ready, copy it to `content/posts/YYYY-MM-DD-slug.md` and add the frontmatter below.
3. Put images in `static/images/`.
4. Preview locally with `python scripts/serve.py`.
5. Commit and push to `main` — the site is built and deployed automatically.

## Writing a post

```markdown
---
title: "Your Post Title"
date: 2026-03-15
categories: [technology, design]
description: "A short description."
---

Your article body here...
```

File naming: `YYYY-MM-DD-slug.md` — the date prefix is stripped from the URL.

Set `draft: true` in the frontmatter to keep a post off the built site (the file itself stays public in the repo).

See [WRITING.md](WRITING.md) for the full Markdown reference (images, code, footnotes, tables, …).

## Static pages

Pages like Impressum go in `content/pages/`:

```markdown
---
title: "Page Title"
slug: page-url-slug
---
```

Rendered at `/<slug>/` and linked in the footer automatically.

## Deploy

Push to GitHub with Pages enabled (Source: GitHub Actions). The included workflow builds and deploys automatically.

Optional repository variables (Settings → Secrets and variables → Actions → Variables):

| Variable | Default |
|---|---|
| `SITE_URL` | The GitHub Pages URL of this repo |
| `SITE_TITLE` | `Blog` |
| `SITE_SUBTITLE` | none (shown under the title, used as meta and RSS description) |
| `SITE_AUTHOR` | `Author` |

For local builds, the same keys can go in a `.env` file (not committed). Links are built from the path part of `SITE_URL` (e.g. `/blog`), so the site works both at a domain root and on a project page. `serve.py` always builds for `http://localhost:<port>`.

## Structure

```
content/posts/       ← Blog articles (markdown)
content/pages/       ← Static pages (markdown)
templates/           ← HTML templates (Jinja2)
static/images/       ← Images and assets
scripts/build.py     ← Static site generator
scripts/serve.py     ← Local dev server
WRITING.md           ← Markdown reference for posts
```
