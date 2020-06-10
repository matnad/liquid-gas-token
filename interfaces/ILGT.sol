pragma solidity ^0.6.7;

import "./ILiquidERC20.sol";

interface ILGT is ILiquidERC20 {

    // Minting Tokens
    function mint(uint256 amount) external;
    function mintFor(uint256 amount, address recipient) external;
    function mintToLiquidity(uint256 maxTokens, uint256 minLiquidity, uint256 deadline, address recipient)
        external payable returns (uint256 tokenAmount, uint256 ethAmount, uint256 liquidityCreated);
    function mintToSell(uint256 amount, uint256 minEth, uint256 deadline)
        external returns (uint256 ethBought);
    function mintToSellTo(uint256 amount, uint256 minEth, uint256 deadline, address payable recipient)
        external returns (uint256 ethBought);

    // Freeing Tokens
    function free(uint256 amount) external returns (bool success);
    function freeFrom(uint256 amount, address owner) external returns (bool success);

    // Buying and Freeing Tokens.
    // It is always recommended to check the price for the amount of tokens you intend to buy
    // and then send the exact amount of ether.

    // Will refund excess ether and returns 0 instead of reverting on most errors.
    function buyAndFree(uint256 amount, uint256 deadline, address payable refundTo)
        external payable returns (uint256 ethSold);

    // Spends all ether (no refunds) to buy and free as many tokens as possible.
    function buyMaxAndFree(uint256 deadline)
        external payable returns (uint256 tokensBought);



    // Optimized Functions
    // !!! USE AT YOUR OWN RISK !!!
    // These functions are gas optimized and intended for experienced users.
    // The function names are constructed to have 3 or 4 leading zero bytes
    // in the function selector.
    // Additionally, all checks have been omitted and need to be done before
    // sending the call if desired.
    // There are also no return values to further save gas.
    // !!! USE AT YOUR OWN RISK !!!
    function mintToSell9630191(uint256 amount) external;
    function mintToSellTo25630722(uint256 amount, address payable recipient) external;
    function buyAndFree22457070633(uint256 amount) external payable;

}
