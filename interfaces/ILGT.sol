pragma solidity ^0.6.7;

import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/token/ERC20/IERC20.sol";

interface ILGT is IERC20 {
    function free(uint256 tokenAmount) external returns (bool success);
    function freeFrom(uint256 tokenAmount, address owner) external returns (bool success);
    function buyAndFree(uint256 tokenAmount, uint256 deadline, address payable refundTo) external payable returns (uint256 ethSold);
    function buyUpToAndFree(uint256 maxTokens, uint256 deadline) external payable returns (uint256 tokensBought);
    function getEthToTokenOutputPrice(uint256 tokensBought) external view returns (uint256);
    function getTokenToEthInputPrice(uint256 tokensSold) external view returns (uint256);
}
