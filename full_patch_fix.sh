#!/bin/bash

echo "🔥 FULL PATCH FIX – INSTANT JSON SYNC"
echo "========================================"

# 1. Kill any existing processes
echo "📡 Stopping old processes..."
pkill -f master_controller.py 2>/dev/null
pkill -f sync_investment_strategy.sh 2>/dev/null
sleep 1

# 2. Generate fresh investment_strategy.json
echo "📊 Generating fresh strategy..."
python3 generate_strategy.py

# 3. Commit and push the updated JSON to GitHub (instantly syncs)
echo "📤 Committing and pushing to GitHub..."
git add investment_strategy.json
git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "No changes to commit"
git push origin main

# 4. Restart master controller with wake lock (keeps it alive)
echo "🧠 Restarting master controller..."
termux-wake-lock 2>/dev/null || echo "⚠️ wake-lock not available, process may stop when screen off"
nohup python3 master_controller.py > controller.log 2>&1 &

# 5. Restart sync watcher
echo "🔄 Restarting sync watcher..."
nohup ./sync_investment_strategy.sh > sync.log 2>&1 &

# 6. Verify processes are running
echo ""
echo "🔍 VERIFICATION:"
ps aux | grep -E "master_controller|sync_investment" | grep -v grep || echo "⚠️ Processes not running!"

# 7. Show latest JSON timestamp
echo ""
echo "📄 Latest JSON (should be fresh):"
curl -s https://jvoidial.github.io/spirit-guide-token/investment_strategy.json | grep timestamp | head -1

echo ""
echo "✅ Patch complete! JSON synced instantly."
echo "   If JSON shows old timestamp, wait 1-2 min for GitHub Pages to deploy."
