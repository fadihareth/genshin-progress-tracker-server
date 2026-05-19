import requests
import json
import os

WEAPONS_JSON_PATH = "../weapons/weapons.json"
DATABASE_URL = 'http://localhost:3000/weapon'


def get_weapon_list():
    return requests.get(DATABASE_URL + "/list").json()


def load_existing_weapons():
    if not os.path.exists(WEAPONS_JSON_PATH):
        return []

    with open(WEAPONS_JSON_PATH, "r", encoding="utf-8") as fin:
        try:
            return json.load(fin)
        except json.JSONDecodeError:
            return []


def is_valid_weapon(name):
    try:
        response = requests.get(DATABASE_URL, params={ "name": name.lower().strip() })
        return response.json()["rarity"] > 2

    except requests.exceptions.RequestException:
        return False


def get_weapon_data(name, weapon_id):
    paramsdb = {
        "name": name.lower().strip(),
        "level": 90
    }

    try:
        response = requests.get(DATABASE_URL, params={ "name": name.lower().strip() })
        responseStats = requests.get(DATABASE_URL + "/stats", params=paramsdb)

        if response.status_code == 200 and responseStats.status_code == 200:
            data = response.json()
            dataStats = responseStats.json()

            weapon = {
                "id": weapon_id,
                "name": data["name"],
                "description": data["description"],
                "type": data["weaponText"],
                "rarity": data["rarity"],
                "baseAtk": int(round(data["baseAtkValue"], 0)),
                "baseAtkMax": int(round(dataStats["attack"], 0)),
                "mainStat": data["mainStatText"],
                "mainStatValue": data["baseStatText"],
                "effectname": data["effectName"]
            }

            # Main stat max formatting
            if weapon["mainStat"] == "Elemental Mastery":
                weapon["mainStatValueMax"] = str(int(round(dataStats["specialized"], 0)))
            else:
                weapon["mainStatValueMax"] = str(round(dataStats["specialized"] * 100, 1))

            # Effect formatting
            r1 = data["r1"]["values"]
            effect = data["r1"]["description"]

            for i in range(len(r1)):
                effect = effect.replace(r1[i], "{" + f"{i}" + "}", 1)

                if effect.count("{" + f"{i}" + "}") != 1:
                    print(f'Might want to double check "{name}" effect formatting!')

            weapon["effect"] = effect
            weapon["r1"] = data["r1"]["values"]

            # Refinements
            if "r2" in data:
                weapon["r2"] = data["r2"]["values"]
                weapon["r3"] = data["r3"]["values"]
                weapon["r4"] = data["r4"]["values"]
                weapon["r5"] = data["r5"]["values"]

            # Materials
            weapon["weaponMaterial"] = {
                1: data["costs"]["ascend1"][1]["name"],
                2: data["costs"]["ascend2"][1]["name"],
                3: data["costs"]["ascend4"][1]["name"],
                4: data["costs"]["ascend6"][1]["name"]
            }

            weapon["worldDropMaterial1"] = {
                1: data["costs"]["ascend1"][2]["name"],
                2: data["costs"]["ascend3"][2]["name"],
                3: data["costs"]["ascend5"][2]["name"]
            }

            weapon["worldDropMaterial2"] = {
                1: data["costs"]["ascend1"][3]["name"],
                2: data["costs"]["ascend3"][3]["name"],
                3: data["costs"]["ascend5"][3]["name"]
            }

            return weapon

        else:
            print(f'Error fetching weapon "{name}": API={response.status_code}, DB={responsedb.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Error fetching weapon "{name}": {e}')

    return None


def main():
    print("Starting Weapon Fetch")

    # Load existing JSON
    existing_weapons = load_existing_weapons()

    # Existing weapon names
    existing_names = {
        weapon["name"].strip().lower()
        for weapon in existing_weapons
    }

    # Determine next ID
    if existing_weapons:
        next_id = max(weapon["id"] for weapon in existing_weapons) + 1
    else:
        next_id = 0

    weapons = get_weapon_list()

    if not weapons:
        print("No weapons fetched")
        return

    print(f"Checking {len(weapons)} weapons")

    added_count = 0

    for i, weapon_name in enumerate(weapons):
        # Skip invalid/special weapons
        if weapon_name == "Prized Isshin Blade":
            continue

        if not is_valid_weapon(weapon_name):
            continue

        # Skip existing weapons
        if weapon_name.strip().lower() in existing_names:
            continue

        new_weapon = get_weapon_data(weapon_name, next_id)

        if new_weapon is not None:
            existing_weapons.append(new_weapon)
            existing_names.add(new_weapon["name"].strip().lower())

            print(f'Added: {new_weapon["name"]} (ID: {next_id})')

            next_id += 1
            added_count += 1

    # Save updated JSON
    with open(WEAPONS_JSON_PATH, "w", encoding="utf-8") as fout:
        json.dump(existing_weapons, fout, indent=4, ensure_ascii=False)

    print(f"Done! Added {added_count} new weapons.")


if __name__ == '__main__':
    main()