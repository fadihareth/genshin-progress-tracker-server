#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="${1:-.}"

find "$ROOT_DIR" -type f -iname "*.png" -print0 | while IFS= read -r -d '' img; do
    dir="$(dirname "$img")"
    filename="$(basename "$img")"
    base="${filename%.*}"
    output="$dir/$base.webp"

    echo "Converting: $img → $output"

    if magick "$img" \
        -strip \
        -define webp:method=6 \
        -define webp:image-hint=photo \
        "$output"; then

        rm "$img"
        echo "Deleted: $img"
    else
        echo "❌ Failed: $img (original kept)"
    fi
done

