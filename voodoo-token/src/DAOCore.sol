// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DAOCore {
    address public admin;
    uint256 public constant MIN_DELAY = 1 days;
    mapping(bytes32 => uint256) public timelock;
    event Proposed(bytes32 indexed proposal, uint256 eta);
    event Executed(bytes32 indexed proposal);
    modifier onlyAdmin() { require(msg.sender == admin, "Only admin"); _; }
    constructor() { admin = msg.sender; }
    function propose(bytes32 proposal) external onlyAdmin {
        timelock[proposal] = block.timestamp + MIN_DELAY;
        emit Proposed(proposal, timelock[proposal]);
    }
    function execute(bytes32 proposal) external onlyAdmin {
        require(timelock[proposal] != 0 && block.timestamp >= timelock[proposal], "Not ready");
        require(timelock[proposal] != 1, "Already executed");
        timelock[proposal] = 1;
        emit Executed(proposal);
    }
    function transferAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }
}
