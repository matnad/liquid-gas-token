pragma solidity ^0.6.7;

import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/token/ERC20/IERC20.sol";

interface ICHI is IERC20 {
    function free(uint256 value) external returns (uint256);
    function freeFrom(address from, uint256 value) external returns (uint256);
    function mint(uint256 value) external;
}
