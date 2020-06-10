// SPDX-License-Identifier: MIT
pragma solidity 0.6.9;

import "../interfaces/ILGT.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/math/SafeMath.sol";

contract LGTRelayer {
    using SafeMath for uint256;
    ILGT public constant lgt = ILGT(0x000000000049091F98692b2460500B6D133ae31F);

    /// @notice Forward a call, buy and free as many tokens as possible for the fixed
    ///         amount of ether - `value` sent with this transaction.
    /// @param deadline The time after which the transaction can no longer be executed.
    /// @param destination The address where the call is sent to.
    /// @param value The amount of ether to pass with the call.
    /// @param data The calldata to send to the `destination`.
    /// @return tokensBought The amount of tokens bought and freed.
    function forwardMax(
        uint256 deadline,
        address destination,
        uint256 value,
        bytes memory data
    )
    external
    payable
    returns (uint256)
    {
        require(value <= msg.value);
        uint256 tokensBought = lgt.buyMaxAndFree{value : msg.value - value}(deadline);
        destination.call{value : value}(data);
        return tokensBought;
    }

    /// @notice Forward a call, buy and free `tokenAmount` of tokens.
    ///         Any remaining ether is refunded.
    ///         If not enough ether is sent, no purchase happens and everything is refunded.
    /// @param tokenAmount The amount of tokens to buy and free.
    /// @param deadline The time after which the transaction can no longer be executed.
    /// @param destination The address where the call is sent to.
    /// @param value The amount of ether to pass with the call.
    /// @param data The calldata to send to the `destination`.
    /// @return ethSold The amount of ether spent to buy the tokens, the rest is refunded.
    function forward(
        uint256 tokenAmount,
        uint256 deadline,
        address destination,
        uint256 value,
        bytes memory data
    )
    external
    payable
    returns (uint256)
    {
        require(value <= msg.value);
        uint256 ethSold = lgt.buyAndFree{value : msg.value - value}(tokenAmount, deadline, msg.sender);
        destination.call{value : value}(data);
        return ethSold;
    }

    /// @notice Calculate the optimal amount of tokens and buy them if costs can be reduced.
    ///         Otherwise, execute the transaction without buying tokens.
    /// @dev optimal tokens = (gas_cost + overhead) // 41300
    ///      overhead = ~55000
    function forwardAuto(
        address destination,
        uint256 value,
        bytes memory data
    )
        external
        payable
        returns (uint256 optimalTokens, uint256 buyCost)
    {
        uint256 initialGas = gasleft();
        require(value <= msg.value);
        destination.call{value : value}(data);
        optimalTokens = (initialGas - gasleft() + 55000) / 41300;
        if (optimalTokens > 0) {
            buyCost = lgt.getEthToTokenOutputPrice(optimalTokens);
            if (buyCost < ((18145 * optimalTokens) - 24000) * tx.gasprice) {
                lgt.buyAndFree{value : msg.value - value}(optimalTokens, now, msg.sender);
            } else {
                msg.sender.call{value : msg.value - value}("");
            }
        } else {
            msg.sender.call{value : msg.value - value}("");
        }
        return (optimalTokens, buyCost);
    }
}