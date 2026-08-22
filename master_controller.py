#!/usr/bin/env python3
import subprocess, time, sys

INTERVAL = 300  # seconds
def run_cycle():
    print("🧠 Running investment cycle...")
    try:
        subprocess.run(["python3", "macro_scanner.py"], check=True)
        subprocess.run(["python3", "generate_strategy.py"], check=True)
        subprocess.run(["python3", "money_market.py"], check=True)
        subprocess.run(["python3", "universal_trader.py"], check=True)
        subprocess.run(["python3", "yield_optimizer.py"], check=True)
        subprocess.run(["python3", "update_state_logger.py"], check=True)
        print("✅ Cycle complete.")
    except Exception as e:
        print(f"❌ Cycle error: {e}")

if __name__ == "__main__":
    while True:
        run_cycle()
        time.sleep(INTERVAL)
