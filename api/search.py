from duckduckgo_search import DDGS


def fetch_web_context(policy):
    """Search DuckDuckGo and return top results as a context string."""
    try:
        results = DDGS().text(
            f"{policy} India government bill act scheme",
            max_results=6,
        )
        if not results:
            return None
        return "\n".join(f"- {r['title']}: {r['body']}" for r in results)
    except Exception as e:
        print(f"Search error: {e}")
        return None
