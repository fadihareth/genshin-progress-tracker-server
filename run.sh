#!/bin/bash
set -e

cd scripts

source venv/bin/activate

# Make sure genshindb is up to date
cd genshindb
npm update
cd ..

# Start server in background
node genshindb/server.js &
SERVER_PID=$!

# Cleanup on exit
trap "kill $SERVER_PID" EXIT

# Wait for server to become ready
echo "Waiting for server to start..."

until curl -s http://localhost:3000/health > /dev/null; do
    sleep 1
done

echo "Server is ready."

# Run scripts
python3 fetch_artifacts.py
python3 fetch_characters.py
python3 fetch_weapons.py
python3 fetch_talents.py

python3 img_fetch.py

cd ..

./process_images.sh
