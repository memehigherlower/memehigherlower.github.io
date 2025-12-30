"""
KnowYourMeme View Count Updater - Direct URL Guessing
Tries to guess KYM URLs based on meme names for remaining memes.
Only updates view counts - does NOT modify images or other data.
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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Manual URL mappings for remaining memes
REMAINING_URLS = {
    "sad-pablo-escobar": "https://knowyourmeme.com/memes/sad-pablo-escobar",
    "rage-guy-fffuuu": "https://knowyourmeme.com/memes/rage-guy-fffuuu",
    "wat": "https://knowyourmeme.com/memes/wat",
    "omae-wa-mou-shindeiru": "https://knowyourmeme.com/memes/you-are-already-dead-omae-wa-mou-shindeiru",
    "do-you-even-lift": "https://knowyourmeme.com/memes/do-you-even-lift",
    "haters-gonna-hate": "https://knowyourmeme.com/memes/haters-gonna-hate",
    "yo-dawg-xzibit": "https://knowyourmeme.com/memes/xzibit-yo-dawg",
    "the-most-interesting-man": "https://knowyourmeme.com/memes/the-most-interesting-man-in-the-world",
    "cash-me-outside": "https://knowyourmeme.com/memes/cash-me-outside-howbow-dah",
    "i-know-that-feel-bro": "https://knowyourmeme.com/memes/i-know-that-feel-bro",
    "he-protec-but-he-also-attac": "https://knowyourmeme.com/memes/he-protec-but-he-also-attac",
    "high-expectations-asian-father": "https://knowyourmeme.com/memes/high-expectations-asian-father",
    "its-over-9000": "https://knowyourmeme.com/memes/its-over-9000",
    "leeroy-jenkins": "https://knowyourmeme.com/memes/leeroy-jenkins",
    "the-cake-is-a-lie": "https://knowyourmeme.com/memes/the-cake-is-a-lie",
    "impossibru": "https://knowyourmeme.com/memes/impossibru",
    "feels-bad-man": "https://knowyourmeme.com/memes/feels-bad-man-sad-frog",
    "dont-talk-to-me-or-my-son": "https://knowyourmeme.com/memes/dont-talk-to-me-or-my-son-ever-again",
    "honey-badger-dont-care": "https://knowyourmeme.com/memes/honey-badger",
    "9-10-21": "https://knowyourmeme.com/memes/9-10-21",
    "yes-this-is-dog": "https://knowyourmeme.com/memes/yes-this-is-dog",
    "gangnam-style": "https://knowyourmeme.com/memes/gangnam-style",
    "bear-grylls": "https://knowyourmeme.com/memes/bear-grylls-better-drink-my-own-piss",
    "successful-black-man": "https://knowyourmeme.com/memes/successful-black-man",
    "tragedy-of-darth-plagueis": "https://knowyourmeme.com/memes/the-tragedy-of-darth-plagueis-the-wise",
    "leonardo-dicaprio-cheers": "https://knowyourmeme.com/memes/leonardo-dicaprio-laughing",
    "oprah-you-get-a": "https://knowyourmeme.com/memes/oprah-you-get-a-car",
    "condescending-wonka": "https://knowyourmeme.com/memes/condescending-wonka-creepy-wonka",
    "dinkleberg": "https://knowyourmeme.com/memes/dinkleberg",
    "third-world-skeptical-kid": "https://knowyourmeme.com/memes/third-world-skeptical-kid",
    "blue-pill-red-pill": "https://knowyourmeme.com/memes/red-pill-blue-pill",
    "awkward-moment-seal": "https://knowyourmeme.com/memes/awkward-moment-seal",
    "mr-bean-waiting": "https://knowyourmeme.com/memes/waiting-for-op",
    "mike-wazowski-face-swap": "https://knowyourmeme.com/memes/mike-wazowski-sulley-face-swap",
    "crying-michael-jordan": "https://knowyourmeme.com/memes/crying-michael-jordan",
    "guy-explaining": "https://knowyourmeme.com/memes/guy-explaining",
    "types-of-headaches": "https://knowyourmeme.com/memes/types-of-headaches",
    "scared-cat": "https://knowyourmeme.com/memes/cat-scared-of-cucumber",
    "oh-no-its-retarded": "https://knowyourmeme.com/memes/oh-no-its-retarded",
    "uno-reverse-card": "https://knowyourmeme.com/memes/uno-reverse-card",
    "inhaling-seagull": "https://knowyourmeme.com/memes/inhaling-seagull",
    "polish-jerry": "https://knowyourmeme.com/memes/polish-jerry",
    "sleeping-shaq": "https://knowyourmeme.com/memes/sleeping-shaq",
    "sad-cat-thumbs-up": "https://knowyourmeme.com/memes/sad-thumbs-up-cat",
    "no-no-hes-got-a-point": "https://knowyourmeme.com/memes/no-no-hes-got-a-point",
    "drake-wheres-the-door-hole": "https://knowyourmeme.com/memes/wheres-the-door-hole",
    "men-will-literally": "https://knowyourmeme.com/memes/men-will-literally",
    "stonks-not-stonks": "https://knowyourmeme.com/memes/stonks",
    "cat-lawyer": "https://knowyourmeme.com/memes/lawyer-cat",
    "pet-the-dog": "https://knowyourmeme.com/memes/petting-the-dog",
    "fernanfloo-laughing": "https://knowyourmeme.com/memes/fernanfloo-laughing",
    "vince-mcmahon-reaction": "https://knowyourmeme.com/memes/vince-mcmahon-reaction",
    "hold-up-wait-a-minute": "https://knowyourmeme.com/memes/hol-up-wait-a-minute",
    "excuse-me-what-the-f": "https://knowyourmeme.com/memes/excuse-me-what-the-fuck",
    "skyrim-skill-tree": "https://knowyourmeme.com/memes/skyrim-skill-tree",
    "distracted-boyfriend-reversed": "https://knowyourmeme.com/memes/distracted-boyfriend",
    "the-scroll-of-truth": "https://knowyourmeme.com/memes/the-scroll-of-truth",
    "the-office-handshake": "https://knowyourmeme.com/memes/epic-handshake",
    "sad-affleck": "https://knowyourmeme.com/memes/sad-ben-affleck",
    "brain-before-sleep": "https://knowyourmeme.com/memes/brain-before-sleep",
    "kpop-fans-be-like": "https://knowyourmeme.com/memes/kpop-stans-fancams",
    "obama-giving-medal-to-obama": "https://knowyourmeme.com/memes/obama-awarding-obama-a-medal",
    "listen-here-you-little": "https://knowyourmeme.com/memes/listen-here-you-little-shit",
    "finally-inner-peace": "https://knowyourmeme.com/memes/finally-inner-peace",
    "two-soyjaks-pointing": "https://knowyourmeme.com/memes/two-soyjaks-pointing",
    "pedro-raccoon": "https://knowyourmeme.com/memes/pedro-raccoon",
    "chad-yes": "https://knowyourmeme.com/memes/yes-chad",
    "angry-birds-pig": "https://knowyourmeme.com/memes/angry-birds",
    "its-free-real-estate": "https://knowyourmeme.com/memes/its-free-real-estate",
    "spider-man-glasses": "https://knowyourmeme.com/memes/spider-man-reading",
    "megamind-no-maidens": "https://knowyourmeme.com/memes/no-bitches",
}


def is_placeholder(views: int) -> bool:
    """Check if a view count is a placeholder (round number)."""
    return views > 1000000 and views % 500000 == 0


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
    except requests.exceptions.HTTPError as e:
        if e.response.status_code != 404:
            print(f"HTTP error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Main function to update view counts using direct URLs."""
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
            meme_id = meme['id']
            meme_name = meme['name']
            old_views = meme['views']

            print(f"[{idx}/{len(placeholder_memes)}] {meme_name}...", end=" ", flush=True)

            # Look up URL in mapping
            url = REMAINING_URLS.get(meme_id)

            if not url:
                # Try to construct URL from ID
                url_slug = meme_id.lower().replace(' ', '-')
                url = f"https://knowyourmeme.com/memes/{url_slug}"

            # Scrape view count
            views = scrape_views(session, url)

            if views and views > 10000:
                memes[i]['views'] = views
                print(f"{old_views:,} -> {views:,}")
                updated_count += 1
            else:
                print(f"NOT FOUND (keeping {old_views:,})")
                failed_count += 1

            # Rate limiting (shorter since we're hitting KYM directly)
            time.sleep(random.uniform(1.5, 2.5))

    except KeyboardInterrupt:
        print("\n\nInterrupted! Saving progress...")

    # Save updated data
    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"Done! Updated: {updated_count}, Failed: {failed_count}")
    print(f"Saved to {memes_path}")


if __name__ == "__main__":
    main()
