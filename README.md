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

# Local preview with auto-rebuild
python scripts/serve.py
```

## Writing a post

Create a markdown file in `content/posts/`:

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

## Structure

```
content/posts/       ← Blog articles (markdown)
content/pages/       ← Static pages (markdown)
templates/           ← HTML templates (Jinja2)
static/images/       ← Images and assets
scripts/build.py     ← Static site generator
scripts/serve.py     ← Local dev server
```
