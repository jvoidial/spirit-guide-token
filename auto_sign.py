#!/usr/bin/env python3
import os, re, json, subprocess
from pathlib import Path
from web3 import Web3
from eth_account.messages import encode_defunct

# The deployer address
DEPLOYER = "0x3212d08f2ad637918bd90932829159874e39be4c"
# The exact message from BaseScan
MESSAGE = "[basescan.org 21/08/2026 21:58:34] I, hereby verify that I am the owner/creator of the address [0x38e4f08d08b4d772a7b75669c356b4749dd2d30b]"

def find_private_key():
    """Search for the private key in common locations."""
    # 1. Environment variables
    for env_var in ["PRIVATE_KEY", "DEPLOYER_PRIVATE_KEY", "DEPLOYER_KEY"]:
        key = os.getenv(env_var)
        if key:
            return key.strip()
    # 2. .env files
    for env_file in [".env", "../.env", ".env.local"]:
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                match = re.search(r'PRIVATE_KEY\s*=\s*([a-fA-F0-9]{64})', content)
                if match:
                    return match.group(1)
        except:
            pass
    # 3. JSON keystore files (try to extract, but need password – skip for now)
    # 4. Look for any file containing the deployer address and a hex string nearby
    # (risky, but we'll search for 64-char hex in common files)
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh') or file.endswith('.json') or file == '.env':
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        # Look for 64-char hex (private key without 0x)
                        match = re.search(r'([a-fA-F0-9]{64})', content)
                        if match:
                            # Heuristic: if the file also contains the deployer address, it's likely the key
                            if DEPLOYER.lower() in content.lower():
                                return match.group(1)
                except:
                    pass
    return None

def generate_signature(private_key):
    """Generate the signature hash."""
    msg = encode_defunct(text=MESSAGE)
    signed = Web3().eth.account.sign_message(msg, private_key=private_key)
    return signed.signature.hex()

def main():
    print("🔍 Searching for private key...")
    key = find_private_key()
    if key:
        print("✅ Private key found.")
        # Validate it's 64 hex chars
        if re.fullmatch(r'[a-fA-F0-9]{64}', key):
            sig = generate_signature(key)
            print("\n📝 Signature Hash (copy this):")
            print("0x" + sig)
            print("\nLength:", len("0x" + sig), "(should be 132)")
        else:
            print("⚠️ Found key but it seems invalid (not 64 hex chars).")
            print("Please sign manually using MetaMask.")
            show_manual_instructions()
    else:
        print("❌ Private key not found in scanned locations.")
        show_manual_instructions()

def show_manual_instructions():
    print("\n🧠 Please sign the message manually with MetaMask:")
    print("1. Open MetaMask and switch to the deployer account:")
    print("   " + DEPLOYER)
    print("2. Go to Settings → Advanced → 'Sign Message'")
    print("3. Paste this exact message:")
    print("\n   " + MESSAGE)
    print("\n4. Click Sign and copy the resulting 0x... string.")
    print("5. Paste it into BaseScan's 'Signature Hash' field.")

if __name__ == "__main__":
    main()
