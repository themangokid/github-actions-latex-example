#!/bin/bash

folder="$1"

if [ -z "$folder" ]; then
  echo "Usage: $0 /path/to/folder"
  exit 1
fi

for file in "$folder"/*.txt; do
  [ -f "$file" ] || continue
  perl -pi -e 's/\d+\s|\*//g' "$file"
done
