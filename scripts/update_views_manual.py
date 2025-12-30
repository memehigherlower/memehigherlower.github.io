"""
KnowYourMeme View Count Updater - Manual URLs from user
"""

import json
import time
import random
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Manual URLs provided by user
MANUAL_URLS = {
    "sad-pablo-escobar": "https://knowyourmeme.com/memes/pablo-escobar-waiting",
    "cash-me-outside": "https://knowyourmeme.com/memes/cash-me-ousside-howbow-dah",
    "morpheus-blue-red-pill": "https://knowyourmeme.com/memes/red-pill",
    "sad-cat-thumbs-up": "https://knowyourmeme.com/memes/thumbs-up-crying-cat",
    "drake-josh-door": "https://knowyourmeme.com/memes/drake-wheres-the-door-hole",
    "men-will-literally": "https://knowyourmeme.com/memes/instead-of-going-to-therapy",
    "cat-lawyer": "https://knowyourmeme.com/memes/zoom-cat-lawyer-im-not-a-cat",
    "pet-the-dog": "https://knowyourmeme.com/memes/pet-the-x-petthe-emotes",
    "sad-affleck": "https://knowyourmeme.com/memes/sad-affleck",
    "obama-medal": "https://knowyourmeme.com/memes/obama-awards-obama-a-medal",
    "pedro-raccoon": "https://knowyourmeme.com/memes/raccoon-dancing-in-a-circle-pedro-pedro-pedro",
    "spiderman-glasses": "https://knowyourmeme.com/memes/peter-parkers-glasses",
}


def extract_views(soup: BeautifulSoup) -> int:
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
    except:
        pass
    return None


def scrape_views(session: requests.Session, url: str) -> int:
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_views(soup)
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    with open(memes_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']
    session = requests.Session()
    updated = 0

    print(f"Updating {len(MANUAL_URLS)} memes with user-provided URLs")
    print("=" * 60)

    for meme_id, url in MANUAL_URLS.items():
        # Find the meme in the list
        meme_idx = None
        meme = None
        for i, m in enumerate(memes):
            if m['id'] == meme_id:
                meme_idx = i
                meme = m
                break

        if meme is None:
            print(f"{meme_id}: NOT IN DATABASE")
            continue

        print(f"{meme['name']}...", end=" ", flush=True)

        views = scrape_views(session, url)

        if views and views > 1000:
            old_views = meme['views']
            memes[meme_idx]['views'] = views
            print(f"{old_views:,} -> {views:,}")
            updated += 1
        else:
            print(f"FAILED")

        time.sleep(random.uniform(1.5, 2.5))

    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"Updated: {updated}/{len(MANUAL_URLS)}")


if __name__ == "__main__":
    main()
