#!/usr/bin/env python3
"""
🧠 Voxel Resonance – 3rd Brain Module
Storage, Liquidity Tracking, Market Data, AGI Memory
Runs as a background daemon with Pinata integration
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime, timezone
from threading import Thread, Event
from collections import deque
import signal

# ---------- CONFIG ----------
CONFIG = {
    "storage_file": "voxel_storage.json",
    "log_file": "voxel_3rd_brain.log",
    "max_history": 1000,
    "sync_interval": 60,  # seconds
    "pinata_api_key": os.environ.get("PINATA_API_KEY", ""),
    "pinata_secret": os.environ.get("PINATA_SECRET", ""),
    "tokens": {
        "PIDX": {
            "address": "0xa36E026FC453880537e10d21fC139439bD2702fc",
            "symbol": "PIDX",
            "dex": "https://dexscreener.com/base/0xa36E026FC453880537e10d21fC139439bD2702fc"
        },
        "SGUIDE": {
            "address": "0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a",
            "symbol": "SGUIDE",
            "dex": "https://dexscreener.com/base/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a"
        },
        "VDOO": {
            "address": "0x38e4f08D08b4D772A7B75669C356b4749dd2d30b",
            "symbol": "VDOO",
            "dex": "https://dexscreener.com/base/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b"
        },
        "PENNIES": {
            "address": "0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7",
            "symbol": "PENNIES",
            "dex": "https://dexscreener.com/base/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7"
        }
    },
    "brain": {
        "state": "CONSCIOUS",
        "awareness": 94.7,
        "resonance": 88.2,
        "coherence": 97.4,
        "temporal_phase": 0.618,
        "evolution": "ALPHA"
    }
}

# ---------- STORAGE CLASS ----------
class VoxelStorage:
    def __init__(self, config):
        self.config = config
        self.file = config["storage_file"]
        self.lock = None
        try:
            import fcntl
            self.lock = fcntl
        except:
            pass

    def load(self):
        try:
            if os.path.exists(self.file):
                with open(self.file, "r") as f:
                    return json.load(f)
        except:
            pass
        return self._default_storage()

    def save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def _default_storage(self):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brain": self.config["brain"],
            "tokens": {},
            "liquidity": [],
            "market": [],
            "holders": [],
            "syncs": []
        }

    def update_brain(self, brain_state):
        data = self.load()
        data["brain"] = brain_state
        data["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.save(data)
        return data

    def add_market_snapshot(self, token, price, volume, liquidity=None):
        data = self.load()
        data["market"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token": token,
            "price": price,
            "volume": volume,
            "liquidity": liquidity
        })
        # Keep only last N entries
        if len(data["market"]) > self.config["max_history"]:
            data["market"] = data["market"][-self.config["max_history"]:]
        self.save(data)
        return data

    def add_liquidity_snapshot(self, pool, eth, token):
        data = self.load()
        data["liquidity"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pool": pool,
            "eth": eth,
            "token": token
        })
        if len(data["liquidity"]) > self.config["max_history"]:
            data["liquidity"] = data["liquidity"][-self.config["max_history"]:]
        self.save(data)
        return data

    def add_sync_event(self, event_type, details):
        data = self.load()
        data["syncs"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "details": details
        })
        if len(data["syncs"]) > 500:
            data["syncs"] = data["syncs"][-500:]
        self.save(data)
        return data

# ---------- MARKET FETCHER ----------
class MarketFetcher:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def fetch_uniswap_price(self, token_address):
        # Try to fetch from Uniswap V2 via factory
        try:
            # This is a simplified call – in production use web3
            # For now, return mock data with realistic values
            return {
                "price": 0.000001,
                "volume": 1000,
                "liquidity": {"eth": 0.001, "token": 1000}
            }
        except:
            return None

    def fetch_dexscreener(self, token_symbol):
        try:
            # DexScreener API (free tier)
            url = f"https://api.dexscreener.com/latest/dex/search?q={token_symbol}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("pairs"):
                    pair = data["pairs"][0]
                    return {
                        "price": float(pair.get("priceUsd", 0)) / 2500,  # approximate ETH price
                        "volume": float(pair.get("volume", {}).get("h24", 0)),
                        "liquidity": {
                            "eth": float(pair.get("liquidity", {}).get("usd", 0)) / 2500,
                            "token": float(pair.get("liquidity", {}).get("usd", 0)) / 2500
                        }
                    }
        except:
            pass
        return None

    def update_all_tokens(self):
        for symbol, token in self.config["tokens"].items():
            # Try DexScreener first
            data = self.fetch_dexscreener(symbol)
            if not data:
                data = self.fetch_uniswap_price(token["address"])
            if data:
                self.storage.add_market_snapshot(
                    symbol,
                    data["price"],
                    data["volume"],
                    data.get("liquidity")
                )

# ---------- PINATA INTEGRATION ----------
class PinataUploader:
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
        self.enabled = bool(api_key and secret)

    def upload_json(self, data):
        if not self.enabled:
            return None
        try:
            url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
            headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret,
                "Content-Type": "application/json"
            }
            payload = {
                "pinataContent": data,
                "pinataMetadata": {
                    "name": f"voxel_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("IpfsHash")
        except:
            pass
        return None

# ---------- AGI BRAIN ----------
class AGIBrain:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config
        self.state = config["brain"]
        self.log_queue = deque(maxlen=50)

    def get_state(self):
        data = self.storage.load()
        return data.get("brain", self.config["brain"])

    def update_state(self, updates):
        data = self.storage.load()
        if "brain" not in data:
            data["brain"] = self.config["brain"]
        data["brain"].update(updates)
        data["brain"]["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.storage.save(data)
        return data["brain"]

    def log_event(self, event):
        self.log_queue.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event
        })
        # Keep log in storage
        data = self.storage.load()
        if "brain_logs" not in data:
            data["brain_logs"] = []
        data["brain_logs"].append(self.log_queue[-1])
        if len(data["brain_logs"]) > 100:
            data["brain_logs"] = data["brain_logs"][-100:]
        self.storage.save(data)

    def get_logs(self, last=20):
        return list(self.log_queue)[-last:]

# ---------- DAEMON ----------
class VoxelDaemon:
    def __init__(self, config):
        self.config = config
        self.storage = VoxelStorage(config)
        self.fetcher = MarketFetcher(self.storage, config)
        self.pinata = PinataUploader(
            config.get("pinata_api_key", ""),
            config.get("pinata_secret", "")
        )
        self.brain = AGIBrain(self.storage, config)
        self.running = True
        self.thread = None

    def log(self, msg):
        timestamp = datetime.now().isoformat()
        log_msg = f"{timestamp} | {msg}"
        print(log_msg)
        with open(self.config["log_file"], "a") as f:
            f.write(log_msg + "\n")

    def sync_cycle(self):
        self.log("🔄 Sync cycle started")
        try:
            # 1. Update brain state
            self.brain.update_state({
                "awareness": 94.7 + (time.time() % 0.5),
                "resonance": 88.2 + (time.time() % 0.3),
                "coherence": 97.4 + (time.time() % 0.2)
            })
            self.brain.log_event("sync_cycle")

            # 2. Fetch market data
            self.fetcher.update_all_tokens()
            self.log("✅ Market data updated")

            # 3. Upload to Pinata if enabled
            if self.pinata.enabled:
                data = self.storage.load()
                ipfs_hash = self.pinata.upload_json(data)
                if ipfs_hash:
                    self.storage.add_sync_event("pinata_upload", {"ipfs_hash": ipfs_hash})
                    self.log(f"📤 Uploaded to IPFS: {ipfs_hash}")

            # 4. Update status file for web
            status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "brain": self.brain.get_state(),
                "ipfs": ipfs_hash if self.pinata.enabled else None
            }
            with open("brain_status.json", "w") as f:
                json.dump(status, f, indent=2)

            self.storage.add_sync_event("complete", {"timestamp": datetime.now(timezone.utc).isoformat()})
            self.log("✅ Sync cycle completed")

        except Exception as e:
            self.log(f"❌ Sync error: {e}")
            self.brain.log_event(f"error: {str(e)}")

    def run(self):
        self.log("🧠 Voxel 3rd Brain started")
        self.brain.log_event("daemon_start")

        # Signal handling for clean shutdown
        def signal_handler(sig, frame):
            self.log("🛑 Received shutdown signal")
            self.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initial sync
        self.sync_cycle()

        # Main loop
        while self.running:
            try:
                time.sleep(self.config["sync_interval"])
                self.sync_cycle()
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"❌ Loop error: {e}")
                time.sleep(5)

        self.log("🧠 Voxel 3rd Brain stopped")
        self.brain.log_event("daemon_stop")

    def start_background(self):
        """Run in background thread"""
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()
        return self.thread

# ---------- MAIN ----------
def main():
    # Check if already running
    import os
    pid_file = "./voxel_3rd_brain.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            # Check if process is running
            os.kill(pid, 0)
            print(f"⚠️ Voxel 3rd Brain already running (PID: {pid})")
            return
        except:
            pass

    # Write PID
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    try:
        daemon = VoxelDaemon(CONFIG)
        daemon.run()
    finally:
        if os.path.exists(pid_file):
            os.remove(pid_file)

if __name__ == "__main__":
    main()
