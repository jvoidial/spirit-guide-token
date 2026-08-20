// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address,address,uint256) external returns(bool);
    function approve(address,uint256) external returns(bool);
}

interface IUniswapV2Router {
    function addLiquidity(address,address,uint,uint,uint,uint,address,uint) external payable returns(uint,uint,uint);
    function WETH() external view returns(address);
}

contract LiquidityEngine {
    IERC20 public token;
    IUniswapV2Router public router;
    address public owner;

    constructor(address _token, address _router) {
        token = IERC20(_token);
        router = IUniswapV2Router(_router);
        owner = msg.sender;
    }

    function addLiquidity(uint tokenAmount, uint ethAmount) external {
        require(msg.sender == owner);
        token.transferFrom(msg.sender, address(this), tokenAmount);
        token.approve(address(router), tokenAmount);
        router.addLiquidity{value: ethAmount}(address(token), router.WETH(), tokenAmount, ethAmount, 0, 0, msg.sender, block.timestamp);
    }
}
