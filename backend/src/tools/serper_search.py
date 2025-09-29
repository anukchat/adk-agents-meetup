# serper_search.py
"""
Web search tool using SERPER API for integration with LLM workflows.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_BASE_URL = os.getenv("SERPER_BASE_URL", "https://google.serper.dev/search")

def serper_search(query: str, api_key: str = None, base_url: str = None):
    """
    Perform a web search using the SERPER API.
    Args:
        query (str): The search query.
        api_key (str, optional): SERPER API key. Defaults to env var.
        base_url (str, optional): SERPER API base URL. Defaults to env var.
    Returns:
        dict: Search results from SERPER API.
    """
    api_key = api_key or SERPER_API_KEY
    base_url = base_url or SERPER_BASE_URL
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query}
    response = requests.post(base_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Simple test
    test_query = "Who won the world series in 2020?"
    results = serper_search(test_query)
    print(results.get("organic", [{}])[0].get("snippet", "No results found."))