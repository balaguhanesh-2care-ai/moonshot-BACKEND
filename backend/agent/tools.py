import logging
from typing import Any

import httpx

from agent.models import DocSearchResult, DocSearchResultItem, FetchedDoc, FetchedDocs

log = logging.getLogger(__name__)

MAX_FETCH_CHARS = 80_000


def fetch_url(url: str, *, timeout: float = 25.0) -> str:
    with httpx.Client(follow_redirects=True) as client:
        r = client.get(url, timeout=timeout)
        r.raise_for_status()
        text = r.text
    if len(text) > MAX_FETCH_CHARS:
        text = text[:MAX_FETCH_CHARS] + "\n... [truncated]"
    return text


def tavily_search(queries: list[str], *, max_results_per_query: int = 5) -> DocSearchResult:
    from config import TAVILY_API_KEY
    if not (TAVILY_API_KEY and queries):
        log.info("tavily_search: no TAVILY_API_KEY or empty queries, skipping")
        return DocSearchResult()
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        items: list[DocSearchResultItem] = []
        seen: set[str] = set()
        for q in queries[:5]:
            try:
                resp = client.search(q, max_results=max_results_per_query)
                for r in getattr(resp, "results", []) or []:
                    url = getattr(r, "url", None) or getattr(r, "href", "") or ""
                    if url and url not in seen:
                        seen.add(url)
                        items.append(DocSearchResultItem(
                            url=url,
                            title=getattr(r, "title", "") or "",
                            content=(getattr(r, "content", "") or getattr(r, "snippet", "") or "")[:2000],
                        ))
            except Exception as e:
                log.warning("tavily_search query %s failed: %s", q[:50], e)
        log.info("tavily_search: %d queries -> %d unique URLs", len(queries), len(items))
        return DocSearchResult(results=items)
    except Exception as e:
        log.warning("tavily_search failed: %s", e)
        return DocSearchResult()


def fallback_web_search(queries: list[str], max_per: int = 3) -> DocSearchResult:
    items: list[DocSearchResultItem] = []
    seen: set[str] = set()
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for q in queries[:5]:
                try:
                    for r in list(ddgs.text(q, max_results=max_per)):
                        href = r.get("href", "") or ""
                        if href and href not in seen:
                            seen.add(href)
                            items.append(DocSearchResultItem(
                                url=href,
                                title=r.get("title", "") or "",
                                content=(r.get("body", "") or "")[:2000],
                            ))
                except Exception as e:
                    log.warning("fallback_web_search query failed: %s", e)
    except Exception as e:
        log.warning("fallback_web_search (duckduckgo) failed: %s", e)
    log.info("fallback_web_search: %d queries -> %d URLs", len(queries), len(items))
    return DocSearchResult(results=items)


def search_docs(queries: list[str]) -> DocSearchResult:
    result = tavily_search(queries)
    if not result.results:
        result = fallback_web_search(queries)
    return result


def fetch_docs_from_urls(urls: list[str], *, max_docs: int = 10) -> FetchedDocs:
    docs: list[FetchedDoc] = []
    for url in urls[:max_docs]:
        if not url or not url.startswith("http"):
            continue
        try:
            content = fetch_url(url)
            docs.append(FetchedDoc(url=url, content=content))
            log.info("fetch_docs: fetched %s (%d chars)", url[:60], len(content))
        except Exception as e:
            log.warning("fetch_docs: failed %s: %s", url[:50], e)
    log.info("fetch_docs: %d URLs -> %d docs", len(urls[:max_docs]), len(docs))
    return FetchedDocs(docs=docs)
