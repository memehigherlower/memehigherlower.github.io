"""
KnowYourMeme View Count Updater - Web Search Version
Uses DuckDuckGo to find KYM pages for memes without direct URLs.
Only updates view counts - does NOT modify images or other data.
"""

import json
import time
import random
import re
from pathlib import Path
from urllib.parse import quote_plus, unquote
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def is_placeholder(views: int) -> bool:
    """Check if a view count is a placeholder (round number)."""
    return views > 1000000 and views % 500000 == 0


def search_duckduckgo(session: requests.Session, query: str) -> str:
    """
    Search DuckDuckGo for a query and return the first KYM meme URL found.
    """
    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

    try:
        response = session.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find result links - DuckDuckGo uses class "result__a" for result links
        for link in soup.select('a.result__a'):
            href = link.get('href', '')

            # DuckDuckGo wraps URLs, need to extract the actual URL
            if 'uddg=' in href:
                # Extract URL from DuckDuckGo redirect
                match = re.search(r'uddg=([^&]+)', href)
                if match:
                    href = unquote(match.group(1))

            # Check if it's a KYM meme page (not people, sites, etc.)
            if 'knowyourmeme.com/memes/' in href:
                # Skip non-meme pages
                if '/memes/people/' in href or '/memes/sites/' in href or '/memes/subcultures/' in href:
                    continue
                return href

        # Fallback: look for any knowyourmeme link in href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'knowyourmeme.com/memes/' in href:
                if '/memes/people/' not in href and '/memes/sites/' not in href:
                    # Clean up the URL if needed
                    if href.startswith('//'):
                        href = 'https:' + href
                    return href

    except Exception as e:
        print(f"Search error: {e}")

    return None


def extract_views(soup: BeautifulSoup) -> int:
    """Extract view count from KYM page - first large number in dl element."""
    try:
        dls = soup.select('dl')
        for dl in dls:
            text = dl.get_text()
            numbers = re.findall(r'(\d{1,3}(?:,\d{3})+)', text)
            if numbers:
                for num_str in numbers:
                    views = int(num_str.replace(',', ''))
                    if views > 10000:
                        return views
    except Exception as e:
        print(f"Extract error: {e}")
    return None


def scrape_views(session: requests.Session, url: str) -> int:
    """Scrape view count from a KYM page."""
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_views(soup)
    except Exception as e:
        return None


def main():
    """Main function to update view counts using web search."""
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    with open(memes_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']

    # Find memes with placeholder values
    placeholder_memes = [(i, m) for i, m in enumerate(memes) if is_placeholder(m['views'])]

    print(f"Loaded {len(memes)} memes")
    print(f"Found {len(placeholder_memes)} memes with placeholder values")
    print("=" * 70)

    session = requests.Session()
    updated_count = 0
    failed_count = 0

    try:
        for idx, (i, meme) in enumerate(placeholder_memes, 1):
            meme_name = meme['name']
            old_views = meme['views']

            print(f"[{idx}/{len(placeholder_memes)}] {meme_name}...", end=" ", flush=True)

            # Search for the meme
            query = f"{meme_name} know your meme"
            kym_url = search_duckduckgo(session, query)

            if not kym_url:
                print(f"NOT FOUND (keeping {old_views:,})")
                failed_count += 1
                time.sleep(random.uniform(8, 12))
                continue

            # Longer delay before fetching the page
            time.sleep(random.uniform(3, 5))

            # Scrape view count
            views = scrape_views(session, kym_url)

            if views and views > 10000:
                memes[i]['views'] = views
                print(f"{old_views:,} -> {views:,}")
                updated_count += 1
            else:
                print(f"NO VIEWS (keeping {old_views:,})")
                failed_count += 1

            # Longer rate limiting between searches (8-12 seconds)
            time.sleep(random.uniform(8, 12))

    except KeyboardInterrupt:
        print("\n\nInterrupted! Saving progress...")

    # Save updated data (only views changed, everything else preserved)
    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"Done! Updated: {updated_count}, Failed: {failed_count}")
    print(f"Saved to {memes_path}")


if __name__ == "__main__":
    main()
