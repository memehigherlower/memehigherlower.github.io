"""Test the search function to see what's happening."""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def test_search(term):
    """Test searching for a meme."""
    search_url = f"https://knowyourmeme.com/search?q={requests.utils.quote(term)}"
    print(f"\nSearching for: {term}")
    print(f"URL: {search_url}")

    r = requests.get(search_url, headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")

    soup = BeautifulSoup(r.text, 'html.parser')

    # Look for links
    meme_links = soup.select('a[href*="/memes/"]')
    print(f"Found {len(meme_links)} /memes/ links")

    for i, link in enumerate(meme_links[:5]):
        href = link.get('href', '')
        text = link.get_text()[:50].strip()
        print(f"  {i+1}. {href} - {text}")

# Test a few
test_search("doge")
test_search("trollface")
test_search("pepe the frog")
