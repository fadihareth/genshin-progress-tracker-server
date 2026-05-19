import requests
from pathlib import Path
import os

API_URL = "https://genshin-impact.fandom.com/api.php"

session = requests.Session()


def sanitize_filename(name):
    return (
        name.replace("/", "")
            .replace(":", "")
            .replace("  ", " ")
            .replace(" ", "_")
    )


def get_existing_items():
    path = Path("../items")

    return [
        file.stem
        for file in path.iterdir()
        if file.is_file()
    ]
    


def get_all_category_pages(category):
    pages = []

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "500",
        "format": "json"
    }

    while True:
        response = session.get(API_URL, params=params)
        data = response.json()

        pages.extend(data["query"]["categorymembers"])

        if "continue" not in data:
            break

        params["cmcontinue"] = data["continue"]["cmcontinue"]

    return pages


def get_page_images(titles):
    images = {}

    params = {
        "action": "query",
        "prop": "pageimages",
        "piprop": "original",
        "format": "json",
        "titles": "|".join(titles)
    }

    response = session.get(API_URL, params=params)
    data = response.json()

    for page in data["query"]["pages"].values():
        if "original" in page:
            images[page["title"]] = page["original"]["source"]

    return images


def download_images():
    wiki_category = "Character_Development_Items"
    image_folder = "../items"

    print(f"\n========== {wiki_category} ==========")

    # Determine missing images
    existing_items = get_existing_items()

    print(f"Currently have: {len(existing_items)} images")

    # Fetch all category pages
    print("Fetching wiki pages...")
    pages = get_all_category_pages(wiki_category)

    titles = [page["title"] for page in pages]

    # Fetch image URLs
    print("Fetching image URLs...")
    urls = {}

    CHUNK_SIZE = 50

    for i in range(0, len(titles), CHUNK_SIZE):
        chunk = titles[i:i + CHUNK_SIZE]
        urls.update(get_page_images(chunk))

    print(f"Found {len(urls)} total wiki images")

    # Download only missing images
    downloaded = []

    for name, url in urls.items():

        filename = sanitize_filename(name)

        if filename in existing_items:
            continue

        try:
            print(f"Downloading {name}...")

            img_data = session.get(url).content

            filename += ".png"
            filepath = os.path.join(image_folder, filename)

            with open(filepath, "wb") as fout:
                fout.write(img_data)

            downloaded.append(name)

            print(f"Downloaded {name}")

        except Exception as e:
            print(f"Failed to download {name}: {e}")

    print(f"\nFinished {len(downloaded)} downloads")


def main():
    print("Starting items downloader...")

    download_images()

    print("\nDone!")


if __name__ == "__main__":
    main()