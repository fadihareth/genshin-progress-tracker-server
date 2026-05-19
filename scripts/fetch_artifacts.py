import requests
import json
import os

ARTIFACTS_JSON_PATH = "../artifacts/artifacts.json"
DATABASE_URL = 'http://localhost:3000/artifact'


def get_artifact_list():
    return requests.get(DATABASE_URL + "/list").json()


def load_existing_artifacts():
    if not os.path.exists(ARTIFACTS_JSON_PATH):
        return []

    with open(ARTIFACTS_JSON_PATH, "r", encoding="utf-8") as fin:
        try:
            return json.load(fin)
        except json.JSONDecodeError:
            return []


def get_artifact_data(name, artifact_id):
    try:
        response = requests.get(DATABASE_URL, params={ "name": name.lower().strip() })

        if response.status_code == 200:
            data = response.json()

            # Skip 1pc artifacts
            if "effect1Pc" in data:
                return None

            artifact = {
                "id": artifact_id,
                "name": data["name"],
                "rarity": data["rarityList"],
                "2pc": data["effect2Pc"],
                "4pc": data["effect4Pc"],
                "flower": data["flower"]["name"],
                "plume": data["plume"]["name"],
                "sands": data["sands"]["name"],
                "goblet": data["goblet"]["name"],
                "circlet": data["circlet"]["name"]
            }

            return artifact

        else:
            print(f'Error fetching artifact "{name}": {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Error fetching artifact "{name}": {e}')

    return None


def main():
    print("Starting Artifact Fetch")

    # Load existing JSON
    existing_artifacts = load_existing_artifacts()

    # Create lookup set of existing names
    existing_names = {
        artifact["name"].strip().lower()
        for artifact in existing_artifacts
    }

    # Determine next ID
    if existing_artifacts:
        next_id = max(artifact["id"] for artifact in existing_artifacts) + 1
    else:
        next_id = 0

    artifacts = get_artifact_list()

    if not artifacts:
        print("No artifacts fetched")
        return

    print(f"Checking {len(artifacts)} artifacts")

    added_count = 0

    for i, artifact_name in enumerate(artifacts):
        # Skip if already exists in JSON
        if artifact_name.strip().lower() in existing_names:
            continue

        new_artifact = get_artifact_data(artifact_name, next_id)

        if new_artifact is not None:
            existing_artifacts.append(new_artifact)
            existing_names.add(new_artifact["name"].strip().lower())

            print(f'Added: {new_artifact["name"]} (ID: {next_id})')

            next_id += 1
            added_count += 1

    # Save updated JSON
    with open(ARTIFACTS_JSON_PATH, "w", encoding="utf-8") as fout:
        json.dump(existing_artifacts, fout, indent=4, ensure_ascii=False)

    print(f"Done! Added {added_count} new artifacts.")


if __name__ == '__main__':
    main()