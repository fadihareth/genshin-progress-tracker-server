import requests
import json
import os

API_URL = "https://genshin-impact.fandom.com/api.php"

CATEGORIES = [
    {
        "wiki_category": "Character_Profiles",
        "json_path": "../characters/characters.json",
        "image_folder": "../characters/profiles",
        "type": "character_profiles"
    },
    {
        "wiki_category": "Character_Icons",
        "json_path": "../characters/characters.json",
        "image_folder": "../characters/icons",
        "type": "character_icons"
    },
    {
        "wiki_category": "Weapons",
        "json_path": "../weapons/weapons.json",
        "image_folder": "../weapons/images",
        "type": "weapons"
    },
    {
        "wiki_category": "Artifacts",
        "json_path": "../artifacts/artifacts.json",
        "image_folder": "../artifacts/images",
        "type": "artifacts"
    },
    {
        "wiki_category": "Talent",
        "json_path": "../characters/talents.json",
        "image_folder": "../characters/talents",
        "type": "talents"
    }
]

missing_items = set()

session = requests.Session()


def sanitize_filename(name):
    return (
        name.replace("/", "")
            .replace(":", "")
            .replace("  ", " ")
            .replace(" ", "_")
    )

## Used only for building missing_items array
def verify_missing_material(name):
    if not item_exists("../items", name):
        missing_items.add(name)

def item_exists(image_folder, name):
    webp_filepath = os.path.join(
        image_folder,
        sanitize_filename(name) + ".webp"
    )

    png_filepath = os.path.join(
        image_folder,
        sanitize_filename(name) + ".png"
    )

    return os.path.exists(webp_filepath) or os.path.exists(png_filepath)

def get_missing_names(category_config):
    json_path = category_config["json_path"]
    image_folder = category_config["image_folder"]
    category_type = category_config["type"]

    os.makedirs(image_folder, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as fin:
        data = json.load(fin)

    missing = []

    # Standard array format (characters, weapons)
    if category_type == "character_profiles":
        for item in data:

            name = item["name"] + " Profile"
            if item_exists(image_folder, name):
                continue

            verify_missing_material(item["localSpecialtyMaterial"])
            verify_missing_material(item["worldBossMaterial"])
            for i in range(1, 4):
                verify_missing_material(item["worldDropMaterial"][str(i)])
            missing.append("File:" + name + ".png")
    
    elif category_type == "character_icons":
        for item in data:

            name = item["name"] + " Icon"
            if item_exists(image_folder, name):
                continue

            missing.append("File:" + name + ".png")

    elif category_type == "weapons":

        for item in data:
            name = item["name"]
            if item_exists(image_folder, name):
                continue

            for i in range(1, 4):
                verify_missing_material(item["worldDropMaterial1"][str(i)])
                verify_missing_material(item["worldDropMaterial2"][str(i)])
            verify_missing_material(item["weaponMaterial"]["4"])
            missing.append(name)
    
    elif category_type == "artifacts":

        for item in data:
            name = item["flower"]
            if item_exists(image_folder, name):
                continue

            missing.append(name)

    # Talents dictionary format
    elif category_type == "talents":

        for _, talent_data in data.items():

            for talent_name in [
                talent_data["skill"],
                talent_data["burst"]
            ]:

                webp_filepath = os.path.join(
                    image_folder,
                    sanitize_filename(talent_name) + ".webp"
                )

                png_filepath = os.path.join(
                    image_folder,
                    sanitize_filename(talent_name) + ".png"
                )

                if os.path.exists(webp_filepath) or os.path.exists(png_filepath):
                    continue

                for i in range(1, 4):
                    verify_missing_material(talent_data["talentMaterial"][str(i)])
                verify_missing_material(talent_data["weeklyBossMaterial"])
                missing.append(talent_name)

    return missing


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


def download_images(category_config, missing_names):
    wiki_category = category_config["wiki_category"]
    image_folder = category_config["image_folder"]

    print(f"\n========== {wiki_category} ==========")

    if not missing_names:
        print("No missing images!")
        return

    print(f"Missing images: {len(missing_names)}")

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

        if name not in missing_names:
            continue

        try:
            print(f"Downloading {name}...")

            img_data = session.get(url).content

            fixed_name = name
            if category_config["type"] == "character_profiles":
                fixed_name = name.replace('File:', '').replace('.png', '')
            elif category_config["type"] == "character_icons":
                fixed_name = name.replace('File:', '').replace('.png', '')
            
            filename = sanitize_filename(fixed_name)

            filename += ".png"
            filepath = os.path.join(image_folder, filename)

            with open(filepath, "wb") as fout:
                fout.write(img_data)

            downloaded.append(name)

            print(f"Downloaded {name}")

        except Exception as e:
            print(f"Failed to download {name}: {e}")

    print(f"\nFinished {len(downloaded)}/{len(missing_names)} downloads")

    # Print missed items
    missed = [
        item for item in missing_names
        if item not in downloaded
    ]

    if missed:
        print("\n----------------")
        print("Missed items:")

        for item in missed:
            print(item)


def main():
    print("Starting image downloader...")

    for category in CATEGORIES:
        missing_names = get_missing_names(category)
        download_images(category, missing_names)
    
    download_images(
        {
            "wiki_category": "Item",
            "json_path": "",
            "image_folder": "../items",
            "type": "items"
        },
        missing_items
    )

    print("\nDone!")


if __name__ == "__main__":
    main()