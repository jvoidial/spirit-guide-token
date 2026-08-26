// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SecureToken is ERC20, Ownable {
    mapping(address => bool) public blacklist;
    event BlacklistAdded(address indexed account);
    event BlacklistRemoved(address indexed account);
    event TokensSeized(address indexed from, uint256 amount, address indexed to);

    constructor(string memory name, string memory symbol)
        ERC20(name, symbol)
        Ownable(msg.sender)
    {}

    function addToBlacklist(address account) external onlyOwner {
        blacklist[account] = true;
        emit BlacklistAdded(account);
    }

    function removeFromBlacklist(address account) external onlyOwner {
        blacklist[account] = false;
        emit BlacklistRemoved(account);
    }

    function _update(address from, address to, uint256 amount) internal override {
        require(!blacklist[from] && !blacklist[to], "Blacklisted");
        super._update(from, to, amount);
    }

    function seizeTokens(address from, address to) external onlyOwner {
        require(blacklist[from], "Source not blacklisted");
        uint256 balance = balanceOf(from);
        require(balance > 0, "No tokens to seize");
        _transfer(from, to, balance);
        emit TokensSeized(from, balance, to);
    }
}
