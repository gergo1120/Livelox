import os
import re
import requests
from PIL import Image
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

SAVE_DIR = "tiles"
OUTPUT_IMAGE = "egyesitett_terkep.png"
URL_FILE = "URL.txt"

def read_url_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.readline().strip()

def download_tiles(tiles_urls, prefix):
    os.makedirs(SAVE_DIR, exist_ok=True)
    for url in tiles_urls:
        filename = url.split("/")[-1]
        if not filename.endswith(".png"):
            filename += ".png"
        filepath = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Letöltés: {filename}")
            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
            else:
                print(f"Hiba a letöltéskor: {url}")

def stitch_tiles():
    pattern = re.compile(r"([a-f0-9]{32})-(\d+)-(\d+)-(\d+)-(\d+)\.png")
    tiles = []

    for fname in os.listdir(SAVE_DIR):
        m = pattern.match(fname)
        if m:
            _, x, y, w, h = m.groups()
            tiles.append({
                "filename": fname,
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            })

    if not tiles:
        print("❌ Nem találtam tile képeket.")
        return

    max_x = max(tile["x"] + tile["w"] for tile in tiles)
    max_y = max(tile["y"] + tile["h"] for tile in tiles)
    print(f"🖼️ Összesített kép mérete: {max_x}x{max_y}")

    canvas = Image.new("RGB", (max_x, max_y))
    for tile in tiles:
        img_path = os.path.join(SAVE_DIR, tile["filename"])
        img = Image.open(img_path)
        canvas.paste(img, (tile["x"], tile["y"]))

    canvas.save(OUTPUT_IMAGE)
    print(f"✅ Kép elmentve: {OUTPUT_IMAGE}")

def main():
    url = read_url_from_file(URL_FILE)
    print(f"🔗 Beolvasott URL: {url}")

    tile_urls = []
    prefix = None

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            nonlocal prefix
            u = response.url
            if "/tiles/" in u and re.search(r"/[a-f0-9]{32}-\d+-\d+-\d+-\d+$", u):
                tile_urls.append(u)
                if not prefix:
                    m = re.search(r"/([a-f0-9]{32})-", u)
                    if m:
                        prefix = m.group(1)

        page.on("response", handle_response)

        print("🌍 Oldal betöltése...")
        page.goto(url)
        page.wait_for_timeout(15000)  # várunk 15 másodpercet
        browser.close()

    if not prefix or not tile_urls:
        print("❌ Nem találtam prefixet vagy tile URL-eket.")
        input("Nyomj Enter-t a kilépéshez...")
        return

    print(f"✅ Prefix: {prefix}")
    print(f"✅ Tile URL-ek száma: {len(tile_urls)}")

    download_tiles(tile_urls, prefix)
    stitch_tiles()

    input("Press enter to proceed...")

if __name__ == "__main__":
    main()
