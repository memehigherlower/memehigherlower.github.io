"""
Meme Image Downloader
Downloads meme images from various sources and saves them locally.
Run this script to populate the public/images/memes/ folder.

Usage:
  python download_images.py
"""

import json
import os
import requests
import time
from pathlib import Path
from urllib.parse import urlparse

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MEMES_JSON_PATH = PROJECT_ROOT / "src" / "data" / "memes.json"
OUTPUT_DIR = PROJECT_ROOT / "public" / "images" / "memes"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

# Alternative image sources for memes (more reliable URLs)
# Using a mix of sources: Imgflip direct template URLs and other reliable hosts
ALTERNATIVE_URLS = {
    # Working Imgflip URLs (verified template IDs)
    "doge": "https://i.imgflip.com/4t0m5.jpg",
    "distracted-boyfriend": "https://i.imgflip.com/1ur9b0.jpg",
    "grumpy-cat": "https://i.imgflip.com/8p0a.jpg",
    "success-kid": "https://i.imgflip.com/1bhk.jpg",
    "pepe-the-frog": "https://i.kym-cdn.com/entries/icons/original/000/017/618/pepefroggie.jpg",
    "drake-hotline-bling": "https://i.imgflip.com/30b1gx.jpg",
    "expanding-brain": "https://i.imgflip.com/1jwhww.jpg",
    "surprised-pikachu": "https://i.imgflip.com/2kbn1e.jpg",
    "wojak": "https://i.kym-cdn.com/entries/icons/original/000/018/433/wojak.jpg",
    "stonks": "https://i.imgflip.com/3388rw.png",
    "this-is-fine": "https://i.imgflip.com/wxica.jpg",
    "two-buttons": "https://i.imgflip.com/1g8my4.jpg",
    "woman-yelling-at-cat": "https://i.imgflip.com/345v97.jpg",
    "hide-the-pain-harold": "https://i.imgflip.com/gk5el.jpg",
    "bad-luck-brian": "https://i.imgflip.com/2/1bip.jpg",
    "one-does-not-simply": "https://i.imgflip.com/1bij.jpg",
    "change-my-mind": "https://i.imgflip.com/24y43o.jpg",
    "is-this-a-pigeon": "https://i.imgflip.com/1o00in.jpg",
    "roll-safe": "https://i.imgflip.com/1h7in3.jpg",
    "mocking-spongebob": "https://i.imgflip.com/1otk96.jpg",
    "ancient-aliens": "https://i.imgflip.com/26am.jpg",
    "disaster-girl": "https://i.imgflip.com/23ls.jpg",
    "left-exit-12": "https://i.kym-cdn.com/entries/icons/original/000/025/086/car.jpg",
    "spiderman-pointing": "https://i.imgflip.com/1tkjq9.jpg",
    "always-has-been": "https://imgflip.com/s/meme/Always-Has-Been.png",
    "bernie-mittens": "https://i.kym-cdn.com/entries/icons/original/000/036/345/EsMANJkW4AYbmvv.jpeg",
    "they-dont-know": "https://i.kym-cdn.com/entries/icons/original/000/016/183/Iwish.jpg",
    "ight-imma-head-out": "https://i.kym-cdn.com/entries/icons/original/000/030/967/spongebob.jpg",
    "gru-plan": "https://imgflip.com/s/meme/Grus-Plan.jpg",
    "trade-offer": "https://i.imgflip.com/54hjww.jpg",
    "gigachad": "https://i.kym-cdn.com/entries/icons/original/000/026/152/gigachadd.jpg",
    "buff-doge-vs-cheems": "https://i.imgflip.com/43a45p.png",
    "you-guys-are-getting-paid": "https://i.imgflip.com/2xscjb.png",
    "uno-draw-25": "https://i.imgflip.com/3lmzyx.jpg",
    "batman-slapping-robin": "https://i.imgflip.com/9ehk.jpg",
    "panik-kalm-panik": "https://i.imgflip.com/3qqcim.png",
    "think-mark": "https://i.kym-cdn.com/entries/icons/original/000/037/158/thinkmarkthumbnail.PNG",
    "boardroom-meeting": "https://i.kym-cdn.com/entries/icons/original/000/012/066/Boardroom_Suggestion_Icon.png",
    "finding-neverland": "https://i.kym-cdn.com/entries/icons/original/000/015/309/5xksc.jpg",
    "waiting-skeleton": "https://i.imgflip.com/2fm6x.jpg",
    "epic-handshake": "https://i.imgflip.com/28j0te.jpg",
    "hard-to-swallow-pills": "https://imgflip.com/s/meme/Hard-To-Swallow-Pills.jpg",
    "they-are-the-same-picture": "https://i.imgflip.com/2za3u1.jpg",
    "sad-pablo-escobar": "https://i.imgflip.com/1c1uej.jpg",
    "evil-kermit": "https://i.imgflip.com/1e7ql7.jpg",
    "tuxedo-winnie-the-pooh": "https://i.imgflip.com/2ybua0.png",
    "monkey-puppet": "https://i.imgflip.com/2gnnjh.jpg",
    "running-away-balloon": "https://i.kym-cdn.com/entries/icons/original/000/031/623/opportunities.jpg",
    "rickroll": "https://i.kym-cdn.com/entries/icons/original/000/000/007/bd6.jpg",
    # Memes 51-190 (Using i.imgflip.com/s/meme/ format and verified URLs)
    "trollface": "https://i.kym-cdn.com/entries/icons/original/000/000/091/TrollFace.jpg",
    "forever-alone": "https://i.imgflip.com/2/1bh4.jpg",
    "me-gusta": "https://i.kym-cdn.com/entries/icons/original/000/002/252/NoMeGusta.jpg",
    "big-chungus": "https://i.kym-cdn.com/entries/icons/original/000/027/843/chungcover.jpg",
    "slender-man": "https://i.imgflip.com/2/6fg2.jpg",
    "lenny-face": "https://i.kym-cdn.com/entries/icons/original/000/011/764/LennyFace.jpg",
    "hello-there": "https://i.kym-cdn.com/entries/icons/original/000/029/079/hellothere.jpg",
    "ermahgerd": "https://i.kym-cdn.com/entries/icons/original/000/009/479/Ermahgerd.jpg",
    "ugandan-knuckles": "https://i.kym-cdn.com/entries/icons/original/000/025/067/ugandanknuck.jpg",
    "yao-ming-face": "https://i.imgflip.com/2/2c47.jpg",
    "y-u-no": "https://i.imgflip.com/2/1bh3.jpg",
    "overly-attached-girlfriend": "https://i.imgflip.com/2/25w8.jpg",
    "scumbag-steve": "https://i.imgflip.com/2/1bgy.jpg",
    "you-dont-say": "https://i.imgflip.com/2/bun6.jpg",
    "look-of-disapproval": "https://i.kym-cdn.com/entries/icons/original/000/000/428/1.jpg",
    "ridiculously-photogenic-guy": "https://i.kym-cdn.com/entries/icons/original/000/009/754/PhotogenicGuy.jpg",
    "good-guy-greg": "https://i.imgflip.com/2/1bgx.jpg",
    "not-bad-obama": "https://i.kym-cdn.com/entries/icons/original/000/006/151/ObamaNotBad.jpg",
    "derp": "https://i.imgflip.com/2/hagp.jpg",
    "okay-guy": "https://i.kym-cdn.com/entries/icons/original/000/003/617/OkayGuy.jpg",
    "press-f": "https://i.kym-cdn.com/entries/icons/original/000/017/039/pressf.jpg",
    "dat-boi": "https://i.kym-cdn.com/entries/icons/original/000/020/401/HereDatBoi.jpg",
    "philosoraptor": "https://i.imgflip.com/2/1bgs.jpg",
    "harambe": "https://i.kym-cdn.com/entries/icons/original/000/020/605/Harambe.jpg",
    "kappa": "https://i.kym-cdn.com/entries/icons/original/000/017/403/218_copy.jpg",
    "rage-guy": "https://i.kym-cdn.com/entries/icons/original/000/000/063/Rage.jpg",
    "wat": "https://i.imgflip.com/2/2634p.jpg",
    "omae-wa-mou-shindeiru": "https://i.kym-cdn.com/entries/icons/original/000/012/134/maxresdefault.jpg",
    "60s-spiderman": "https://i.imgflip.com/2/tas1.jpg",
    "sad-keanu": "https://i.kym-cdn.com/entries/icons/original/000/002/862/SadKeanu.jpg",
    "do-you-even-lift": "https://i.kym-cdn.com/entries/icons/original/000/009/740/DoULift.jpg",
    "haters-gonna-hate": "https://i.kym-cdn.com/entries/icons/original/000/001/945/haters.jpg",
    "yo-dawg": "https://i.imgflip.com/2/26hg.jpg",
    "most-interesting-man": "https://i.kym-cdn.com/entries/icons/original/000/002/598/InterestingMan.jpg",
    "challenge-accepted": "https://i.kym-cdn.com/entries/icons/original/000/004/457/challenge.jpg",
    "nyan-cat": "https://i.kym-cdn.com/entries/icons/original/000/005/608/nyan-cat-01-625x450.jpg",
    "facepalm": "https://i.imgflip.com/2/wczz.jpg",
    "deal-with-it": "https://i.imgflip.com/77ogp.jpg",
    "cash-me-outside": "https://i.kym-cdn.com/entries/icons/original/000/021/985/image.png",
    "i-know-that-feel": "https://i.kym-cdn.com/entries/icons/original/000/005/393/IKIFEEL.jpg",
    "futurama-fry": "https://i.kym-cdn.com/entries/icons/original/000/006/026/NOTSUREIF.jpg",
    "socially-awkward-penguin": "https://i.imgflip.com/2/1bh0.jpg",
    "first-world-problems": "https://i.imgflip.com/2/1bhf.jpg",
    "virgin-vs-chad": "https://i.imgflip.com/3xnk83.png",
    "he-protec-he-attac": "https://i.kym-cdn.com/entries/icons/original/000/022/574/a7c.jpg",
    "karen": "https://i.kym-cdn.com/entries/icons/original/000/027/963/karenimg.jpg",
    "high-expectations-asian-father": "https://i.imgflip.com/2/1bhz.jpg",
    "but-thats-none-of-my-business": "https://i.imgflip.com/2/9sw43.jpg",
    "its-over-9000": "https://i.kym-cdn.com/entries/icons/original/000/000/056/itsover1000.jpg",
    "leeroy-jenkins": "https://i.kym-cdn.com/entries/icons/original/000/000/191/leeroy-jenkins.jpg",
    "the-cake-is-a-lie": "https://i.kym-cdn.com/entries/icons/original/000/001/707/thecakeisalie.jpg",
    "impossibru": "https://i.kym-cdn.com/entries/icons/original/000/004/918/imposibru.jpg",
    "insanity-wolf": "https://i.imgflip.com/2/1bgu.jpg",
    "feels-bad-man": "https://i.kym-cdn.com/entries/icons/original/000/002/830/sad_frog.jpg",
    "dont-talk-to-me-or-my-son": "https://i.kym-cdn.com/entries/icons/original/000/019/798/donttalktome.jpg",
    "u-mad": "https://i.kym-cdn.com/entries/icons/original/000/001/445/umad_.jpg",
    "soyjak": "https://i.kym-cdn.com/photos/images/original/001/330/809/d90.png",
    "honey-badger": "https://i.imgflip.com/mgwrj.jpg",
    "nine-plus-ten": "https://i.kym-cdn.com/entries/icons/original/000/016/998/You_stupid_vine_(what's_9_10)_0-2_screenshot.jpg",
    "weird-flex-but-ok": "https://i.imgflip.com/2m9ulw.jpg",
    "shut-up-and-take-my-money": "https://i.imgflip.com/2/3si4.jpg",
    "courage-wolf": "https://i.imgflip.com/2/1bgt.jpg",
    "yes-this-is-dog": "https://i.imgflip.com/322k.jpg",
    "gangnam-style": "https://i.kym-cdn.com/entries/icons/original/000/010/964/gangnamstyle.jpg",
    "cool-story-bro": "https://i.kym-cdn.com/entries/icons/original/000/000/346/COOLSTORY.jpg",
    "aint-nobody-got-time": "https://i.imgflip.com/2/9hhr.jpg",
    "all-the-things": "https://i.imgflip.com/2/4pxv0.jpg",
    "bear-grylls": "https://i.imgflip.com/2/1bho.jpg",
    "cereal-guy": "https://imgflip.com/s/meme/Cereal-Guy.jpg",
    "successful-black-man": "https://i.imgflip.com/2/1bhl.jpg",
    "darth-plagueis": "https://static.wikia.nocookie.net/starwars/images/9/9a/Palp_trustme.jpg",
    "confused-math-lady": "https://i.imgflip.com/1c81c1.jpg",
    "leonardo-dicaprio-cheers": "https://i.kym-cdn.com/entries/icons/original/000/034/858/Untitled-1.png",
    "oprah-you-get-a": "https://i.kym-cdn.com/entries/icons/original/000/012/809/oprah-free-car.gif",
    "arthur-fist": "https://i.imgflip.com/2/1866qe.jpg",
    "willy-wonka": "https://i.imgflip.com/2/1bim.jpg",
    "dinkleberg": "https://i.kym-cdn.com/entries/icons/original/000/004/192/Dinkleberg.jpg",
    "matrix-morpheus": "https://i.imgflip.com/2/25w3.jpg",
    "conspiracy-keanu": "https://i.imgflip.com/2/1bin.jpg",
    "third-world-skeptical-kid": "https://imgflip.com/s/meme/Third-World-Skeptical-Kid.jpg",
    "morpheus-blue-red-pill": "https://i.imgflip.com/31a6wo.jpg",
    "awkward-moment-seal": "https://i.imgflip.com/2/86vlk.jpg",
    "minor-mistake-marvin": "https://i.imgflip.com/2/czes2.jpg",
    "mr-bean-waiting": "https://i.kym-cdn.com/entries/icons/original/000/054/803/mrbeancover.jpg",
    "surprised-tom": "https://i.imgflip.com/2wkncm.jpg",
    "unsettled-tom": "https://i.kym-cdn.com/entries/icons/original/000/028/861/cover3.jpg",
    "mike-wazowski-face-swap": "https://i.kym-cdn.com/entries/icons/original/000/031/003/cover3.jpg",
    "bongo-cat": "https://i.kym-cdn.com/entries/icons/original/000/027/115/maxresdefault.jpg",
    "crying-michael-jordan": "https://i.kym-cdn.com/entries/icons/original/000/017/966/cryingmj.jpg",
    "young-michael-scott": "https://i.imgflip.com/3ksxaa.png",
    "grandma-finds-the-internet": "https://i.kym-cdn.com/entries/icons/original/000/004/982/e-mails.jpg",
    "guy-explaining": "https://i.kym-cdn.com/entries/icons/original/000/032/666/acaster.jpg",
    "types-of-headaches": "https://i.kym-cdn.com/entries/icons/original/000/024/583/tyes.jpg",
    "scared-cat": "https://imgflip.com/s/meme/Scared-Cat.jpg",
    "oh-no-its-retarded": "https://i.kym-cdn.com/entries/icons/original/000/018/824/insidejob.JPG",
    "squidward-window": "https://i.imgflip.com/145qvv.jpg",
    "uno-reverse-card": "https://i.kym-cdn.com/entries/icons/original/000/030/219/reverse_thumb.png",
    "inhaling-seagull": "https://i.kym-cdn.com/entries/icons/original/000/023/897/inhalegull.jpg",
    "american-chopper-argument": "https://i.kym-cdn.com/entries/icons/original/000/025/800/Screen_Shot_2018-03-28_at_3.00.37_PM.png",
    "polish-jerry": "https://i.imgflip.com/1ll661.jpg",
    "lisa-simpson-presentation": "https://i.imgflip.com/2baxar.jpg",
    "sleeping-shaq": "https://imgflip.com/s/meme/Sleeping-Shaq.jpg",
    "thomas-had-never-seen": "https://i.kym-cdn.com/entries/icons/original/000/031/008/thumb.png",
    "sad-cat-thumbs-up": "https://i.imgflip.com/54o27s.png",
    "kombucha-girl": "https://i.kym-cdn.com/entries/icons/original/000/030/781/kombuchaahh.jpg",
    "coffin-dance": "https://i.kym-cdn.com/entries/icons/original/000/033/381/dancing_coffin.jpg",
    "no-no-hes-got-a-point": "https://i.kym-cdn.com/entries/icons/original/000/032/632/No_No_He's_Got_A_Point_Banner.jpg",
    "drake-josh-door": "https://i.kym-cdn.com/entries/icons/original/000/025/820/thumbdrake.jpg",
    "men-will-literally": "https://i.kym-cdn.com/entries/icons/original/000/036/385/depositphotos_42644395-stock-video-young-man-lying-on-sofa.jpg",
    "stonks-not-stonks": "https://i.kym-cdn.com/entries/icons/original/000/029/959/Screen_Shot_2019-06-05_at_1.26.32_PM.jpg",
    "baby-yoda": "https://i.kym-cdn.com/entries/icons/original/000/031/827/bright.jpg",
    "cat-lawyer": "https://i.imgflip.com/4xeam3.png",
    "pet-the-dog": "https://i.imgflip.com/3i9m82.jpg",
    "fernanfloo-laughing": "https://i.kym-cdn.com/entries/icons/original/000/036/168/cover1.jpg",
    "vince-mcmahon": "https://i.kym-cdn.com/entries/icons/original/000/016/911/mcmahongif.PNG",
    "hold-up": "https://i.imgflip.com/40otgs.png",
    "math-lady": "https://i.imgflip.com/1c81c1.jpg",
    "excuse-me-what-the-f": "https://i.kym-cdn.com/entries/icons/original/000/026/913/excuse.jpg",
    "skyrim-skill-tree": "https://i.kym-cdn.com/entries/icons/original/000/023/247/cover12.jpg",
    "distracted-boyfriend-reversed": "https://i.imgflip.com/1yicsm.jpg",
    "the-scroll-of-truth": "https://i.kym-cdn.com/photos/images/original/001/239/994/681.jpg",
    "flex-tape": "https://i.imgflip.com/34w435.jpg",
    "the-office-handshake": "https://i.imgflip.com/3ksxaa.png",
    "sad-affleck": "https://i.kym-cdn.com/entries/icons/original/000/020/104/People_are_being_mean_by_making_mashups_of_sad_Ben_Affleck_s_reaction_to_Batman_v_Superman_reviews.jpg",
    "brain-before-sleep": "https://i.kym-cdn.com/entries/icons/original/000/026/489/crying.jpg",
    "kpop-fans-be-like": "https://i.imgflip.com/2/l2icw.jpg",
    "obama-medal": "https://i.kym-cdn.com/entries/icons/original/000/030/329/cover1.jpg",
    "listen-here-you-little-sht": "https://i.imgflip.com/3dvdso.jpg",
    "finally-inner-peace": "https://i.imgflip.com/3nkh17.png",
    "cat-looking-away": "https://i.kym-cdn.com/entries/icons/original/000/030/729/smudgeyyy.jpg",
    "two-soyjaks-pointing": "https://i.kym-cdn.com/entries/icons/original/000/035/627/cover2.jpg",
    "pedro-raccoon": "https://i.kym-cdn.com/entries/icons/original/000/049/273/cover11.jpg",
    "amogus": "https://i.kym-cdn.com/entries/icons/original/000/036/482/cover5.jpg",
    "chad-yes": "https://i.kym-cdn.com/entries/icons/original/000/031/015/cover5.jpg",
    "angry-birds-pig": "https://imgflip.com/s/meme/Angry-Birds-Pig.jpg",
    "its-free-real-estate": "https://i.kym-cdn.com/entries/icons/original/000/021/311/free.jpg",
    "spiderman-glasses": "https://i.imgflip.com/2jay5q.jpg",
    "well-yes-but-actually-no": "https://i.kym-cdn.com/entries/icons/original/000/028/596/dsmGaKWMeHXe9QuJtq_ys30PNfTGnMsRuHuo_MUzGCg.jpg",
    "megamind-no-bitches": "https://i.imgflip.com/65939r.jpg",
}


def download_image(url: str, output_path: Path, meme_id: str) -> bool:
    """Download an image from a URL and save it locally."""
    try:
        # Try alternative URL first if available
        if meme_id in ALTERNATIVE_URLS:
            url = ALTERNATIVE_URLS[meme_id]
            print(f"  Using alternative URL for {meme_id}")

        response = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        response.raise_for_status()

        # Determine file extension from content type or URL
        content_type = response.headers.get("content-type", "")
        if "png" in content_type or url.endswith(".png"):
            ext = ".png"
        elif "gif" in content_type or url.endswith(".gif"):
            ext = ".gif"
        else:
            ext = ".jpg"

        # Update output path with correct extension
        output_path = output_path.with_suffix(ext)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  Downloaded: {output_path.name}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  Failed to download {meme_id}: {e}")
        return False


def main():
    print("Meme Image Downloader")
    print("=" * 50)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    # Load memes.json
    with open(MEMES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    memes = data["memes"]
    print(f"Found {len(memes)} memes to download\n")

    successful = 0
    failed = []

    for i, meme in enumerate(memes, 1):
        meme_id = meme["id"]
        url = meme["imageUrl"]
        output_path = OUTPUT_DIR / f"{meme_id}.jpg"

        print(f"[{i}/{len(memes)}] {meme['name']}")

        if download_image(url, output_path, meme_id):
            successful += 1
        else:
            failed.append(meme_id)

        # Be nice to servers
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print(f"Download complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(failed)}")

    if failed:
        print(f"\nFailed memes: {', '.join(failed)}")
        print("You may need to manually download these images.")

    print(f"\nImages saved to: {OUTPUT_DIR}")
    print("\nNext step: Update memes.json to use local paths")
    print('  Change imageUrl from "https://..." to "/images/memes/{id}.jpg"')


if __name__ == "__main__":
    main()
