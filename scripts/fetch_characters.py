import requests
import json
import os

CHARACTERS_JSON_PATH = "../characters/characters.json"
DATABASE_URL = 'http://localhost:3000/character/list'


def get_character_list():
    return requests.get(DATABASE_URL)


def load_existing_characters():
    if not os.path.exists(CHARACTERS_JSON_PATH):
        return []

    with open(CHARACTERS_JSON_PATH, "r", encoding="utf-8") as fin:
        try:
            return json.load(fin)
        except json.JSONDecodeError:
            return []


def get_character_data(name, character_id):
    url = 'https://genshin-db-api.vercel.app/api/v5/characters?query=' + name.lower().strip()

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            character = {
                "id": character_id,
                "name": data["name"],
                "title": data["title"],
                "description": data["description"],
                "weapon": data["weaponText"],
                "gender": data["gender"],
                "rarity": data["rarity"],
                "birthday": data["birthdaymmdd"],
                "element": data["elementText"],
                "region": data["region"] if "region" in data else None,
                "substat": data["substatText"],
                "localSpecialtyMaterial": data["costs"]["ascend1"][2]["name"],
            }

            # World boss material
            if len(data["costs"]["ascend2"]) > 4:
                character["worldBossMaterial"] = data["costs"]["ascend2"][2]["name"]
            else:
                character["worldBossMaterial"] = None

            # World drop materials
            character["worldDropMaterial"] = {
                1: data["costs"]["ascend1"][-1]["name"],
                2: data["costs"]["ascend3"][-1]["name"],
                3: data["costs"]["ascend6"][-1]["name"]
            }

            return character

        else:
            print(f'Error fetching character "{name}": {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Error fetching character "{name}": {e}')

    return None


def main():
    print("Starting Character Fetch")

    # Load existing JSON
    existing_characters = load_existing_characters()

    # Existing character names
    existing_names = {
        character["name"].strip().lower()
        for character in existing_characters
    }

    # Determine next ID
    if existing_characters:
        next_id = max(character["id"] for character in existing_characters) + 1
    else:
        next_id = 0

    characters = get_character_list()

    if not characters:
        print("No characters fetched")
        return

    print(f"Checking {len(characters)} characters")

    added_count = 0

    for i, character_name in enumerate(characters):

        # Skip travelers
        if character_name in ["Lumine", "Aether"]:
            continue

        # Skip existing characters
        if character_name.strip().lower() in existing_names:
            continue

        new_character = get_character_data(character_name, next_id)

        if new_character is not None:
            existing_characters.append(new_character)
            existing_names.add(new_character["name"].strip().lower())

            print(f'Added: {new_character["name"]} (ID: {next_id})')

            next_id += 1
            added_count += 1

    # Save updated JSON
    with open(CHARACTERS_JSON_PATH, "w", encoding="utf-8") as fout:
        json.dump(existing_characters, fout, indent=4, ensure_ascii=False)

    print(f"Done! Added {added_count} new characters.")


if __name__ == '__main__':
    main()