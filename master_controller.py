#!/usr/bin/env python3
import subprocess, time, sys, os
INTERVAL = 60
def run_cycle():
    print("🧠 Running cycle...")
    try:
        subprocess.run(["python3", "macro_scanner.py"], check=False)
        subprocess.run(["python3", "generate_strategy.py"], check=True)
        subprocess.run(["python3", "universal_trader.py"], check=True)
        subprocess.run(["git", "add", "*.json"], check=False)
        subprocess.run(["git", "commit", "-m", f"Auto-update {time.strftime('%Y-%m-%d %H:%M:%S')}"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print("✅ Cycle complete.")
    except Exception as e:
        print(f"❌ Cycle error: {e}")
if __name__ == "__main__":
    while True:
        run_cycle()
        time.sleep(INTERVAL)
