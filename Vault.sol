
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

interface IPenniesIndex {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
}

contract IndexVault {
    IPenniesIndex public PIDX;
    address public owner;

    address constant PENNIES = 0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7;
    address constant SGUIDE  = 0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a;
    address constant VDOO    = 0x38e4f08D08b4D772A7B75669C356b4749dd2d30b;
    address constant WBTC    = 0x0555E30da8f98308EdB960aa94C0Db47230d2B9c;

    uint256 constant WEIGHT_PENNIES = 40;
    uint256 constant WEIGHT_SGUIDE  = 30;
    uint256 constant WEIGHT_VDOO    = 20;
    uint256 constant WEIGHT_WBTC    = 10;
    uint256 constant TOTAL_WEIGHT   = 100;

    constructor(address _pidx) {
        PIDX = IPenniesIndex(_pidx);
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    function deposit(uint256 pidxAmount) external {
        uint256 penniesAmount = (pidxAmount * WEIGHT_PENNIES) / TOTAL_WEIGHT;
        uint256 sguideAmount  = (pidxAmount * WEIGHT_SGUIDE)  / TOTAL_WEIGHT;
        uint256 vdooAmount    = (pidxAmount * WEIGHT_VDOO)    / TOTAL_WEIGHT;
        uint256 wbtcAmount    = (pidxAmount * WEIGHT_WBTC)    / TOTAL_WEIGHT;

        require(_transferFrom(PENNIES, msg.sender, address(this), penniesAmount), "pennies transfer failed");
        require(_transferFrom(SGUIDE, msg.sender, address(this), sguideAmount), "sguide transfer failed");
        require(_transferFrom(VDOO, msg.sender, address(this), vdooAmount), "vdoo transfer failed");
        require(_transferFrom(WBTC, msg.sender, address(this), wbtcAmount), "wbtc transfer failed");

        PIDX.mint(msg.sender, pidxAmount);
    }

    function redeem(uint256 pidxAmount) external {
        PIDX.burn(msg.sender, pidxAmount);

        uint256 penniesAmount = (pidxAmount * WEIGHT_PENNIES) / TOTAL_WEIGHT;
        uint256 sguideAmount  = (pidxAmount * WEIGHT_SGUIDE)  / TOTAL_WEIGHT;
        uint256 vdooAmount    = (pidxAmount * WEIGHT_VDOO)    / TOTAL_WEIGHT;
        uint256 wbtcAmount    = (pidxAmount * WEIGHT_WBTC)    / TOTAL_WEIGHT;

        require(_transfer(PENNIES, msg.sender, penniesAmount), "pennies transfer failed");
        require(_transfer(SGUIDE, msg.sender, sguideAmount), "sguide transfer failed");
        require(_transfer(VDOO, msg.sender, vdooAmount), "vdoo transfer failed");
        require(_transfer(WBTC, msg.sender, wbtcAmount), "wbtc transfer failed");
    }

    function _transferFrom(address token, address from, address to, uint256 amount) internal returns (bool) {
        (bool success, ) = token.call(abi.encodeWithSignature("transferFrom(address,address,uint256)", from, to, amount));
        return success;
    }

    function _transfer(address token, address to, uint256 amount) internal returns (bool) {
        (bool success, ) = token.call(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
        return success;
    }
}
