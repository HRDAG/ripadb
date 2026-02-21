"""Render markdown articles to HTML fragments at build time."""

from pathlib import Path

import markdown
import yaml

CONTENT_DIR = Path(__file__).parent / "content"
ARTICLES_YAML = CONTENT_DIR / "articles.yaml"
RENDERED_DIR = CONTENT_DIR / "rendered"

EXTENSIONS = ["tables", "fenced_code", "toc", "smarty"]


def build():
    with open(ARTICLES_YAML) as f:
        meta = yaml.safe_load(f)

    RENDERED_DIR.mkdir(exist_ok=True)

    md = markdown.Markdown(extensions=EXTENSIONS)

    for article in meta["articles"]:
        src = CONTENT_DIR / article["file"]
        out = RENDERED_DIR / f"{article['slug']}.html"

        text = src.read_text()
        md.reset()
        html = md.convert(text)

        out.write_text(html)
        print(f"  {src.name} -> {out.name}")

    print(f"Rendered {len(meta['articles'])} article(s)")


if __name__ == "__main__":
    build()
