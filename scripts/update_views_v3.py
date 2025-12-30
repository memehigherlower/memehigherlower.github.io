"""
KnowYourMeme View Count Updater v3
Extracts view counts from the dl (definition list) stats section.
The first number in the stats dl is the view count.
"""

import json
import time
import random
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Mapping of meme IDs to their KnowYourMeme search terms
MEME_SEARCH_TERMS = {
    "doge": "doge",
    "distracted-boyfriend": "distracted boyfriend",
    "pepe-the-frog": "pepe the frog",
    "rickroll": "rickroll",
    "success-kid": "success kid",
    "grumpy-cat": "grumpy cat",
    "drake-hotline-bling": "drakeposting",
    "expanding-brain": "expanding brain",
    "surprised-pikachu": "surprised pikachu",
    "wojak": "wojak feels guy",
    "this-is-fine": "this is fine",
    "trollface": "trollface",
    "bad-luck-brian": "bad luck brian",
    "one-does-not-simply": "one does not simply",
    "hide-the-pain-harold": "hide the pain harold",
    "woman-yelling-at-cat": "woman yelling at a cat",
    "two-buttons": "daily struggle two buttons",
    "change-my-mind": "change my mind",
    "stonks": "stonks",
    "laughing-leo": "laughing leo",
    "mocking-spongebob": "mocking spongebob",
    "roll-safe": "roll safe",
    "disaster-girl": "disaster girl",
    "always-has-been": "always has been",
    "bernie-mittens": "bernie sanders mittens",
    "crying-jordan": "crying michael jordan",
    "is-this-a-pigeon": "is this a pigeon",
    "gru-plan": "gru's plan",
    "they-dont-know": "they dont know",
    "trade-offer": "trade offer",
    "ight-imma-head-out": "ight imma head out",
    "sad-pablo-escobar": "sad pablo escobar",
    "waiting-skeleton": "waiting skeleton",
    "monkey-puppet": "monkey puppet",
    "panik-kalm-panik": "panik kalm panik",
    "think-mark": "think mark",
    "anakin-padme": "for the better right",
    "buff-doge-vs-cheems": "swole doge vs cheems",
    "we-dont-do-that-here": "we dont do that here",
    "perhaps-cow": "perhaps cow",
    "confused-nick-young": "confused nick young",
    "evil-kermit": "evil kermit",
    "but-thats-none-of-my-business": "but thats none of my business",
    "uno-draw-25": "uno draw 25",
    "tom-reading-newspaper": "i should buy a boat cat",
    "i-sleep-real-shit": "sleeping shaq",
    "bro-visited": "bro visited",
    "first-time": "james franco first time",
    "galaxy-brain": "galaxy brain",
    "mike-wazowski-explaining": "mike wazowski explaining",
    "i-bet-hes-thinking-about-other-women": "i bet hes thinking about other women",
    "spiderman-pointing": "spider-man pointing",
    "you-guys-are-getting-paid": "you guys are getting paid",
    "im-in-danger": "im in danger",
    "visible-confusion": "visible confusion",
    "thanos-impossible": "impossible thanos",
    "why-are-you-running": "why are you running",
    "finally-worthy-opponent": "finally a worthy opponent",
    "thomas-had-never-seen": "thomas had never seen such bullshit",
    "be-a-lot-cooler-if-you-did": "be a lot cooler if you did",
    "shrek": "shrek",
    "nyan-cat": "nyan cat",
    "harambe": "harambe",
    "arthur-fist": "arthur fist",
    "philosoraptor": "philosoraptor",
    "rage-comics": "rage comics",
    "ancient-aliens": "ancient aliens",
    "overly-attached-girlfriend": "overly attached girlfriend",
    "confession-bear": "confession bear",
    "scumbag-steve": "scumbag steve",
    "good-guy-greg": "good guy greg",
    "first-world-problems": "first world problems",
    "y-u-no": "y u no",
    "shut-up-and-take-my-money": "shut up and take my money",
    "futurama-fry": "futurama fry not sure if",
    "conspiracy-keanu": "conspiracy keanu",
    "the-most-interesting-man": "most interesting man in the world",
    "condescending-wonka": "condescending wonka",
    "minor-mistake-marvin": "minor mistake marvin",
    "matrix-morpheus": "matrix morpheus",
    "insanity-wolf": "insanity wolf",
    "socially-awkward-penguin": "socially awkward penguin",
    "captain-hindsight": "captain hindsight",
    "aint-nobody-got-time": "aint nobody got time for that",
    "ermahgerd": "ermahgerd",
    "yao-ming-face": "yao ming face",
    "all-the-things": "x all the y",
    "ceiling-cat": "ceiling cat",
    "keyboard-cat": "keyboard cat",
    "chemistry-cat": "chemistry cat",
    "business-cat": "business cat",
    "advice-dog": "advice dog",
    "courage-wolf": "courage wolf",
    "lolcats": "lolcats",
    "cheezburger": "i can has cheezburger",
    "forever-alone": "forever alone",
    "me-gusta": "me gusta",
    "cereal-guy": "cereal guy",
    "poker-face": "poker face rage",
    "challenge-accepted": "challenge accepted",
    "okay-guy": "okay guy",
    "its-a-trap": "its a trap",
    "thats-a-paddlin": "thats a paddlin",
    "surprised-patrick": "surprised patrick",
    "imagination-spongebob": "imagination spongebob",
    "krusty-krab-vs-chum-bucket": "krusty krab vs chum bucket",
    "squidward-window": "squidward looking out window",
    "tired-spongebob": "tired spongebob",
    "pickle-rick": "pickle rick",
    "big-brain-time": "big brain time",
    "oh-yeah-its-all-coming-together": "oh yeah its all coming together",
    "no-this-isnt-how-youre-supposed-to-play-the-game": "this isnt how youre supposed to play the game",
    "well-yes-but-actually-no": "well yes but actually no",
    "outstanding-move": "outstanding move",
    "modern-problems-require-modern-solutions": "modern problems require modern solutions",
    "cat-vibing": "vibing cat",
    "coffin-dance": "coffin dance",
    "bonk-go-to-horny-jail": "bonk go to horny jail",
    "among-us": "among us",
    "amogus": "amogus",
    "sus": "sus among us",
    "pog": "pogchamp",
    "pogchamp": "pogchamp",
    "ok-boomer": "ok boomer",
    "karen": "karen meme",
    "simp": "simp",
    "press-f-to-pay-respects": "press f to pay respects",
    "stonks-man": "meme man stonks",
    "big-chungus": "big chungus",
    "ugandan-knuckles": "ugandan knuckles",
    "thanos-snap": "thanos snap",
    "perfectly-balanced": "perfectly balanced",
    "reality-can-be-whatever-i-want": "reality can be whatever i want",
    "i-am-inevitable": "i am inevitable",
    "a-small-price-to-pay": "a small price to pay for salvation",
    "say-sike-right-now": "say sike right now",
    "me-and-the-boys": "me and the boys",
    "ah-shit-here-we-go-again": "ah shit here we go again",
    "you-werent-supposed-to-do-that": "wait thats illegal",
    "sike-thats-the-wrong-number": "thats the wrong number",
    "my-goals-are-beyond-your-understanding": "my goals are beyond your understanding",
    "yes-honey": "yes honey",
    "amateurs": "amateurs comic",
    "american-chopper-argument": "american chopper argument",
    "blinking-white-guy": "blinking white guy",
    "theyre-the-same-picture": "theyre the same picture",
    "why-would-you-say-something-so-controversial": "why would you say something so controversial",
    "confused-math-lady": "math lady confused lady",
    "kombucha-girl": "kombucha girl",
    "crying-cat": "crying cat",
    "polite-cat": "polite cat",
    "bongo-cat": "bongo cat",
    "smudge-the-cat": "smudge the cat",
    "sad-cat": "sad cat",
    "sad-affleck": "sad ben affleck",
    "sad-keanu": "sad keanu",
    "keanu-breathtaking": "youre breathtaking keanu",
    "john-wick": "john wick",
    "matrix-dodge": "matrix dodge",
    "red-pill-blue-pill": "red pill blue pill",
    "uno-reverse": "uno reverse card",
    "no-u": "no u",
    "mega-mind": "megamind no bitches",
    "patrick-wallet": "patrick wallet",
    "patrick-mayonnaise": "is mayonnaise an instrument",
    "bold-and-brash": "bold and brash",
    "60s-spiderman": "60s spider-man",
    "everyone-liked-that": "everyone liked that",
    "thats-what-heroes-do": "because thats what heroes do",
    "carefully-hes-a-hero": "carefully hes a hero",
    "i-see-this-as-an-absolute-win": "i see this as an absolute win",
    "im-gonna-pretend-i-didnt-see-that": "im gonna pretend i didnt see that",
    "skeletor-disturbing-facts": "skeletor disturbing facts",
    "hello-there": "hello there obi wan",
    "high-ground": "i have the high ground",
    "this-is-where-the-fun-begins": "this is where the fun begins",
    "i-love-democracy": "i love democracy",
    "its-treason-then": "its treason then",
    "do-it": "do it palpatine",
    "flappy-bird": "flappy bird",
    "minecraft-creeper": "creeper aw man",
    "elon-musk": "elon musk",
    "mark-zuckerberg": "mark zuckerberg",
    "soyjak": "soyjak",
    "chad": "chad meme",
    "virgin-vs-chad": "virgin vs chad",
    "gigachad": "gigachad",
    "sigma-male": "sigma male grindset",
    "deal-with-it": "deal with it",
    "u-mad": "u mad",
    "cool-story-bro": "cool story bro",
    "come-at-me-bro": "come at me bro",
    "you-dont-say": "you dont say nicolas cage",
    "grandma-finds-the-internet": "grandma finds the internet",
    "weird-flex-but-ok": "weird flex but ok",
    "batman-slapping-robin": "batman slapping robin",
    "left-exit-12": "left exit 12 off ramp",
    "boardroom-meeting-suggestion": "boardroom meeting suggestion",
    "epic-handshake": "epic handshake",
    "hard-to-swallow-pills": "hard to swallow pills",
    "tuxedo-winnie-the-pooh": "tuxedo winnie the pooh",
    "running-away-balloon": "running away balloon",
    "slender-man": "slender man",
    "lenny-face": "lenny face",
    "look-of-disapproval": "look of disapproval",
    "not-bad-obama": "not bad obama",
    "derp": "derp",
    "dat-boi": "dat boi",
    "kappa": "kappa twitch",
    "rage-guy-fffuuu": "rage guy fffuuu",
    "wat": "wat meme",
    "do-you-even-lift": "do you even lift",
    "haters-gonna-hate": "haters gonna hate",
    "yo-dawg-xzibit": "xzibit yo dawg",
    "facepalm": "facepalm",
    "cash-me-outside": "cash me outside",
    "he-protec-but-he-also-attac": "he protec but he also attac",
    "high-expectations-asian-father": "high expectations asian father",
    "its-over-9000": "its over 9000",
    "leeroy-jenkins": "leeroy jenkins",
    "the-cake-is-a-lie": "the cake is a lie",
    "impossibru": "impossibru",
    "feels-bad-man": "feels bad man",
    "honey-badger": "honey badger dont care",
    "bear-grylls": "bear grylls",
    "successful-black-man": "successful black man",
    "leonardo-dicaprio-cheers": "leonardo dicaprio cheers",
    "oprah-you-get-a": "oprah you get a",
    "dinkleberg": "dinkleberg",
    "third-world-skeptical-kid": "third world skeptical kid",
    "awkward-moment-seal": "awkward moment seal",
    "mr-bean-waiting": "mr bean waiting",
    "unsettled-tom": "unsettled tom",
    "mike-wazowski-face-swap": "mike wazowski face swap",
    "guy-explaining": "guy explaining",
    "types-of-headaches": "types of headaches",
    "inhaling-seagull": "inhaling seagull",
    "polish-jerry": "polish jerry",
    "lisa-simpson-presentation": "lisa simpson presentation",
    "no-no-hes-got-a-point": "no no hes got a point",
    "baby-yoda": "baby yoda",
    "vince-mcmahon-reaction": "vince mcmahon reaction",
    "skyrim-skill-tree": "skyrim skill tree",
    "the-scroll-of-truth": "scroll of truth",
    "flex-tape": "flex tape",
}


def search_kym(session: requests.Session, search_term: str) -> str:
    """Search KnowYourMeme and return the first meme result URL."""
    search_url = f"https://knowyourmeme.com/search?q={requests.utils.quote(search_term)}"

    try:
        response = session.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for meme entry links in search results
        for link in soup.select('a[href*="/memes/"]'):
            href = link.get('href', '')
            # Skip non-meme pages
            if '/memes/people/' in href or '/memes/sites/' in href or '/memes/subcultures/' in href:
                continue
            if '/memes/' in href:
                if href.startswith('/'):
                    return f"https://knowyourmeme.com{href}"
                return href

    except Exception as e:
        print(f"Search error: {e}")

    return None


def extract_views_from_page(soup: BeautifulSoup) -> int:
    """
    Extract view count from KnowYourMeme page.
    The views are in a <dl> element - first large number is the view count.
    """
    try:
        # Find all dl elements (definition lists containing stats)
        dls = soup.select('dl')

        for dl in dls:
            text = dl.get_text()
            # Look for numbers with commas (like 14,589,348)
            numbers = re.findall(r'(\d{1,3}(?:,\d{3})+)', text)

            if numbers:
                # The first large number is typically the view count
                for num_str in numbers:
                    views = int(num_str.replace(',', ''))
                    # View counts are typically > 10,000
                    if views > 10000:
                        return views

        # Fallback: search entire page for large comma-separated numbers
        page_text = soup.get_text()
        numbers = re.findall(r'(\d{1,3}(?:,\d{3}){2,})', page_text)  # At least 2 comma groups (millions)
        if numbers:
            views_list = [int(n.replace(',', '')) for n in numbers]
            # Return the largest reasonable number
            reasonable = [v for v in views_list if 10000 < v < 1000000000]
            if reasonable:
                return max(reasonable)

    except Exception as e:
        print(f"Error extracting views: {e}")

    return None


def scrape_meme_views(session: requests.Session, meme_url: str) -> int:
    """Scrape view count from a KnowYourMeme meme page."""
    try:
        response = session.get(meme_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_views_from_page(soup)

    except Exception as e:
        print(f"Error: {e}")

    return None


def main():
    """Main function to update view counts."""
    memes_path = Path(__file__).parent.parent / 'src' / 'data' / 'memes.json'

    # Load existing memes
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

            # Get search term
            search_term = MEME_SEARCH_TERMS.get(meme_id, meme_name.lower())

            print(f"[{i}/{len(memes)}] {meme_name}...", end=" ", flush=True)

            # Search for the meme
            meme_url = search_kym(session, search_term)

            if not meme_url:
                print(f"NOT FOUND (keeping {meme['views']:,})")
                failed_count += 1
                time.sleep(random.uniform(1, 2))
                continue

            # Scrape the view count
            views = scrape_meme_views(session, meme_url)

            if views and views > 10000:
                old_views = meme['views']
                meme['views'] = views
                print(f"{old_views:,} -> {views:,}")
                updated_count += 1
            else:
                print(f"NO VIEWS (keeping {meme['views']:,})")
                failed_count += 1

            # Rate limiting
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
