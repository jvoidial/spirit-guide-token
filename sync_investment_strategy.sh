#!/bin/bash
SRC_FILE="investment_strategy.json"
DEST="/sdcard/backup/voxel_resonance/"
IMPORT_SCRIPT="process_strategy.py"
mkdir -p "$DEST"
rsync -avz "$SRC_FILE" "$DEST" 2>/dev/null
echo "✅ Initial sync done."
inotifywait -m -e modify -e create -e move "$SRC_FILE" --format '%w%f' 2>/dev/null | while read FILE; do
    rsync -avz "$FILE" "$DEST" 2>/dev/null
    if [ -f "$IMPORT_SCRIPT" ]; then
        python3 "$IMPORT_SCRIPT"
    fi
done
