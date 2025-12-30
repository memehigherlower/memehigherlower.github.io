"""
KnowYourMeme View Count Updater - Final batch
Uses correct KYM URLs for the last 28 memes.
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

# Final URL mappings for remaining 28 memes
FINAL_URLS = {
    "sad-pablo-escobar": "https://knowyourmeme.com/memes/sad-pablo-escobar",
    "yo-dawg": "https://knowyourmeme.com/memes/xzibit-yo-dawg",
    "most-interesting-man": "https://knowyourmeme.com/memes/the-most-interesting-man-in-the-world",
    "cash-me-outside": "https://knowyourmeme.com/memes/cash-me-outside-howbow-dah",
    "i-know-that-feel": "https://knowyourmeme.com/memes/i-know-that-feel-bro",
    "he-protec-he-attac": "https://knowyourmeme.com/memes/he-protec-but-he-also-attac",
    "nine-plus-ten": "https://knowyourmeme.com/memes/9-10-21",
    "darth-plagueis": "https://knowyourmeme.com/memes/the-tragedy-of-darth-plagueis-the-wise",
    "willy-wonka": "https://knowyourmeme.com/memes/condescending-wonka-creepy-wonka",
    "third-world-skeptical-kid": "https://knowyourmeme.com/memes/third-world-skeptical-kid",
    "morpheus-blue-red-pill": "https://knowyourmeme.com/memes/red-pill-blue-pill",
    "guy-explaining": "https://knowyourmeme.com/memes/man-explaining",
    "scared-cat": "https://knowyourmeme.com/memes/scared-cat",
    "sad-cat-thumbs-up": "https://knowyourmeme.com/memes/sad-thumbs-up-cat",
    "drake-josh-door": "https://knowyourmeme.com/memes/wheres-the-door-hole",
    "men-will-literally": "https://knowyourmeme.com/memes/men-will-literally",
    "cat-lawyer": "https://knowyourmeme.com/memes/lawyer-dog-cat-im-not-a-cat",
    "pet-the-dog": "https://knowyourmeme.com/memes/you-can-pet-the-dog",
    "fernanfloo-laughing": "https://knowyourmeme.com/memes/fernanfloo-laughing",
    "hold-up": "https://knowyourmeme.com/memes/hol-up",
    "sad-affleck": "https://knowyourmeme.com/memes/sad-ben-affleck",
    "brain-before-sleep": "https://knowyourmeme.com/memes/brain-before-sleep",
    "kpop-fans-be-like": "https://knowyourmeme.com/memes/kpop-fans-in-comment-sections",
    "obama-medal": "https://knowyourmeme.com/memes/obama-awarding-obama-a-medal",
    "finally-inner-peace": "https://knowyourmeme.com/memes/finally-inner-peace",
    "pedro-raccoon": "https://knowyourmeme.com/memes/pedro-raccoon-dancing-raccoon",
    "spiderman-glasses": "https://knowyourmeme.com/memes/spider-man-reading",
    "megamind-no-bitches": "https://knowyourmeme.com/memes/no-bitches",
}


def is_placeholder(views: int) -> bool:
    return views > 1000000 and views % 500000 == 0


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
    except:
        return None


def main():
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    with open(memes_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']
    placeholder_memes = [(i, m) for i, m in enumerate(memes) if is_placeholder(m['views'])]

    print(f"Found {len(placeholder_memes)} memes with placeholder values")
    print("=" * 60)

    session = requests.Session()
    updated = 0

    for idx, (i, meme) in enumerate(placeholder_memes, 1):
        meme_id = meme['id']
        meme_name = meme['name']
        old_views = meme['views']

        print(f"[{idx}/{len(placeholder_memes)}] {meme_name}...", end=" ", flush=True)

        url = FINAL_URLS.get(meme_id)
        if not url:
            print(f"NO URL")
            continue

        views = scrape_views(session, url)

        if views and views > 10000:
            memes[i]['views'] = views
            print(f"{old_views:,} -> {views:,}")
            updated += 1
        else:
            print(f"NOT FOUND")

        time.sleep(random.uniform(1.5, 2.5))

    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"Updated: {updated}/{len(placeholder_memes)}")


if __name__ == "__main__":
    main()
