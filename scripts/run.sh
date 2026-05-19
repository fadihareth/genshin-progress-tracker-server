#!/bin/bash

source venv/bin/activate
node genshindb/server.js &
SERVER_PID=$!

python fetch_artifacts.py
python fetch_characters.py
python fetch_weapons.py
python fetch_talents.py

kill $SERVER_PID