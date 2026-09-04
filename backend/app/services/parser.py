from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from uuid import uuid4
import json
from bs4 import BeautifulSoup
from app.schemas import Block, CanonicalDocument, Section, Statistics

NOISE = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"}

def _meta(soup: BeautifulSoup, *names: str) -> str | None:
    for name in names:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"): return tag["content"].strip()
    return None

def parse_source(url: str, final_url: str, raw: bytes) -> CanonicalDocument:
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup.find_all(NOISE): tag.decompose()
    title = _meta(soup, "og:title", "twitter:title") or (soup.title.get_text(" ", strip=True) if soup.title else None)
    description = _meta(soup, "description", "og:description", "twitter:description")
    author = _meta(soup, "author", "article:author")
    published = _meta(soup, "article:published_time", "date", "pubdate")
    published_at = None
    if published:
        try: published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except ValueError: pass
    root = soup.find("article") or soup.find("main") or soup.body or soup
    sections = [Section(level=1, blocks=[])]
    for element in root.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "pre", "ul", "ol", "table"], recursive=True):
        if not element.get_text(" ", strip=True): continue
        if element.name in {"ul", "ol"}:
            sections[-1].blocks.append(Block(type="list", items=[li.get_text(" ", strip=True) for li in element.find_all("li", recursive=False)]))
        elif element.name == "table":
            rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])] for row in element.find_all("tr")]
            if rows: sections[-1].blocks.append(Block(type="table", headers=rows[0], rows=rows[1:]))
        elif element.name in {"h1", "h2", "h3", "h4"}:
            sections.append(Section(heading=element.get_text(" ", strip=True), level=int(element.name[1]), blocks=[]))
        else:
            block_type = "quote" if element.name == "blockquote" else "code" if element.name == "pre" else "paragraph"
            sections[-1].blocks.append(Block(type=block_type, text=element.get_text(" ", strip=True)))
    sections = [section for section in sections if section.heading or section.blocks]
    text = " ".join(block.text or " ".join(block.items) for section in sections for block in section.blocks)
    links = list(dict.fromkeys(urljoin(final_url, a["href"]) for a in root.find_all("a", href=True) if urlparse(urljoin(final_url, a["href"])).scheme in {"http", "https"}))
    images = list(dict.fromkeys(urljoin(final_url, image["src"]) for image in root.find_all("img", src=True)))
    return CanonicalDocument(id=uuid4(), source_url=url, canonical_url=_meta(soup, "og:url") or final_url, domain=urlparse(final_url).netloc, title=title, author=author, published_at=published_at, fetched_at=datetime.now(timezone.utc), description=description, language=soup.html.get("lang") if soup.html else None, content={"sections": sections}, links=links, images=images, metadata={"open_graph": {tag.get("property"): tag.get("content") for tag in soup.find_all("meta", property=True) if tag.get("property", "").startswith("og:")}}, statistics=Statistics(word_count=len(text.split()), character_count=len(text), reading_time_minutes=max(1, round(len(text.split()) / 200))))
