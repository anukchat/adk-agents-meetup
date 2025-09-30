
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

def fetch_web_page(url: str) -> Dict[str, Any]:
    """
    Fetches the full HTML content of a static web page.

    Use this when the page is likely server-rendered (no JavaScript needed),
    to quickly extract links, visible tables, or metadata using HTML parsing.

    Args:
        url: Target web page URL.

    Returns:
        Dict with full HTML string or error.
    """
    try:
        headers = {'User-Agent': DEFAULT_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return {"content": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def fetch_web_page_simple(url: str) -> Dict[str, Any]:
    """
    Fetches only the **visible text** content from a static page (stripped HTML).

    Use this when you're looking for readable content, quick summaries,
    or validating that the page contains the needed info before deeper navigation.

    Args:
        url: Web page to fetch.

    Returns:
        Dict with extracted readable text or error.
    """
    try:
        headers = {'User-Agent': DEFAULT_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        return {"content": " ".join(soup.stripped_strings)}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_web_tools(selected_tools: List[str] = ["fetch_web_page", "fetch_web_page_simple"]):
    tool_mapping = {
        "fetch_web_page": fetch_web_page,
        "fetch_web_page_simple": fetch_web_page_simple,
    }
    return [tool_mapping[tool] for tool in selected_tools if tool in tool_mapping]

