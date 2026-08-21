import os, json, time, sys, subprocess, re
from web3 import Web3

# -------------------- CONFIG --------------------
RPC = "https://mainnet.base.org"
PRIVATE_KEY = "1955255138c5f0a45e71fe6efb6f81d9c8ea83058f0795c3d5f9623c7dc3498a"
DEPLOYER = Web3.to_checksum_address("0x3212D08f2ad637918bd90932829159874E39bE4c")
OLD_PIDX = Web3.to_checksum_address("0xd7dEf6924835d83ca11fcd7a16271CA919723e65")

# Underlying tokens (checksummed)
PENNIES = Web3.to_checksum_address("0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a")
SGUIDE  = Web3.to_checksum_address("0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7")
VDOO    = Web3.to_checksum_address("0x38e4f08D08b4D772A7B75669C356b4749dd2d30b")
WBTC    = Web3.to_checksum_address("0x0555E30da8f98308EdB960aa94C0Db47230d2B9c")  # official Base WBTC
ROUTER  = Web3.to_checksum_address("0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24")

# -------------------- Connect --------------------
w3 = Web3(Web3.HTTPProvider(RPC))
account = w3.eth.account.from_key(PRIVATE_KEY)

def send_tx(tx, desc=""):
    print(f"   {desc}...")
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction")
    tx_hash = w3.eth.send_raw_transaction(raw)
    print(f"   TX: {tx_hash.hex()[:10]}...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    if receipt.status != 1:
        print(f"   ❌ Failed: {tx_hash.hex()}")
        return None
    print(f"   ✅ Confirmed")
    return receipt

def get_nonce():
    return w3.eth.get_transaction_count(DEPLOYER, "pending")

# -------------------- Write Solidity files --------------------
PIDX_SOL = f"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract PenniesIndex is ERC20, AccessControl {{
    bytes32 public constant VAULT_ROLE = keccak256("VAULT_ROLE");

    constructor() ERC20("Pennies Index", "PIDX") {{
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }}

    function mint(address to, uint256 amount) external onlyRole(VAULT_ROLE) {{
        _mint(to, amount);
    }}

    function burn(address from, uint256 amount) external onlyRole(VAULT_ROLE) {{
        _burn(from, amount);
    }}

    function grantVaultRole(address vault) external onlyRole(DEFAULT_ADMIN_ROLE) {{
        _grantRole(VAULT_ROLE, vault);
    }}
}}
"""

VAULT_SOL = f"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IPenniesIndex {{
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
}}

contract IndexVault is Ownable {{
    IERC20 public constant PENNIES = IERC20({PENNIES});
    IERC20 public constant SGUIDE  = IERC20({SGUIDE});
    IERC20 public constant VDOO    = IERC20({VDOO});
    IERC20 public constant WBTC    = IERC20({WBTC});

    IPenniesIndex public PIDX;

    uint256 public constant WEIGHTS = 40; // base weight for PENNIES

    constructor(address _pidx) {{
        PIDX = IPenniesIndex(_pidx);
    }}

    function deposit(uint256 pidxAmount) external {{
        uint256 penniesAmount = (pidxAmount * 40) / 100;
        uint256 sguideAmount  = (pidxAmount * 30) / 100;
        uint256 vdooAmount    = (pidxAmount * 20) / 100;
        uint256 wbtcAmount    = (pidxAmount * 10) / 100;

        PENNIES.transferFrom(msg.sender, address(this), penniesAmount);
        SGUIDE.transferFrom(msg.sender, address(this), sguideAmount);
        VDOO.transferFrom(msg.sender, address(this), vdooAmount);
        WBTC.transferFrom(msg.sender, address(this), wbtcAmount);

        PIDX.mint(msg.sender, pidxAmount);
    }}

    function redeem(uint256 pidxAmount) external {{
        PIDX.burn(msg.sender, pidxAmount);

        uint256 penniesAmount = (pidxAmount * 40) / 100;
        uint256 sguideAmount  = (pidxAmount * 30) / 100;
        uint256 vdooAmount    = (pidxAmount * 20) / 100;
        uint256 wbtcAmount    = (pidxAmount * 10) / 100;

        PENNIES.transfer(msg.sender, penniesAmount);
        SGUIDE.transfer(msg.sender, sguideAmount);
        VDOO.transfer(msg.sender, vdooAmount);
        WBTC.transfer(msg.sender, wbtcAmount);
    }}
}}
"""

with open("PIDX.sol", "w") as f:
    f.write(PIDX_SOL)
with open("Vault.sol", "w") as f:
    f.write(VAULT_SOL)

print("📝 Solidity source files written.")

# -------------------- Compile with solc --------------------
def compile_contracts():
    cmd = [
        "solc",
        "--combined-json", "abi,bin",
        "--allow-paths", ".",
        "--base-path", ".",
        "--include-path", "lib",
        "PIDX.sol", "Vault.sol"
    ]
    env = os.environ.copy()
    env["SOLC_REMAPPINGS"] = "@openzeppelin/=lib/openzeppelin-contracts/"
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print("❌ Compilation failed:")
        print(result.stderr)
        sys.exit(1)
    # Parse JSON output
    data = json.loads(result.stdout)
    contracts = data["contracts"]
    pidx_data = contracts["PIDX.sol:PenniesIndex"]
    vault_data = contracts["Vault.sol:IndexVault"]
    pidx_abi = json.loads(pidx_data["abi"])
    pidx_bytecode = "0x" + pidx_data["bin"]
    vault_abi = json.loads(vault_data["abi"])
    vault_bytecode = "0x" + vault_data["bin"]
    return pidx_abi, pidx_bytecode, vault_abi, vault_bytecode

print("🔨 Compiling contracts with solc...")
pidx_abi, pidx_bytecode, vault_abi, vault_bytecode = compile_contracts()
print("✅ Compiled successfully.")

# -------------------- Deploy new PIDX --------------------
print("🚀 Deploying new PIDX contract...")
nonce = get_nonce()
gas_price = w3.eth.gas_price
tx = {
    "from": DEPLOYER,
    "data": pidx_bytecode,
    "gas": 3000000,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 8453,
}
receipt = send_tx(tx, "deploy PIDX")
if not receipt: sys.exit(1)
NEW_PIDX = receipt.contractAddress
print(f"✅ New PIDX deployed at: {NEW_PIDX}")

# -------------------- Deploy Vault --------------------
print("🚀 Deploying Vault contract...")
from web3.contract import Contract
vault_contract = w3.eth.contract(abi=vault_abi, bytecode=vault_bytecode)
nonce = get_nonce()
tx = vault_contract.constructor(NEW_PIDX).build_transaction({
    "from": DEPLOYER,
    "gas": 3000000,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 8453,
})
receipt = send_tx(tx, "deploy Vault")
if not receipt: sys.exit(1)
VAULT_ADDR = receipt.contractAddress
print(f"✅ Vault deployed at: {VAULT_ADDR}")

# -------------------- Grant vault role --------------------
print("🔐 Granting VAULT_ROLE to vault...")
pidx_contract = w3.eth.contract(address=NEW_PIDX, abi=pidx_abi)
nonce = get_nonce()
tx = pidx_contract.functions.grantVaultRole(VAULT_ADDR).build_transaction({
    "from": DEPLOYER,
    "gas": 200000,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 8453,
})
if not send_tx(tx, "grant role"): sys.exit(1)

# -------------------- Airdrop new PIDX to old holders --------------------
print("🪂 Airdropping new PIDX to old holders...")
old_holders = [DEPLOYER]
try:
    with open("airdrop_list.json") as f:
        old_holders += json.load(f)
except:
    print("   No airdrop_list.json found, using deployer only.")

old_pidx = w3.eth.contract(address=OLD_PIDX, abi=pidx_abi)
total_to_airdrop = 0
holder_amounts = {}
for addr in set(old_holders):
    addr = Web3.to_checksum_address(addr)
    bal = old_pidx.functions.balanceOf(addr).call()
    if bal > 0:
        holder_amounts[addr] = bal
        total_to_airdrop += bal

print(f"   Total old PIDX circulating: {total_to_airdrop/1e18:.0f} PIDX")
print(f"   Airdropping to {len(holder_amounts)} addresses.")

for addr, amount in holder_amounts.items():
    nonce = get_nonce()
    tx = pidx_contract.functions.mint(addr, amount).build_transaction({
        "from": DEPLOYER,
        "gas": 200000,
        "gasPrice": gas_price,
        "nonce": nonce,
        "chainId": 8453,
    })
    if not send_tx(tx, f"mint {amount/1e18:.0f} to {addr[:10]}"):
        print(f"   Skipping {addr}")
        continue

# -------------------- Add liquidity (optional) --------------------
print("💧 Adding liquidity to SushiSwap with new PIDX...")
# Approve router
nonce = get_nonce()
tx = pidx_contract.functions.approve(ROUTER, 300 * 10**18).build_transaction({
    "from": DEPLOYER,
    "gas": 150000,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 8453,
})
if not send_tx(tx, "approve router"): sys.exit(1)

router_abi = [{"constant": False, "inputs": [{"name": "token", "type": "address"}, {"name": "amountTokenDesired", "type": "uint256"}, {"name": "amountTokenMin", "type": "uint256"}, {"name": "amountETHMin", "type": "uint256"}, {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], "name": "addLiquidityETH", "outputs": [{"name": "amountToken", "type": "uint256"}, {"name": "amountETH", "type": "uint256"}, {"name": "liquidity", "type": "uint256"}], "stateMutability": "payable", "type": "function"}]
router = w3.eth.contract(address=ROUTER, abi=router_abi)
nonce = get_nonce()
tx = router.functions.addLiquidityETH(
    NEW_PIDX,
    300 * 10**18,
    0,
    0,
    DEPLOYER,
    int(time.time()) + 1800
).build_transaction({
    "from": DEPLOYER,
    "value": int(0.0003 * 1e18),
    "gas": 400000,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 8453,
})
if send_tx(tx, "addLiquidity"):
    print("✅ Liquidity added.")
else:
    print("❌ Liquidity addition failed (you can add manually).")

# -------------------- Final Output --------------------
print("\n" + "="*60)
print("  🎉 DEPLOYMENT COMPLETE")
print("="*60)
print(f"New PIDX (mint/burn): {NEW_PIDX}")
print(f"Vault:                {VAULT_ADDR}")
print(f"Old PIDX:             {OLD_PIDX}")
print("\nNext steps:")
print("1. Verify contracts on BaseScan.")
print("2. Add more liquidity.")
print("3. Promote the vault.")
print("4. Users can now deposit the basket and mint PIDX.")
print("   Vault functions: deposit(pidxAmount) and redeem(pidxAmount).")
print("   Underlying tokens: PENNIES, SGUIDE, VDOO, WBTC.")
