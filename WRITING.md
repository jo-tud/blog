# Writing Guide

Reference for writing blog posts. All posts are markdown files in `content/posts/` with YAML frontmatter.

## Frontmatter

Every post starts with a YAML block:

```yaml
---
title: "Your Post Title"
date: 2026-03-15
categories: [technology, design]
description: "A short summary for RSS and meta tags."
draft: true
---
```

- **title** — displayed as the article heading and in the post list
- **date** — publication date (YYYY-MM-DD)
- **categories** — list of categories; new ones are created automatically
- **description** — optional, used in HTML meta and RSS
- **draft** — set to `true` to exclude from the built site

## Text formatting

```markdown
*italic text*
**bold text**
***bold italic***
~~strikethrough~~
```

## Headings

Use `##` for sections (H2) and `###` for subsections (H3). Don't use `#` (H1) — the post title is already H1.

```markdown
## Section heading

### Subsection heading
```

## Links

```markdown
[link text](https://example.com)
[another post](/posts/2026/03/the-architecture-of-good-defaults/)
```

Write internal links from the site root (`/posts/…`, `/static/…`). The build prefixes them with the site's base path, so they also work when the blog is served from a subpath like `jo-tud.github.io/blog/`.

## Images

Images go in `static/images/`. Reference them with a root-relative path:

```markdown
![Alt text describing the image](/static/images/my-diagram.png)
```

External images work too:

```markdown
![Alt text](https://example.com/photo.jpg)
```

An image alone in its own paragraph will be centered. Images are responsive and scale down on mobile.

## Code

Inline code uses single backticks:

```markdown
Use the `build.py` script to generate the site.
```

Code blocks use triple backticks with an optional language for syntax highlighting:

````markdown
```python
def hello():
    print("world")
```
````

Supported languages include `python`, `javascript`, `bash`, `go`, `rust`, `html`, `css`, `yaml`, `json`, `sql`, `typescript`, and [many more](https://pygments.org/languages/).

Code blocks scroll horizontally on mobile if they're too wide.

## Blockquotes

```markdown
> This is a blockquote. Use it for quotes,
> callouts, or to set aside a thought.
>
> Multiple paragraphs work too.
```

## Lists

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item
3. Third item
```

## Tables

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Row 1    | Data     | More     |
| Row 2    | Data     | More     |
```

Tables scroll horizontally on mobile and have alternating row colors.

## Horizontal rules

```markdown
---
```

A line with just `---` (after frontmatter) creates a horizontal rule.

## Footnotes

```markdown
This claim needs a source[^1].

[^1]: Here is the footnote text.
```

Footnotes are collected at the bottom of the article automatically.

## File naming

Post files follow the pattern `YYYY-MM-DD-slug.md`:

```
content/posts/2026-03-15-my-post-title.md
```

The date prefix is stripped from the URL slug. This post would be served at `/posts/2026/03/my-post-title/`.

## Static pages

Non-post pages (e.g. an Impressum) go in `content/pages/`:

```yaml
---
title: "Page Title"
slug: page-url-slug
---
```

They're rendered at `/<slug>/` and linked in the site footer automatically.
