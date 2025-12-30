"""Test the scraper on a single meme to verify it extracts views correctly."""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def test_doge():
    """Test extracting views from the Doge meme page."""
    url = "https://knowyourmeme.com/memes/doge"

    print(f"Fetching {url}...")
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Save HTML for inspection
    html_path = Path(__file__).parent / "doge_page.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Saved page HTML to {html_path}")

    # Find the aside section
    aside = soup.select_one('aside')
    if aside:
        print("\n--- ASIDE CONTENT ---")
        print(aside.get_text()[:1000])
        print("--- END ASIDE ---\n")

        # Look for numbers
        numbers = re.findall(r'(\d{1,3}(?:,\d{3})+|\d+)', aside.get_text())
        print(f"Numbers found in aside: {numbers}")

        # Filter large numbers
        large_numbers = []
        for n in numbers:
            try:
                val = int(n.replace(',', ''))
                if val > 10000:
                    large_numbers.append(val)
            except:
                pass
        print(f"Large numbers (>10000): {large_numbers}")

        if large_numbers:
            print(f"\nExtracted view count: {max(large_numbers):,}")
    else:
        print("No aside found!")

    # Also check for specific stat patterns
    print("\n--- Looking for stat patterns ---")

    # Look for dl/dd elements (definition lists often used for stats)
    dls = soup.select('dl')
    for dl in dls:
        print(f"DL content: {dl.get_text()[:200]}")

    # Look for any element with "views" nearby
    for elem in soup.find_all(string=re.compile(r'views', re.IGNORECASE)):
        parent = elem.parent
        if parent:
            print(f"Found 'views' text in: {parent.name} - {parent.get_text()[:100]}")

if __name__ == "__main__":
    test_doge()
