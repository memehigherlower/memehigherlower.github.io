"""Quick test to verify view extraction works."""

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def extract_views(soup):
    """Extract view count from dl elements."""
    dls = soup.select('dl')
    for dl in dls:
        text = dl.get_text()
        numbers = re.findall(r'(\d{1,3}(?:,\d{3})+)', text)
        if numbers:
            for num_str in numbers:
                views = int(num_str.replace(',', ''))
                if views > 10000:
                    return views
    return None

# Test on Doge
print("Testing Doge...")
r = requests.get("https://knowyourmeme.com/memes/doge", headers=HEADERS)
soup = BeautifulSoup(r.text, 'html.parser')
views = extract_views(soup)
print(f"Doge views: {views:,}" if views else "Failed to extract")

# Test on Trollface
print("\nTesting Trollface...")
r = requests.get("https://knowyourmeme.com/memes/trollface", headers=HEADERS)
soup = BeautifulSoup(r.text, 'html.parser')
views = extract_views(soup)
print(f"Trollface views: {views:,}" if views else "Failed to extract")

# Test on Pepe
print("\nTesting Pepe...")
r = requests.get("https://knowyourmeme.com/memes/pepe-the-frog", headers=HEADERS)
soup = BeautifulSoup(r.text, 'html.parser')
views = extract_views(soup)
print(f"Pepe views: {views:,}" if views else "Failed to extract")
