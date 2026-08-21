#!/usr/bin/env python3
import subprocess, time, json
def run_cycle():
    print("🧠 Running investment cycle...")
    subprocess.run(["python3", "generate_strategy.py"], check=True)
    subprocess.run(["python3", "money_market.py"], check=True)
    subprocess.run(["python3", "trade_executor.py"], check=True)
    print("✅ Cycle complete.")
if __name__ == "__main__":
    while True:
        run_cycle()
        time.sleep(60)
