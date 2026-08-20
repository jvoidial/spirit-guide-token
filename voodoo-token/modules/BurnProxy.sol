// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract BurnProxy {
    IERC20 public immutable token;
    address public immutable dead = address(0xdead);
    uint256 public constant BURN_FEE = 100; // 1%

    event Transfer(address indexed from, address indexed to, uint256 amount, uint256 burned);

    constructor(IERC20 _token) {
        token = _token;
    }

    function transfer(address from, address to, uint256 amount) external {
        uint256 burnAmount = (amount * BURN_FEE) / 10000;
        uint256 sendAmount = amount - burnAmount;
        if (burnAmount > 0) {
            token.transferFrom(from, dead, burnAmount);
        }
        token.transferFrom(from, to, sendAmount);
        emit Transfer(from, to, sendAmount, burnAmount);
    }
}
