"""
KnowYourMeme View Count Updater
This script updates the view counts for all memes in memes.json by scraping KnowYourMeme.

Usage:
  1. Install dependencies: pip install selenium webdriver-manager beautifulsoup4
  2. Run: python update_views.py
"""

import json
import time
import random
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# Mapping of meme IDs to their KnowYourMeme URLs
MEME_URLS = {
    "doge": "https://knowyourmeme.com/memes/doge",
    "distracted-boyfriend": "https://knowyourmeme.com/memes/distracted-boyfriend",
    "pepe-the-frog": "https://knowyourmeme.com/memes/pepe-the-frog",
    "rickroll": "https://knowyourmeme.com/memes/rickroll",
    "success-kid": "https://knowyourmeme.com/memes/success-kid",
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
    "be-a-lot-cooler-if-you-did": "https://knowyourmeme.com/memes/itd-be-a-lot-cooler-if-you-did",
    "shrek": "https://knowyourmeme.com/memes/shrek",
    "nyan-cat": "https://knowyourmeme.com/memes/nyan-cat",
    "harambe": "https://knowyourmeme.com/memes/harambe-the-gorilla",
    "arthur-fist": "https://knowyourmeme.com/memes/arthur-fist",
    "harold-pain": "https://knowyourmeme.com/memes/hide-the-pain-harold",
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
    "captain-hindsight": "https://knowyourmeme.com/memes/captain-hindsight",
    "aint-nobody-got-time": "https://knowyourmeme.com/memes/sweet-brown-aint-nobody-got-time-for-that",
    "ermahgerd": "https://knowyourmeme.com/memes/ermahgerd",
    "yao-ming-face": "https://knowyourmeme.com/memes/yao-ming-face-bitch-please",
    "all-the-things": "https://knowyourmeme.com/memes/x-all-the-y",
    "ceiling-cat": "https://knowyourmeme.com/memes/ceiling-cat",
    "keyboard-cat": "https://knowyourmeme.com/memes/keyboard-cat",
    "chemistry-cat": "https://knowyourmeme.com/memes/chemistry-cat",
    "business-cat": "https://knowyourmeme.com/memes/business-cat",
    "chemistry-dog": "https://knowyourmeme.com/memes/chemistry-dog",
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
    "thats-a-paddlin": "https://knowyourmeme.com/memes/thats-a-paddlin",
    "surprised-patrick": "https://knowyourmeme.com/memes/surprised-patrick",
    "imagination-spongebob": "https://knowyourmeme.com/memes/imagination-spongebob",
    "krusty-krab-vs-chum-bucket": "https://knowyourmeme.com/memes/krusty-krab-vs-chum-bucket",
    "squidward-window": "https://knowyourmeme.com/memes/squidward-looking-out-the-window",
    "tired-spongebob": "https://knowyourmeme.com/memes/tired-spongebob",
    "pickle-rick": "https://knowyourmeme.com/memes/pickle-rick",
    "big-brain-time": "https://knowyourmeme.com/memes/yeah-this-is-big-brain-time",
    "oh-yeah-its-all-coming-together": "https://knowyourmeme.com/memes/oh-yeah-its-all-coming-together",
    "no-this-isnt-how-youre-supposed-to-play-the-game": "https://knowyourmeme.com/memes/no-this-isnt-how-youre-supposed-to-play-the-game",
    "well-yes-but-actually-no": "https://knowyourmeme.com/memes/well-yes-but-actually-no",
    "outstanding-move": "https://knowyourmeme.com/memes/outstanding-move",
    "modern-problems-require-modern-solutions": "https://knowyourmeme.com/memes/modern-problems-require-modern-solutions",
    "cat-vibing": "https://knowyourmeme.com/memes/vibing-cat",
    "coffin-dance": "https://knowyourmeme.com/memes/coffin-dance-dancing-pallbearers",
    "bonk-go-to-horny-jail": "https://knowyourmeme.com/memes/bonk-go-to-horny-jail",
    "among-us": "https://knowyourmeme.com/memes/among-us",
    "amogus": "https://knowyourmeme.com/memes/amogus",
    "sus": "https://knowyourmeme.com/memes/sus-among-us",
    "pog": "https://knowyourmeme.com/memes/pogchamp",
    "pogchamp": "https://knowyourmeme.com/memes/pogchamp",
    "ok-boomer": "https://knowyourmeme.com/memes/ok-boomer",
    "karen": "https://knowyourmeme.com/memes/karen",
    "simp": "https://knowyourmeme.com/memes/simp",
    "press-f-to-pay-respects": "https://knowyourmeme.com/memes/press-f-to-pay-respects",
    "stonks-man": "https://knowyourmeme.com/memes/meme-man",
    "big-chungus": "https://knowyourmeme.com/memes/big-chungus",
    "ugandan-knuckles": "https://knowyourmeme.com/memes/ugandan-knuckles",
    "thanos-snap": "https://knowyourmeme.com/memes/thanos-snap",
    "perfectly-balanced": "https://knowyourmeme.com/memes/perfectly-balanced",
    "reality-can-be-whatever-i-want": "https://knowyourmeme.com/memes/reality-can-be-whatever-i-want",
    "i-am-inevitable": "https://knowyourmeme.com/memes/i-am-inevitable",
    "a-small-price-to-pay": "https://knowyourmeme.com/memes/a-small-price-to-pay-for-salvation",
    "say-sike-right-now": "https://knowyourmeme.com/memes/say-sike-right-now",
    "me-and-the-boys": "https://knowyourmeme.com/memes/me-and-the-boys",
    "ah-shit-here-we-go-again": "https://knowyourmeme.com/memes/ah-shit-here-we-go-again",
    "you-werent-supposed-to-do-that": "https://knowyourmeme.com/memes/wait-thats-illegal",
    "sike-thats-the-wrong-number": "https://knowyourmeme.com/memes/thats-the-wrong-number",
    "my-goals-are-beyond-your-understanding": "https://knowyourmeme.com/memes/my-goals-are-beyond-your-understanding",
    "yes-honey": "https://knowyourmeme.com/memes/yes-honey",
    "gaming-setup": "https://knowyourmeme.com/memes/average-fan-vs-average-enjoyer",
    "amateurs": "https://knowyourmeme.com/memes/amateurs-comic",
    "american-chopper-argument": "https://knowyourmeme.com/memes/american-chopper-argument",
    "blinking-white-guy": "https://knowyourmeme.com/memes/blinking-white-guy",
    "theyre-the-same-picture": "https://knowyourmeme.com/memes/theyre-the-same-picture",
    "corporate-needs-you-to-find-the-difference": "https://knowyourmeme.com/memes/theyre-the-same-picture",
    "why-would-you-say-something-so-controversial": "https://knowyourmeme.com/memes/why-would-you-say-something-so-controversial-yet-so-brave",
    "confused-math-lady": "https://knowyourmeme.com/memes/math-lady-confused-lady",
    "kombucha-girl": "https://knowyourmeme.com/memes/kombucha-girl",
    "crying-cat": "https://knowyourmeme.com/memes/crying-cat",
    "polite-cat": "https://knowyourmeme.com/memes/beluga-the-polite-cat",
    "thumbs-up-cat": "https://knowyourmeme.com/memes/thumbs-up-crying-cat",
    "screaming-cat": "https://knowyourmeme.com/memes/screaming-externally",
    "standing-cat": "https://knowyourmeme.com/memes/standing-cat",
    "bongo-cat": "https://knowyourmeme.com/memes/bongo-cat",
    "cat-in-the-hat-bat": "https://knowyourmeme.com/memes/cat-in-the-hat-bat",
    "smudge-the-cat": "https://knowyourmeme.com/memes/smudge-the-cat",
    "sad-cat": "https://knowyourmeme.com/memes/sad-cat",
    "sad-affleck": "https://knowyourmeme.com/memes/sad-ben-affleck",
    "sad-keanu": "https://knowyourmeme.com/memes/sad-keanu",
    "keanu-breathtaking": "https://knowyourmeme.com/memes/keanu-reeves-youre-breathtaking",
    "john-wick": "https://knowyourmeme.com/memes/subcultures/john-wick",
    "matrix-dodge": "https://knowyourmeme.com/memes/the-matrix",
    "red-pill-blue-pill": "https://knowyourmeme.com/memes/red-pill-blue-pill",
    "he-is-the-one": "https://knowyourmeme.com/memes/the-matrix",
    "take-my-money": "https://knowyourmeme.com/memes/shut-up-and-take-my-money",
    "fry-not-sure": "https://knowyourmeme.com/memes/futurama-fry-not-sure-if",
    "zoidberg-why-not": "https://knowyourmeme.com/memes/why-not-zoidberg",
    "leela-disappointed": "https://knowyourmeme.com/memes/futurama-disappointed",
    "draw-25": "https://knowyourmeme.com/memes/uno-draw-25-cards",
    "uno-reverse": "https://knowyourmeme.com/memes/uno-reverse-card",
    "no-u": "https://knowyourmeme.com/memes/no-u",
    "mega-mind": "https://knowyourmeme.com/memes/no-bitches",
    "spongebob-imagination": "https://knowyourmeme.com/memes/imagination-spongebob",
    "patrick-wallet": "https://knowyourmeme.com/memes/patrick-stars-wallet",
    "patrick-mayonnaise": "https://knowyourmeme.com/memes/is-mayonnaise-an-instrument",
    "krabby-patty": "https://knowyourmeme.com/memes/subcultures/spongebob-squarepants",
    "bold-and-brash": "https://knowyourmeme.com/memes/bold-and-brash",
    "60s-spiderman": "https://knowyourmeme.com/memes/60s-spider-man",
    "everyone-liked-that": "https://knowyourmeme.com/memes/everyone-liked-that",
    "thats-what-heroes-do": "https://knowyourmeme.com/memes/because-thats-what-heroes-do",
    "carefully-hes-a-hero": "https://knowyourmeme.com/memes/carefully-hes-a-hero",
    "i-see-this-as-an-absolute-win": "https://knowyourmeme.com/memes/i-see-this-as-an-absolute-win",
    "im-gonna-pretend-i-didnt-see-that": "https://knowyourmeme.com/memes/im-gonna-pretend-i-didnt-see-that",
    "skeletor-disturbing-facts": "https://knowyourmeme.com/memes/skeletor-disturbing-facts",
    "seal-of-approval": "https://knowyourmeme.com/memes/awkward-moment-seal",
    "suspicious-fry": "https://knowyourmeme.com/memes/futurama-fry-not-sure-if",
    "interesting": "https://knowyourmeme.com/memes/interesting",
    "ironic-palpatine": "https://knowyourmeme.com/memes/the-tragedy-of-darth-plagueis-the-wise",
    "hello-there": "https://knowyourmeme.com/memes/hello-there",
    "high-ground": "https://knowyourmeme.com/memes/i-have-the-high-ground",
    "this-is-where-the-fun-begins": "https://knowyourmeme.com/memes/this-is-where-the-fun-begins",
    "i-love-democracy": "https://knowyourmeme.com/memes/i-love-democracy",
    "its-treason-then": "https://knowyourmeme.com/memes/its-treason-then",
    "do-it": "https://knowyourmeme.com/memes/do-it",
    "angry-birds-pig": "https://knowyourmeme.com/memes/subcultures/angry-birds",
    "flappy-bird": "https://knowyourmeme.com/memes/flappy-bird",
    "minecraft-creeper": "https://knowyourmeme.com/memes/creeper-aw-man",
    "steve-minecraft": "https://knowyourmeme.com/memes/subcultures/minecraft",
    "elon-musk": "https://knowyourmeme.com/memes/people/elon-musk",
    "mark-zuckerberg": "https://knowyourmeme.com/memes/people/mark-zuckerberg",
    "soyjak": "https://knowyourmeme.com/memes/soy-boy-face-soyjak",
    "chad": "https://knowyourmeme.com/memes/chad",
    "virgin-vs-chad": "https://knowyourmeme.com/memes/virgin-vs-chad",
    "gigachad": "https://knowyourmeme.com/memes/gigachad",
    "sigma-male": "https://knowyourmeme.com/memes/sigma-male-grindset",
    "based": "https://knowyourmeme.com/memes/based-and-redpilled",
    "cringe": "https://knowyourmeme.com/memes/cringe",
    "cope": "https://knowyourmeme.com/memes/cope",
    "seethe": "https://knowyourmeme.com/memes/cope-and-seethe",
    "ratio": "https://knowyourmeme.com/memes/ratio",
    "l-plus-ratio": "https://knowyourmeme.com/memes/ratio",
    "didnt-ask": "https://knowyourmeme.com/memes/who-asked-who-cares",
    "nobody-asked": "https://knowyourmeme.com/memes/who-asked-who-cares",
    "who-asked": "https://knowyourmeme.com/memes/who-asked-who-cares",
    "deal-with-it": "https://knowyourmeme.com/memes/deal-with-it",
    "u-mad": "https://knowyourmeme.com/memes/u-mad",
    "problem": "https://knowyourmeme.com/memes/trollface",
    "cool-story-bro": "https://knowyourmeme.com/memes/cool-story-bro",
    "come-at-me-bro": "https://knowyourmeme.com/memes/come-at-me-bro",
    "you-dont-say": "https://knowyourmeme.com/memes/you-dont-say",
    "dont-tell-me-what-to-do": "https://knowyourmeme.com/memes/first-world-anarchists",
    "if-you-know-what-i-mean": "https://knowyourmeme.com/memes/if-you-know-what-i-mean",
    "forever-alone-christmas": "https://knowyourmeme.com/memes/forever-alone",
    "i-lied": "https://knowyourmeme.com/memes/i-lied",
    "what-if-i-told-you": "https://knowyourmeme.com/memes/matrix-morpheus",
    "grandma-finds-the-internet": "https://knowyourmeme.com/memes/grandma-finds-the-internet",
    "weird-flex-but-ok": "https://knowyourmeme.com/memes/weird-flex-but-ok",
}


def setup_driver():
    """Setup Selenium WebDriver with headless Chrome."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def extract_views(soup: BeautifulSoup) -> int:
    """Extract view count from KnowYourMeme page."""
    try:
        # Method 1: Look for views in the aside stats
        aside = soup.select_one('aside')
        if aside:
            text = aside.get_text()
            # Look for patterns like "12,345,678 Views" or "12.3M Views"
            match = re.search(r'([\d,]+)\s*Views', text, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))

            # Look for abbreviated format like "12.3M"
            match = re.search(r'([\d.]+)([KMB])\s*Views', text, re.IGNORECASE)
            if match:
                num = float(match.group(1))
                suffix = match.group(2).upper()
                multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                return int(num * multipliers.get(suffix, 1))

        # Method 2: Look in meta tags or structured data
        scripts = soup.select('script[type="application/ld+json"]')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'interactionCount' in data:
                    return int(data['interactionCount'])
            except:
                pass

        # Method 3: Look for any element with "views" text
        for elem in soup.find_all(text=re.compile(r'[\d,]+\s*views', re.IGNORECASE)):
            match = re.search(r'([\d,]+)\s*views', elem, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))

    except Exception as e:
        print(f"Error extracting views: {e}")

    return None


def scrape_view_count(driver, url: str) -> int:
    """Scrape the view count from a KnowYourMeme page."""
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))  # Respectful delay

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        views = extract_views(soup)

        if views:
            return views

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return None


def main():
    """Main function to update view counts."""
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    # Load existing memes
    with open(memes_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memes = data['memes']
    print(f"Loaded {len(memes)} memes")

    # Setup driver
    print("Starting browser...")
    driver = setup_driver()

    updated_count = 0
    failed_count = 0

    try:
        for i, meme in enumerate(memes, 1):
            meme_id = meme['id']

            if meme_id not in MEME_URLS:
                print(f"[{i}/{len(memes)}] {meme['name']}: No URL mapping, skipping")
                failed_count += 1
                continue

            url = MEME_URLS[meme_id]
            print(f"[{i}/{len(memes)}] Scraping {meme['name']}...")

            views = scrape_view_count(driver, url)

            if views:
                old_views = meme['views']
                meme['views'] = views
                print(f"  -> Updated: {old_views:,} -> {views:,}")
                updated_count += 1
            else:
                print(f"  -> Failed to get views, keeping existing: {meme['views']:,}")
                failed_count += 1

            # Rate limiting - be respectful to the server
            time.sleep(random.uniform(2, 4))

    finally:
        driver.quit()

    # Save updated data
    data['memes'] = memes
    data['lastUpdated'] = time.strftime("%Y-%m-%d")

    with open(memes_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Updated {updated_count} memes, {failed_count} failed/skipped")
    print(f"Saved to {memes_path}")


if __name__ == "__main__":
    main()
