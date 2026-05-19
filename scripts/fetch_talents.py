import requests
import json
import os

TALENTS_JSON_PATH = "../characters/talents.json"
CHARACTER_DB_URL = 'http://localhost:3000/character/list'
DATABASE_URL = 'http://localhost:3000/talents'


def get_character_list():
    return requests.get(CHARACTER_DB_URL).json()


def load_existing_talents():
    if not os.path.exists(TALENTS_JSON_PATH):
        return {}

    with open(TALENTS_JSON_PATH, "r", encoding="utf-8") as fin:
        try:
            data = json.load(fin)

            # Ensure it's a dictionary
            if isinstance(data, dict):
                return data

            return {}

        except json.JSONDecodeError:
            return {}


def get_character_talents(name):
    try:
        response = requests.get(DATABASE_URL, params={ "name": name.lower().strip() })

        if response.status_code == 200:
            data = response.json()

            talents = {
                "attack": data["combat1"]["name"],
                "skill": data["combat2"]["name"],
                "burst": data["combat3"]["name"]
            }

            talents["talentMaterial"] = {
                1: data["costs"]["lvl2"][1]["name"],
                2: data["costs"]["lvl5"][1]["name"],
                3: data["costs"]["lvl8"][1]["name"]
            }

            talents["weeklyBossMaterial"] = data["costs"]["lvl8"][-1]["name"]

            return talents

        else:
            print(f'Error fetching talents for "{name}": {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Error fetching talents for "{name}": {e}')

    return None


def main():
    print("Starting Talent Fetch")

    # Load existing JSON
    existing_talents = load_existing_talents()

    # Existing character names
    existing_names = {
        name.strip().lower()
        for name in existing_talents.keys()
    }

    characters = get_character_list()

    if not characters:
        print("No characters fetched")
        return

    print(f"Checking {len(characters)} characters")

    added_count = 0

    for i, character_name in enumerate(characters):
        # Skip travelers
        if character_name in ["Lumine", "Aether", "Manekin", "Manekina"]:
            continue

        # Skip existing talents
        if character_name.strip().lower() in existing_names:
            continue

        talents = get_character_talents(character_name)

        if talents is not None:
            existing_talents[character_name] = talents

            print(f'Added talents for: {character_name}')

            added_count += 1

    # Save updated JSON
    with open(TALENTS_JSON_PATH, "w", encoding="utf-8") as fout:
        json.dump(existing_talents, fout, indent=4, ensure_ascii=False)

    print(f"Done! Added talents for {added_count} characters.")


if __name__ == '__main__':
    main()