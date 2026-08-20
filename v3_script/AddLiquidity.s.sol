// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "forge-std/console.sol";

interface IWETH {
    function deposit() external payable;
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface INonfungiblePositionManager {
    struct MintParams {
        address token0;
        address token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
        address recipient;
        uint256 deadline;
    }
    function mint(MintParams calldata params) external returns (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1);
}

contract AddLiquidityScript is Script {
    address constant WETH = 0x4200000000000000000000000000000000000006;
    address constant POSITION_MANAGER = 0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1;
    address constant PIDX = 0xd7dEf6924835d83ca11fcd7a16271CA919723e65;
    address deployer = 0x3212D08f2ad637918bd90932829159874E39bE4c;

    function run() external {
        uint256 pk = uint256(vm.envBytes32("PRIVATE_KEY"));
        vm.startBroadcast(pk);

        // 1. Wrap ETH → WETH
        uint256 wethAmount = 0.001 ether;
        IWETH(WETH).deposit{value: wethAmount}();

        // 2. Approve both tokens
        IERC20(WETH).approve(POSITION_MANAGER, type(uint256).max);
        IERC20(PIDX).approve(POSITION_MANAGER, type(uint256).max);

        // 3. Full‑range mint
        uint256 pidxAmount = 1000 * 10**18;

        INonfungiblePositionManager.MintParams memory params = INonfungiblePositionManager.MintParams({
            token0: WETH,
            token1: PIDX,
            fee: 3000,
            tickLower: -887272,
            tickUpper: 887272,
            amount0Desired: wethAmount,
            amount1Desired: pidxAmount,
            amount0Min: 0,
            amount1Min: 0,
            recipient: deployer,
            deadline: block.timestamp + 1800
        });

        INonfungiblePositionManager(POSITION_MANAGER).mint(params);

        vm.stopBroadcast();
        console.log("Uniswap V3 liquidity added successfully!");
    }
}
