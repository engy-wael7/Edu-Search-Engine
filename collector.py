"""Crawl trusted educational sites and scrape HTML/PDF resources for the corpus."""
from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

ROOT = Path(__file__).parent
PDF_DIR = ROOT / "data" / "pdfs"
PAGE_DIR = ROOT / "data" / "pages"
SOURCES_FILE = ROOT / "data" / "sources.json"
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_PAGE_BYTES = 2 * 1024 * 1024
USER_AGENT = "EducationalSearchEngine/1.0 (student IR project)"
ACADEMIC_SUFFIXES = (".edu", ".ac.uk", ".edu.au", "arxiv.org", "openstax.org", "ocw.mit.edu")
ROBOTS_CACHE: dict[str, tuple[RobotFileParser | None, float]] = {}
LAST_REQUEST: dict[str, float] = {}


def is_academic_host(host: str) -> bool:
    host = host.lower().split(":")[0].rstrip(".")
    return any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in ACADEMIC_SUFFIXES)


def _is_pdf_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return parsed.scheme in {"http", "https"} and is_academic_host(host) and (
        parsed.path.lower().endswith(".pdf") or (host.endswith("arxiv.org") and parsed.path.startswith("/pdf/"))
    )


def _robots_policy(url: str) -> tuple[bool, float]:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in ROBOTS_CACHE:
        parser = RobotFileParser()
        try:
            response = requests.get(origin + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=6)
            if response.status_code in (404, 410):
                parser.parse([])
                ROBOTS_CACHE[origin] = (parser, 1.0)
            elif response.ok:
                parser.parse(response.text.splitlines())
                delay = parser.crawl_delay(USER_AGENT) or parser.crawl_delay("*") or 1.0
                ROBOTS_CACHE[origin] = (parser, max(float(delay), 1.0))
            else:
                ROBOTS_CACHE[origin] = (None, 1.0)
        except requests.RequestException:
            ROBOTS_CACHE[origin] = (None, 1.0)
    parser, delay = ROBOTS_CACHE[origin]
    return bool(parser and parser.can_fetch(USER_AGENT, url)), delay


def _wait_for_host(url: str, delay: float) -> None:
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    remaining = delay - (time.monotonic() - LAST_REQUEST.get(origin, 0.0))
    if origin in LAST_REQUEST and remaining > 0:
        time.sleep(remaining)
    LAST_REQUEST[origin] = time.monotonic()


def _read_sources() -> dict:
    try:
        return json.loads(SOURCES_FILE.read_text(encoding="utf-8")) if SOURCES_FILE.exists() else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _discover_seeds(topic: str, limit: int) -> list[str]:
    queries = (
        f"{topic} educational resources site:edu",
        f"{topic} learning resources site:ac.uk",
        f"{topic} site:openstax.org OR site:ocw.mit.edu",
        f"{topic} research site:arxiv.org",
    )
    seeds, seen = [], set()
    for query in queries:
        try:
            results = DDGS(timeout=12).text(query, max_results=max(3, limit // len(queries)), backend="auto")
        except Exception:
            continue
        for result in results or []:
            url = result.get("href") or result.get("url") or ""
            url, _ = urldefrag(url)
            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and is_academic_host(parsed.hostname or "") and url not in seen:
                seeds.append(url)
                seen.add(url)
                if len(seeds) >= limit:
                    return seeds
    return seeds


def crawl_and_scrape(topic: str, page_limit: int = 20, pdf_limit: int = 8, max_depth: int = 2) -> list[dict]:
    """Seed from web search, then breadth-first crawl same-host educational pages."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    known = _read_sources()
    known_urls = {item.get("url") for item in known.values()}
    queue = deque((url, 0, urlparse(url).hostname or "") for url in _discover_seeds(topic, max(page_limit, 8)))
    queued = {url for url, _, _ in queue}
    visited = set()
    added = []
    crawled_pages = 0
    fetched_html = 0
    downloaded_pdfs = 0

    while queue and fetched_html < page_limit:
        url, depth, seed_host = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if _is_pdf_url(url):
            if downloaded_pdfs < pdf_limit and url not in known_urls:
                allowed, delay = _robots_policy(url)
                if allowed:
                    _wait_for_host(url, delay)
                    try:
                        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(6, 20),
                                          stream=True, allow_redirects=True) as response:
                            final_url = response.url
                            if response.status_code != 200 or not _is_pdf_url(final_url):
                                continue
                            content = bytearray()
                            for chunk in response.iter_content(64 * 1024):
                                if chunk:
                                    content.extend(chunk)
                                    if len(content) > MAX_FILE_BYTES:
                                        break
                        if len(content) > MAX_FILE_BYTES or not content.startswith(b"%PDF"):
                            continue
                    except requests.RequestException:
                        continue
                    filename = hashlib.sha256(final_url.encode("utf-8")).hexdigest()[:20] + ".pdf"
                    (PDF_DIR / filename).write_bytes(content)
                    metadata = {"url": final_url, "title": filename, "filename": filename,
                                "topic": topic, "kind": "pdf"}
                    known[filename] = metadata
                    known_urls.add(final_url)
                    added.append(metadata)
                    downloaded_pdfs += 1
            continue

        if depth > max_depth or not is_academic_host(seed_host):
            continue
        parsed = urlparse(url)
        if (parsed.hostname or "").lower() != seed_host.lower() or url in known_urls:
            continue
        allowed, delay = _robots_policy(url)
        if not allowed:
            continue
        _wait_for_host(url, delay)
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(6, 20),
                              allow_redirects=True, stream=True) as response:
                final_url = urldefrag(response.url)[0]
                if response.status_code != 200 or (urlparse(final_url).hostname or "").lower() != seed_host.lower():
                    continue
                content_type = response.headers.get("Content-Type", "").lower()
                if "html" not in content_type:
                    continue
                raw = bytearray()
                for chunk in response.iter_content(32 * 1024):
                    if chunk:
                        raw.extend(chunk)
                        if len(raw) > MAX_PAGE_BYTES:
                            break
                encoding = response.encoding or "utf-8"
            if len(raw) > MAX_PAGE_BYTES:
                continue
            soup = BeautifulSoup(bytes(raw).decode(encoding, errors="replace"), "html.parser")
        except (requests.RequestException, LookupError, UnicodeError):
            continue

        fetched_html += 1
        title = soup.title.get_text(" ", strip=True) if soup.title else final_url
        for element in soup.select("script, style, noscript, nav, footer, header, aside, form, svg"):
            element.decompose()
        main = soup.find("main") or soup.find("article") or soup.body or soup
        text = " ".join(main.stripped_strings)[:150_000]
        if len(text) >= 80:
            filename = hashlib.sha256(final_url.encode("utf-8")).hexdigest()[:20] + ".json"
            metadata = {"url": final_url, "title": title[:300], "filename": filename,
                        "topic": topic, "kind": "html"}
            (PAGE_DIR / filename).write_text(json.dumps({**metadata, "text": text}, ensure_ascii=False),
                                             encoding="utf-8")
            known[filename] = metadata
            known_urls.add(final_url)
            added.append(metadata)
            crawled_pages += 1

        if depth < max_depth:
            for anchor in soup.find_all("a", href=True):
                link, _ = urldefrag(urljoin(final_url, anchor["href"]))
                link_parsed = urlparse(link)
                if (len(queued) < page_limit * 25
                        and link_parsed.scheme in {"http", "https"}
                        and (link_parsed.hostname or "").lower() == seed_host.lower()
                        and link not in queued and link not in visited):
                    queue.append((link, depth + 1, seed_host))
                    queued.add(link)

    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_FILE.write_text(json.dumps(known, ensure_ascii=False, indent=2), encoding="utf-8")
    return added


# Kept for compatibility with earlier project instructions.
def collect_pdfs(topic: str, limit: int = 8) -> list[dict]:
    return crawl_and_scrape(topic, pdf_limit=limit)
