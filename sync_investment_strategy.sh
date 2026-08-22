#!/bin/bash
SRC_FILE="investment_strategy.json"
DEST="/sdcard/backup/voxel_resonance/"
mkdir -p "$DEST"
rsync -avz "$SRC_FILE" "$DEST" 2>/dev/null || true
inotifywait -m -e modify -e create -e move "$SRC_FILE" --format '%w%f' 2>/dev/null | while read FILE; do
    rsync -avz "$FILE" "$DEST" 2>/dev/null || true
    if [ -f "process_strategy.py" ]; then
        python3 process_strategy.py
    fi
done
