from concurrent.futures import ThreadPoolExecutor, TimeoutError
from duckduckgo_search import DDGS


def _ddg_search(policy):
    results = DDGS().text(
        f"{policy} India government policy scheme",
        max_results=3,
    )
    if not results:
        return None
    return "\n".join(f"- {r['title']}: {r['body']}" for r in results)


def fetch_web_context(policy):
    try:
        with ThreadPoolExecutor(max_workers=1) as ex:
            return ex.submit(_ddg_search, policy).result(timeout=4)
    except (TimeoutError, Exception) as e:
        print(f"Search skipped: {e}")
        return None
