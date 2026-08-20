// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 {
    function transferFrom(address,address,uint256) external returns(bool);
    function transfer(address,uint256) external returns(bool);
}
contract StakingVault {
    IERC20 public stakingToken;
    address public owner;
    uint256 public rewardRate;
    constructor(address _token) { stakingToken = IERC20(_token); owner = msg.sender; }
    function stake(uint256 amount) external {
        stakingToken.transferFrom(msg.sender, address(this), amount);
    }
    function setRewardRate(uint256 _rate) external {
        require(msg.sender == owner); rewardRate = _rate;
    }
}
