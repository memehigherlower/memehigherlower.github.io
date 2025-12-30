"""
KnowYourMeme View Count Updater - Google Search Version
Uses Google search to find KYM pages for memes without direct URLs.
Only updates view counts - does NOT modify images or other data.
"""

import json
import time
import random
import re
from pathlib import Path
from urllib.parse import quote_plus, unquote, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def is_placeholder(views: int) -> bool:
    """Check if a view count is a placeholder (round number)."""
    return views > 1000000 and views % 500000 == 0


def search_google(session: requests.Session, query: str) -> str:
    """
    Search Google for a query and return the first KYM meme URL found.
    """
    # Use Google's search URL
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10"

    try:
        response = session.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in search results
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Google wraps URLs in /url?q= redirects
            if '/url?q=' in href:
                # Extract the actual URL
                parsed = urlparse(href)
                params = parse_qs(parsed.query)
                if 'q' in params:
                    actual_url = params['q'][0]
                    if 'knowyourmeme.com/memes/' in actual_url:
                        # Skip non-meme pages
                        if '/memes/people/' not in actual_url and '/memes/sites/' not in actual_url:
                            return actual_url

            # Direct link check
            if 'knowyourmeme.com/memes/' in href:
                if '/memes/people/' not in href and '/memes/sites/' not in href:
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
    """Main function to update view counts using Google search."""
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

            # Search for the meme on KnowYourMeme specifically
            query = f"site:knowyourmeme.com {meme_name} meme"
            kym_url = search_google(session, query)

            if not kym_url:
                print(f"NOT FOUND (keeping {old_views:,})")
                failed_count += 1
                time.sleep(random.uniform(10, 15))
                continue

            # Delay before fetching the page
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

            # Longer rate limiting between searches (10-15 seconds)
            time.sleep(random.uniform(10, 15))

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
