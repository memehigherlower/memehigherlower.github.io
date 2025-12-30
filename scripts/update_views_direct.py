"""
KnowYourMeme View Count Updater - Direct URLs
Uses direct meme page URLs instead of search.
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

# Direct KYM URLs for each meme
MEME_URLS = {
    "doge": "https://knowyourmeme.com/memes/doge",
    "distracted-boyfriend": "https://knowyourmeme.com/memes/distracted-boyfriend",
    "pepe-the-frog": "https://knowyourmeme.com/memes/pepe-the-frog",
    "rickroll": "https://knowyourmeme.com/memes/rickroll",
    "success-kid": "https://knowyourmeme.com/memes/i-hate-sandcastles-success-kid",
    "grumpy-cat": "https://knowyourmeme.com/memes/grumpy-cat",
    "drake-hotline-bling": "https://knowyourmeme.com/memes/drakeposting",
    "expanding-brain": "https://knowyourmeme.com/memes/expanding-brain",
    "surprised-pikachu": "https://knowyourmeme.com/memes/surprised-pikachu",
    "wojak": "https://knowyourmeme.com/memes/wojak-feels-guy",
    "this-is-fine": "https://knowyourmeme.com/memes/this-is-fine",
    "trollface": "https://knowyourmeme.com/memes/trollface",
    "bad-luck-brian": "https://knowyourmeme.com/memes/bad-luck-brian",
    "one-does-not-simply": "https://knowyourmeme.com/memes/one-does-not-simply-walk-into-mordor",
    "hide-the-pain-harold": "https://knowyourmeme.com/memes/hide-the-pain-harold",
    "woman-yelling-at-cat": "https://knowyourmeme.com/memes/woman-yelling-at-a-cat",
    "two-buttons": "https://knowyourmeme.com/memes/daily-struggle-two-buttons",
    "change-my-mind": "https://knowyourmeme.com/memes/steven-crowders-change-my-mind-campus-sign",
    "stonks": "https://knowyourmeme.com/memes/stonks",
    "laughing-leo": "https://knowyourmeme.com/memes/laughing-leo",
    "mocking-spongebob": "https://knowyourmeme.com/memes/mocking-spongebob",
    "roll-safe": "https://knowyourmeme.com/memes/roll-safe",
    "disaster-girl": "https://knowyourmeme.com/memes/disaster-girl",
    "always-has-been": "https://knowyourmeme.com/memes/wait-its-all-ohio-always-has-been",
    "bernie-mittens": "https://knowyourmeme.com/memes/bernie-sanders-in-a-chair",
    "crying-jordan": "https://knowyourmeme.com/memes/crying-michael-jordan",
    "is-this-a-pigeon": "https://knowyourmeme.com/memes/is-this-a-pigeon",
    "gru-plan": "https://knowyourmeme.com/memes/grus-plan",
    "they-dont-know": "https://knowyourmeme.com/memes/they-dont-know",
    "trade-offer": "https://knowyourmeme.com/memes/trade-offer",
    "ight-imma-head-out": "https://knowyourmeme.com/memes/ight-imma-head-out",
    "sad-pablo-escobar": "https://knowyourmeme.com/memes/sad-pablo-escobar",
    "waiting-skeleton": "https://knowyourmeme.com/memes/waiting-skeleton",
    "monkey-puppet": "https://knowyourmeme.com/memes/monkey-puppet",
    "panik-kalm-panik": "https://knowyourmeme.com/memes/panik-kalm-panik",
    "think-mark": "https://knowyourmeme.com/memes/think-mark-think",
    "anakin-padme": "https://knowyourmeme.com/memes/for-the-better-right",
    "buff-doge-vs-cheems": "https://knowyourmeme.com/memes/swole-doge-vs-cheems",
    "we-dont-do-that-here": "https://knowyourmeme.com/memes/we-dont-do-that-here",
    "perhaps-cow": "https://knowyourmeme.com/memes/perhaps",
    "confused-nick-young": "https://knowyourmeme.com/memes/confused-nick-young",
    "evil-kermit": "https://knowyourmeme.com/memes/evil-kermit",
    "but-thats-none-of-my-business": "https://knowyourmeme.com/memes/but-thats-none-of-my-business",
    "uno-draw-25": "https://knowyourmeme.com/memes/uno-draw-25-cards",
    "tom-reading-newspaper": "https://knowyourmeme.com/memes/i-should-buy-a-boat-cat",
    "i-sleep-real-shit": "https://knowyourmeme.com/memes/sleeping-shaq",
    "bro-visited": "https://knowyourmeme.com/memes/bro-visited",
    "first-time": "https://knowyourmeme.com/memes/james-franco-first-time",
    "galaxy-brain": "https://knowyourmeme.com/memes/galaxy-brain",
    "mike-wazowski-explaining": "https://knowyourmeme.com/memes/mike-wazowski-explaining-things",
    "i-bet-hes-thinking-about-other-women": "https://knowyourmeme.com/memes/i-bet-hes-thinking-about-other-women",
    "spiderman-pointing": "https://knowyourmeme.com/memes/spider-man-pointing-at-spider-man",
    "you-guys-are-getting-paid": "https://knowyourmeme.com/memes/you-guys-are-getting-paid",
    "im-in-danger": "https://knowyourmeme.com/memes/im-in-danger",
    "visible-confusion": "https://knowyourmeme.com/memes/visible-confusion",
    "thanos-impossible": "https://knowyourmeme.com/memes/impossible-thanos",
    "why-are-you-running": "https://knowyourmeme.com/memes/why-are-you-running",
    "finally-worthy-opponent": "https://knowyourmeme.com/memes/finally-a-worthy-opponent",
    "thomas-had-never-seen": "https://knowyourmeme.com/memes/thomas-had-never-seen-such-bullshit-before",
    "shrek": "https://knowyourmeme.com/memes/shrek",
    "nyan-cat": "https://knowyourmeme.com/memes/nyan-cat-pop-tart-cat",
    "harambe": "https://knowyourmeme.com/memes/harambe-the-gorilla",
    "arthur-fist": "https://knowyourmeme.com/memes/arthurs-fist",
    "philosoraptor": "https://knowyourmeme.com/memes/philosoraptor",
    "rage-comics": "https://knowyourmeme.com/memes/rage-comics",
    "ancient-aliens": "https://knowyourmeme.com/memes/ancient-aliens",
    "overly-attached-girlfriend": "https://knowyourmeme.com/memes/overly-attached-girlfriend",
    "confession-bear": "https://knowyourmeme.com/memes/confession-bear",
    "scumbag-steve": "https://knowyourmeme.com/memes/scumbag-steve",
    "good-guy-greg": "https://knowyourmeme.com/memes/good-guy-greg",
    "first-world-problems": "https://knowyourmeme.com/memes/first-world-problems",
    "y-u-no": "https://knowyourmeme.com/memes/y-u-no-guy",
    "shut-up-and-take-my-money": "https://knowyourmeme.com/memes/shut-up-and-take-my-money",
    "futurama-fry": "https://knowyourmeme.com/memes/futurama-fry-not-sure-if",
    "conspiracy-keanu": "https://knowyourmeme.com/memes/conspiracy-keanu",
    "the-most-interesting-man": "https://knowyourmeme.com/memes/the-most-interesting-man-in-the-world",
    "condescending-wonka": "https://knowyourmeme.com/memes/condescending-wonka-creepy-wonka",
    "minor-mistake-marvin": "https://knowyourmeme.com/memes/minor-mistake-marvin",
    "matrix-morpheus": "https://knowyourmeme.com/memes/matrix-morpheus",
    "insanity-wolf": "https://knowyourmeme.com/memes/insanity-wolf",
    "socially-awkward-penguin": "https://knowyourmeme.com/memes/socially-awkward-penguin",
    "aint-nobody-got-time": "https://knowyourmeme.com/memes/sweet-brown-aint-nobody-got-time-for-that",
    "ermahgerd": "https://knowyourmeme.com/memes/ermahgerd",
    "yao-ming-face": "https://knowyourmeme.com/memes/yao-ming-face-bitch-please",
    "all-the-things": "https://knowyourmeme.com/memes/x-all-the-y",
    "ceiling-cat": "https://knowyourmeme.com/memes/ceiling-cat",
    "keyboard-cat": "https://knowyourmeme.com/memes/keyboard-cat",
    "advice-dog": "https://knowyourmeme.com/memes/advice-dog",
    "courage-wolf": "https://knowyourmeme.com/memes/courage-wolf",
    "lolcats": "https://knowyourmeme.com/memes/lolcats",
    "cheezburger": "https://knowyourmeme.com/memes/i-can-has-cheezburger",
    "forever-alone": "https://knowyourmeme.com/memes/forever-alone",
    "me-gusta": "https://knowyourmeme.com/memes/me-gusta",
    "cereal-guy": "https://knowyourmeme.com/memes/cereal-guy",
    "poker-face": "https://knowyourmeme.com/memes/poker-face",
    "challenge-accepted": "https://knowyourmeme.com/memes/challenge-accepted",
    "okay-guy": "https://knowyourmeme.com/memes/okay-guy",
    "its-a-trap": "https://knowyourmeme.com/memes/its-a-trap",
    "surprised-patrick": "https://knowyourmeme.com/memes/surprised-patrick",
    "imagination-spongebob": "https://knowyourmeme.com/memes/imagination-spongebob",
    "squidward-window": "https://knowyourmeme.com/memes/squidward-looking-out-the-window",
    "pickle-rick": "https://knowyourmeme.com/memes/pickle-rick",
    "coffin-dance": "https://knowyourmeme.com/memes/coffin-dance-dancing-pallbearers",
    "among-us": "https://knowyourmeme.com/memes/among-us",
    "amogus": "https://knowyourmeme.com/memes/amogus",
    "pogchamp": "https://knowyourmeme.com/memes/pogchamp",
    "ok-boomer": "https://knowyourmeme.com/memes/ok-boomer",
    "karen": "https://knowyourmeme.com/memes/karen",
    "simp": "https://knowyourmeme.com/memes/simp",
    "press-f-to-pay-respects": "https://knowyourmeme.com/memes/press-f-to-pay-respects",
    "big-chungus": "https://knowyourmeme.com/memes/big-chungus",
    "ugandan-knuckles": "https://knowyourmeme.com/memes/ugandan-knuckles",
    "perfectly-balanced": "https://knowyourmeme.com/memes/perfectly-balanced",
    "me-and-the-boys": "https://knowyourmeme.com/memes/me-and-the-boys",
    "ah-shit-here-we-go-again": "https://knowyourmeme.com/memes/ah-shit-here-we-go-again",
    "american-chopper-argument": "https://knowyourmeme.com/memes/american-chopper-argument",
    "blinking-white-guy": "https://knowyourmeme.com/memes/blinking-white-guy",
    "theyre-the-same-picture": "https://knowyourmeme.com/memes/theyre-the-same-picture",
    "confused-math-lady": "https://knowyourmeme.com/memes/math-lady-confused-lady",
    "kombucha-girl": "https://knowyourmeme.com/memes/kombucha-girl",
    "crying-cat": "https://knowyourmeme.com/memes/crying-cat",
    "bongo-cat": "https://knowyourmeme.com/memes/bongo-cat",
    "smudge-the-cat": "https://knowyourmeme.com/memes/smudge-the-cat",
    "sad-keanu": "https://knowyourmeme.com/memes/sad-keanu",
    "uno-reverse": "https://knowyourmeme.com/memes/uno-reverse-card",
    "60s-spiderman": "https://knowyourmeme.com/memes/60s-spider-man",
    "everyone-liked-that": "https://knowyourmeme.com/memes/everyone-liked-that",
    "hello-there": "https://knowyourmeme.com/memes/hello-there",
    "high-ground": "https://knowyourmeme.com/memes/its-over-anakin-i-have-the-high-ground",
    "flappy-bird": "https://knowyourmeme.com/memes/flappy-bird",
    "soyjak": "https://knowyourmeme.com/memes/soy-boy-face-soyjak",
    "chad": "https://knowyourmeme.com/memes/chad",
    "virgin-vs-chad": "https://knowyourmeme.com/memes/virgin-vs-chad",
    "gigachad": "https://knowyourmeme.com/memes/gigachad",
    "deal-with-it": "https://knowyourmeme.com/memes/deal-with-it",
    "u-mad": "https://knowyourmeme.com/memes/u-mad",
    "cool-story-bro": "https://knowyourmeme.com/memes/cool-story-bro",
    "you-dont-say": "https://knowyourmeme.com/memes/you-dont-say",
    "grandma-finds-the-internet": "https://knowyourmeme.com/memes/grandma-finds-the-internet",
    "weird-flex-but-ok": "https://knowyourmeme.com/memes/weird-flex-but-ok",
    "batman-slapping-robin": "https://knowyourmeme.com/memes/my-parents-are-dead-batman-slapping-robin",
    "left-exit-12": "https://knowyourmeme.com/memes/left-exit-12-off-ramp",
    "boardroom-meeting-suggestion": "https://knowyourmeme.com/memes/boardroom-suggestion",
    "epic-handshake": "https://knowyourmeme.com/memes/epic-handshake",
    "hard-to-swallow-pills": "https://knowyourmeme.com/memes/hard-to-swallow-pills",
    "tuxedo-winnie-the-pooh": "https://knowyourmeme.com/memes/tuxedo-winnie-the-pooh",
    "running-away-balloon": "https://knowyourmeme.com/memes/running-away-balloon",
    "slender-man": "https://knowyourmeme.com/memes/slender-man",
    "lenny-face": "https://knowyourmeme.com/memes/lenny-face",
    "dat-boi": "https://knowyourmeme.com/memes/dat-boi",
    "kappa": "https://knowyourmeme.com/memes/kappa",
    "facepalm": "https://knowyourmeme.com/memes/facepalm",
    "cash-me-outside": "https://knowyourmeme.com/memes/cash-me-outside-howbow-dah",
    "baby-yoda": "https://knowyourmeme.com/memes/baby-yoda",
    "vince-mcmahon-reaction": "https://knowyourmeme.com/memes/vince-mcmahon-reaction",
    "unsettled-tom": "https://knowyourmeme.com/memes/unsettled-tom",
    "lisa-simpson-presentation": "https://knowyourmeme.com/memes/lisa-simpsons-presentation",
    "well-yes-but-actually-no": "https://knowyourmeme.com/memes/well-yes-but-actually-no",
    "flex-tape": "https://knowyourmeme.com/memes/flex-tape",
}


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
    """Main function to update view counts."""
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    with open(memes_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']
    print(f"Loaded {len(memes)} memes")
    print("=" * 70)

    session = requests.Session()
    updated_count = 0
    failed_count = 0

    try:
        for i, meme in enumerate(memes, 1):
            meme_id = meme['id']
            meme_name = meme['name']

            print(f"[{i}/{len(memes)}] {meme_name}...", end=" ", flush=True)

            if meme_id not in MEME_URLS:
                print(f"NO URL (keeping {meme['views']:,})")
                failed_count += 1
                continue

            url = MEME_URLS[meme_id]
            views = scrape_views(session, url)

            if views and views > 10000:
                old_views = meme['views']
                meme['views'] = views
                print(f"{old_views:,} -> {views:,}")
                updated_count += 1
            else:
                print(f"NO VIEWS (keeping {meme['views']:,})")
                failed_count += 1

            time.sleep(random.uniform(1, 2))

    except KeyboardInterrupt:
        print("\n\nInterrupted! Saving progress...")

    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"Done! Updated: {updated_count}, Failed: {failed_count}")
    print(f"Saved to {memes_path}")


if __name__ == "__main__":
    main()
