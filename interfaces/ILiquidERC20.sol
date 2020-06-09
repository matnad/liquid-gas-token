pragma solidity ^0.6.7;

import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/token/ERC20/IERC20.sol";

interface ILiquidERC20 is IERC20 {
    
    // Price Query Functions
    function getEthToTokenInputPrice(uint256 ethSold) external view returns(uint256 tokensBought);
    function getEthToTokenOutputPrice(uint256 tokensBought) external view returns (uint256 ethSold);
    function getTokenToEthInputPrice(uint256 tokensSold) external view returns (uint256 ethBought);
    function getTokenToEthOutputPrice(uint256 ethBought) external view returns (uint256 tokensSold);

    // Liquidity Pool
    function poolTotalSupply() external view returns (uint256);
    function poolTokenReserves() external view returns (uint256);
    function poolBalanceOf(address account) external view returns (uint256);
    function addLiquidity(uint256 minLiquidity, uint256 maxTokens, uint256 deadline)
        external payable returns (uint256 liquidityCreated);
    function removeLiquidity(uint256 amount, uint256 minEth, uint256 minTokens, uint256 deadline)
        external returns (uint256 ethAmount, uint256 tokenAmount);

    // Buy Tokens
    function ethToTokenSwapInput(uint256 minTokens, uint256 deadline)
        external payable returns (uint256 tokensBought);
    function ethToTokenTransferInput(uint256 minTokens, uint256 deadline, address recipient)
        external payable returns (uint256 tokensBought);
    function ethToTokenSwapOutput(uint256 tokensBought, uint256 deadline)
        external payable returns (uint256 ethSold);
    function ethToTokenTransferOutput(uint256 tokensBought, uint256 deadline, address recipient)
        external payable returns (uint256 ethSold);

    // Sell Tokens
    function tokenToEthSwapInput(uint256 tokensSold, uint256 minEth, uint256 deadline)
        external returns (uint256 ethBought);
    function tokenToEthTransferInput(uint256 tokensSold, uint256 minEth, uint256 deadline, address payable recipient)
        external returns (uint256 ethBought);
    function tokenToEthSwapOutput(uint256 ethBought, uint256 maxTokens, uint256 deadline)
        external returns (uint256 tokensSold);
    function tokenToEthTransferOutput(uint256 ethBought, uint256 maxTokens, uint256 deadline, address payable recipient)
        external returns (uint256 tokensSold);

    // Events
    event AddLiquidity(
        address indexed provider,
        uint256 indexed eth_amount,
        uint256 indexed token_amount
    );
    event RemoveLiquidity(
        address indexed provider,
        uint256 indexed eth_amount,
        uint256 indexed token_amount
    );
}
