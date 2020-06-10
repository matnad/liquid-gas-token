pragma solidity ^0.6.7;

interface ILGTRelayer {

    // Forward calldata and `value` to `destination` and buy exactly `tokenAmount`
    function forward(uint256 tokenAmount, uint256 deadline, address destination, uint256 value, bytes memory data)
        external payable returns (uint256 ethSold);

    // Forward calldata and `value` to `destination` and buy as much tokens as possible with the passed ether
    function forwardMax(uint256 deadline, address destination, uint256 value, bytes memory data)
        external payable returns (uint256 tokensBought);

    // Forward calldata and `value` to `destination`. Calculate optimal amount of tokens to buy and check
    // if it is profitable at the current gas price. If all is good, buy tokens and free them.
    // This is not exact science, use with caution.
    function forwardAuto(address destination, uint256 value, bytes memory data)
        external payable returns (uint256 optimalTokens, uint256 buyCost);

}
