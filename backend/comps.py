import os
import re
import requests
from typing import List, Dict, Any, Optional


def parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    # find $123 or 123.45 patterns
    m = re.search(r"\$?\s*([0-9]{1,6}(?:\.[0-9]{1,2})?)", text.replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(1))
    except:
        return None


def fetch_google_comps(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Uses Google Custom Search JSON API.
    Env vars:
      GOOGLE_API_KEY
      GOOGLE_CX
    """
    api_key = os.getenv("GOOGLE_API_KEY", "")
    cx = os.getenv("GOOGLE_CX", "")
    if not api_key or not cx:
        return [{"title": "Missing GOOGLE_API_KEY or GOOGLE_CX", "link": "", "snippet": "", "price": None}]

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": min(limit, 10)}

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    items = data.get("items", [])
    out = []
    for it in items[:limit]:
        title = it.get("title", "")
        link = it.get("link", "")
        snippet = it.get("snippet", "")
        price = parse_price(snippet)  # best-effort from snippet
        out.append({"title": title, "link": link, "snippet": snippet, "price": price})
    return out
