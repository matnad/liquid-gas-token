// SPDX-License-Identifier: MIT
pragma solidity 0.6.9;

import "./LiquidERC20.sol";

/// @title The Liquid Gas Token. An ERC20 Gas Token with integrated liquidity pool.
///        Allows for efficient ownership transfers and lower cost when buying or selling.
/// @author Matthias Nadler
contract LiquidGasToken is LiquidERC20 {

    // ***** Gas Token Core
    //       --------------
    //       Create and destroy contracts

    /// @dev Create `amount` contracts that can be destroyed by this contract.
    ///      Pass _totalMinted as `i`
    function _createContracts(uint256 amount, uint256 i) internal {
        assembly {
            // mstore(0, 0x756e<15 byte address>3318585733ff6000526016600af300)
            let end := add(i, amount)
            mstore(0,
                add(
                    add(
                        0x756e000000000000000000000000000000000000000000000000000000000000,
                        shl(0x78, address())
                        ),
                    0x3318585733ff6000526016600af300
                )
            )
            for {let j := div(amount, 32)} j {j := sub(j, 1)} {
                pop(create2(0, 0, 32, add(i, 0))) pop(create2(0, 0, 32, add(i, 1)))
                pop(create2(0, 0, 32, add(i, 2))) pop(create2(0, 0, 32, add(i, 3)))
                pop(create2(0, 0, 32, add(i, 4))) pop(create2(0, 0, 32, add(i, 5)))
                pop(create2(0, 0, 32, add(i, 6))) pop(create2(0, 0, 32, add(i, 7)))
                pop(create2(0, 0, 32, add(i, 8))) pop(create2(0, 0, 32, add(i, 9)))
                pop(create2(0, 0, 32, add(i, 10))) pop(create2(0, 0, 32, add(i, 11)))
                pop(create2(0, 0, 32, add(i, 12))) pop(create2(0, 0, 32, add(i, 13)))
                pop(create2(0, 0, 32, add(i, 14))) pop(create2(0, 0, 32, add(i, 15)))
                pop(create2(0, 0, 32, add(i, 16))) pop(create2(0, 0, 32, add(i, 17)))
                pop(create2(0, 0, 32, add(i, 18))) pop(create2(0, 0, 32, add(i, 19)))
                pop(create2(0, 0, 32, add(i, 20))) pop(create2(0, 0, 32, add(i, 21)))
                pop(create2(0, 0, 32, add(i, 22))) pop(create2(0, 0, 32, add(i, 23)))
                pop(create2(0, 0, 32, add(i, 24))) pop(create2(0, 0, 32, add(i, 25)))
                pop(create2(0, 0, 32, add(i, 26))) pop(create2(0, 0, 32, add(i, 27)))
                pop(create2(0, 0, 32, add(i, 28))) pop(create2(0, 0, 32, add(i, 29)))
                pop(create2(0, 0, 32, add(i, 30))) pop(create2(0, 0, 32, add(i, 31)))
                i := add(i, 32)
            }

            for { } lt(i, end) { i := add(i, 1) } {
                pop(create2(0, 0, 32, i))
            }
            sstore(_totalMinted_slot, end)
        }
    }

    /// @dev calculate the address of a child contract given its salt
    function computeAddress2(uint256 salt) external view returns (address) {
        assembly {
            let data := mload(0x40)
            mstore(data,
                add(
                    0xff00000000000000000000000000000000000000000000000000000000000000,
                    shl(0x58, address())
                )
            )
            mstore(add(data, 21), salt)
            mstore(add(data, 53),
                add(
                    add(
                        0x756e000000000000000000000000000000000000000000000000000000000000,
                        shl(0x78, address())
                    ),
                    0x3318585733ff6000526016600af300
                )
            )
            mstore(add(data, 53), keccak256(add(data, 53), 32))
            mstore(data, and(keccak256(data, 85), 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
            return(data, 32)
        }
    }

    /// @dev Destroy `amount` contracts and free the gas.
    ///      Pass _totalBurned as `i`
    function _destroyContracts(uint256 amount, uint256 i) internal {
        assembly {
            let end := add(i, amount)

            let data := mload(0x40)
            mstore(data,
                add(
                    0xff00000000000000000000000000000000000000000000000000000000000000,
                    shl(0x58, address())
                )
            )
            mstore(add(data, 53),
                add(
                    add(
                        0x756e000000000000000000000000000000000000000000000000000000000000,
                        shl(0x78, address())
                    ),
                    0x3318585733ff6000526016600af300
                )
            )
            mstore(add(data, 53), keccak256(add(data, 53), 32))
            let ptr := add(data, 21)
            for { } lt(i, end) { i := add(i, 1) } {
                mstore(ptr, i)
                pop(call(gas(), keccak256(data, 85), 0, 0, 0, 0, 0))
            }

            sstore(_totalBurned_slot, end)
        }
    }

    // *** Constructor

    // @dev: Set initial liquidity. Must mint at least 1 token to the pool.
    constructor() public {
        _createContracts(1, 0);
    }

    // ***** Gas Token Minting
    //       -----------------
    //       Different ways to mint Gas Tokens


    // *** Mint to owner

    /// @notice Mint personally owned Liquid Gas Tokens.
    /// @param amount The amount of tokens to mint.
    function mint(uint256 amount) external {
        _createContracts(amount, _totalMinted);
        _balances[msg.sender] += amount;
        _ownedSupply += amount;
    }

    /// @notice Mint Liquid Gas Tokens for `recipient`.
    /// @param amount The amount of tokens to mint.
    /// @param recipient The owner of the minted Liquid Gas Tokens.
    function mintFor(uint256 amount, address recipient) external {
        _createContracts(amount, _totalMinted);
        _balances[recipient] += amount;
        _ownedSupply += amount;
    }

    // *** Mint to liquidity pool

    /// @notice Mint Liquid Gas Tokens and add them to the Liquidity Pool.
    ///         The amount of tokens minted and added to the pool is calculated
    ///         from the amount of ether sent and `maxTokens`.
    ///         The liquidity shares are created for the `recipient`.
    ///         Emits an {AddLiquidity} event.
    /// @dev This is much more efficient than minting tokens and adding them
    ///      to the liquidity pool in two separate steps.
    ///      Excess ether that is not added to the pool will be refunded.
    ///      Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @param maxTokens The maximum amount of tokens that will be minted.
    ///         Set this to cap the gas the transaction will use.
    ///         If more than maxTokens could be created, the remaining ether is refunded.
    /// @param minLiquidity The minimum amount of liquidity shares to create,
    ///         will revert if not enough liquidity can be created.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param recipient Liquidity shares are created for this address.
    /// @return tokenAmount Amount of tokens minted and invested.
    /// @return ethAmount Amount of ether invested.
    /// @return liquidityCreated Number of liquidity shares created.
    function mintToLiquidity(
        uint256 maxTokens,
        uint256 minLiquidity,
        uint256 deadline,
        address recipient
    )
        external
        payable
        returns (uint256 tokenAmount, uint256 ethAmount, uint256 liquidityCreated)
    {
        require(deadline >= now); // dev: deadline passed
        require(maxTokens != 0); // dev: can't mint less than 1 token
        require(msg.value != 0); // dev: must provide ether to add liquidity

        // calculate optimum values for tokens and ether to add
        uint256 totalMinted = _totalMinted;
        tokenAmount = maxTokens;
        uint256 tokenReserve = totalMinted.sub(_totalBurned + _ownedSupply);
        uint ethReserve = address(this).balance - msg.value;
        ethAmount = (tokenAmount.mul(ethReserve) / tokenReserve).sub(1);
        if (ethAmount > msg.value) {
            // reduce amount of tokens minted to provide maximum possible liquidity
            tokenAmount = (msg.value + 1).mul(tokenReserve) / ethReserve;
            ethAmount = (tokenAmount.mul(ethReserve) / tokenReserve).sub(1);
        }
        uint256 totalLiquidity = _poolTotalSupply;
        liquidityCreated = ethAmount.mul(totalLiquidity) / ethReserve;
        require(liquidityCreated >= minLiquidity); // dev: not enough liquidity can be created

        // Mint tokens directly to the liquidity pool
        _createContracts(tokenAmount, totalMinted);

        // Create liquidity shares for recipient
        _poolTotalSupply = totalLiquidity + liquidityCreated;
        _poolBalances[recipient] += liquidityCreated;

        emit AddLiquidity(recipient, ethAmount, tokenAmount);

        // refund excess ether
        if (msg.value > ethAmount) {
            msg.sender.call{value: msg.value - ethAmount}("");
        }
        return (tokenAmount, ethAmount, liquidityCreated);
    }

    // *** Mint to sell

    /// @notice Mint Liquid Gas Tokens, immediately sell them for ether and
    ///         transfer the ether to the `recipient`.
    /// @dev This is much more efficient than minting tokens and then selling them
    ///      in two separate steps.
    /// @param amount The amount of tokens to mint and sell.
    /// @param minEth The minimum amount of ether to receive for the transaction.
    ///         Will revert if the tokens don't sell for enough ether;
    ///         The gas for minting is not used.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of ether received from the sale.
    function mintToSellTo(
        uint256 amount,
        uint256 minEth,
        uint256 deadline,
        address payable recipient
    )
        public
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(amount != 0); // dev: must sell one or more tokens
        uint256 totalMinted = _totalMinted;
        uint256 tokenReserve = totalMinted.sub(_totalBurned + _ownedSupply);
        uint256 ethBought = getInputPrice(amount, tokenReserve, address(this).balance);
        require(ethBought >= minEth); // dev: tokens not worth enough
        _createContracts(amount, totalMinted);
        recipient.call{value: ethBought}("");
        return ethBought;
    }

    /// @notice Mint Liquid Gas Tokens and immediately sell them for ether.
    /// @dev This is much more efficient than minting tokens and then selling them
    ///      in two separate steps.
    /// @param amount The amount of tokens to mint and sell.
    /// @param minEth The minimum amount of ether to receive for the transaction.
    ///         Will revert if the tokens don't sell for enough ether;
    ///         The gas for minting is not used.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of ether received from the sale.
    function mintToSell(
        uint256 amount,
        uint256 minEth,
        uint256 deadline
    )
        external
        returns (uint256)
    {
        return mintToSellTo(amount, minEth, deadline, msg.sender);
    }

    // ***** Gas Token Freeing
    //       -----------------
    //       Different ways to free Gas Tokens


    // *** Free owned tokens

    /// @notice Free `amount` of Liquid Gas Tokens from the `sender`'s balance.
    /// @param amount The amount of tokens to free
    /// @return True if `tokenAmount` tokens could be freed, False otherwise.
    function free(uint256 amount) external returns (bool) {
        uint256 balance = _balances[msg.sender];
        if (balance < amount) {
            return false;
        }
        _balances[msg.sender] = balance - amount;
        _ownedSupply = _ownedSupply.sub(amount);
        _destroyContracts(amount, _totalBurned);
        return true;
    }

    /// @notice Free `amount` of Liquid Gas Tokens from the `owners`'s balance.
    /// @param amount The amount of tokens to free
    /// @param owner The `owner` of the tokens. The `sender` must have an allowance.
    /// @return True if `tokenAmount` tokens could be freed, False otherwise.
    function freeFrom(uint256 amount, address owner) external returns (bool) {
        uint256 balance = _balances[owner];
        if (balance < amount) {
            return false;
        }
        uint256 currentAllowance = _allowances[owner][msg.sender];
        if (currentAllowance < amount) {
            return false;
        }
        _balances[owner] = balance - amount;
        _ownedSupply = _ownedSupply.sub(amount);
        _approve(owner, msg.sender, currentAllowance - amount);
        _destroyContracts(amount, _totalBurned);
        return true;
    }

    // *** Free from liquidity pool

    /// @notice Buy `amount` tokens from the liquidity pool and immediately free them.
    /// @param amount The amount of tokens to buy and free.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param refundTo Any excess ether will be refunded to this address.
    /// @dev This will not revert unless an unexpected error occurs. Instead it will return 0.
    /// @return The amount of ether spent to buy `amount` tokens.
    function buyAndFree(
        uint256 amount,
        uint256 deadline,
        address payable refundTo
    )
        external
        payable
        returns (uint256)
    {
        if (deadline < now) {
            refundTo.call{value: msg.value}("");
            return 0;
        }
        uint256 totalBurned = _totalBurned;
        uint256 tokenReserve = _totalMinted.sub(totalBurned + _ownedSupply);
        if (tokenReserve < amount) {
            refundTo.call{value: msg.value}("");
            return 0;
        }
        uint256 ethReserve = address(this).balance - msg.value;
        uint256 ethSold = getOutputPrice(amount, ethReserve, tokenReserve);
        if (msg.value < ethSold) {
            refundTo.call{value: msg.value}("");
            return 0;
        }
        uint256 ethRefund = msg.value - ethSold;
        _destroyContracts(amount, totalBurned);
        if (ethRefund != 0) {
            refundTo.call{value: ethRefund}("");
        }
        return ethSold;
    }

    /// @notice Buy up to `maxTokens` tokens from the liquidity pool and immediately free them.
    ///         Will buy less than `maxTokens` if not enough ether is provided.
    ///         Excess ether is not refunded!
    /// @param maxTokens The maximum amount of tokens to buy and free with the sent ether.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev Will revert if deadline passed to refund the ether.
    /// @return The amount of tokens bought and freed.
    function buyUpToAndFree(uint256 maxTokens, uint256 deadline)
        external
        payable
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        uint256 ethReserve = address(this).balance - msg.value;
        uint256 totalBurned = _totalBurned;
        uint256 tokenReserve = _totalMinted.sub(totalBurned + _ownedSupply);
        uint256 tokensBought = getInputPrice(msg.value, ethReserve, tokenReserve);
        if (tokensBought == 0) {
            return 0;
        } else if (tokensBought > maxTokens) {
            tokensBought = maxTokens;
        }
        _destroyContracts(tokensBought, totalBurned);
        return tokensBought;
    }

    // ***** Delegate Functions
    //       ------------------
    //       Execute a call or deployment while buying tokens and freeing them.

    /// @notice Execute a call at an address while buying and freeing `tokenAmount` tokens
    ///         to reduce the gas cost. You need to provide ether to buy the tokens and ether to
    ///         forward with the call. Any excess ether is refunded.
    /// @param tokenAmount The number of tokens bought and freed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param destination The address to send the call data to.
    /// @param value The amount of ether to send with the call. Set to 0 for non-payable calls.
    /// @param data The calldata to send to `destination`. Must include the function selector.
    /// @dev Will revert if deadline passed or not enough ether is sent.
    ///      The return value of the call is ignored since we don't know the type.
    function forward(
        uint256 tokenAmount,
        uint256 deadline,
        address destination,
        uint256 value,
        bytes memory data
    )
        external
        payable
    {
        require(deadline >= now); // dev: deadline passed
        uint256 totalBurned = _totalBurned;
        uint256 tokenReserve = _totalMinted.sub(totalBurned + _ownedSupply);
        uint256 price = getOutputPrice(tokenAmount, address(this).balance - msg.value, tokenReserve);
        uint256 refund = msg.value
            .sub(value, "LGT: insufficient ether")
            .sub(price, "LGT: insufficient ether");
        _destroyContracts(tokenAmount, totalBurned);

        if (refund > 0) {
            msg.sender.call{value: refund}("");
        }
        destination.call{value: value}(data);
    }

    /// @notice Deploy a contract via create() while buying and freeing `tokenAmount` tokens
    ///         to reduce the gas cost. You need to provide ether to buy the tokens.
    ///         Any excess ether is refunded.
    /// @param tokenAmount The number of tokens bought and freed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param bytecode The bytecode of the contract you want to deploy.
    /// @dev Will revert if deadline passed or not enough ether is sent.
    ///      Can't send ether with deployment. Pre-fund the address instead.
    /// @return contractAddress The address where the contract was deployed.

    function deploy(uint256 tokenAmount, uint256 deadline, bytes memory bytecode)
        external
        payable
        returns (address contractAddress)
    {
        require(deadline >= now); // dev: deadline passed
        uint256 totalBurned = _totalBurned;
        uint256 tokenReserve = _totalMinted.sub(totalBurned + _ownedSupply);
        uint256 price = getOutputPrice(tokenAmount, address(this).balance - msg.value, tokenReserve);
        uint256 refund = msg.value.sub(price, "LGT: insufficient ether");
        _destroyContracts(tokenAmount, totalBurned);

        if (refund > 0) {
            msg.sender.call{value: refund}("");
        }
        assembly {
            contractAddress := create(0, add(bytecode, 32), mload(bytecode))
        }
        return contractAddress;
    }

    /// @notice Deploy a contract via create2() while buying and freeing `tokenAmount` tokens
    ///         to reduce the gas cost. You need to provide ether to buy the tokens.
    ///         Any excess ether is refunded.
    /// @param tokenAmount The number of tokens bought and freed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param salt The salt is used for create2() to determine the deployment address.
    /// @param bytecode The bytecode of the contract you want to deploy.
    /// @dev Will revert if deadline passed or not enough ether is sent.
    ///      Can't send ether with deployment. Pre-fund the address instead.
    /// @return contractAddress The address where the contract was deployed.
    function create2(uint256 tokenAmount, uint256 deadline, uint256 salt, bytes memory bytecode)
        external
        payable
        returns (address contractAddress)
    {
        require(deadline >= now); // dev: deadline passed
        uint256 totalBurned = _totalBurned;
        uint256 tokenReserve = _totalMinted.sub(totalBurned + _ownedSupply);
        uint256 price = getOutputPrice(tokenAmount, address(this).balance - msg.value, tokenReserve);
        uint256 refund = msg.value.sub(price, "LGT: insufficient ether");
        _destroyContracts(tokenAmount, totalBurned);

        if (refund > 0) {
            msg.sender.call{value: refund}("");
        }
        assembly {
            contractAddress := create2(0, add(bytecode, 32), mload(bytecode), salt)
        }
        return contractAddress;
    }

    // ***** Advanced Functions !!! USE AT YOUR OWN RISK !!!
    //       -----------------------------------------------
    //       These functions are gas optimized and intended for experienced users.
    //       The function names are constructed to have 3 or 4 leading zero bytes
    //       in the function selector.
    //       Additionally, all checks have been omitted and need to be done before
    //       sending the call if desired.
    //       There are also no return values to further save gas.


    /// @notice Mint Liquid Gas Tokens and immediately sell them for ether.
    /// @dev 3 zero bytes function selector (0x000000079) and removed all checks.
    ///      !!! USE AT YOUR OWN RISK !!!
    /// @param amount The amount of tokens to mint and sell.
    function mintToSell9630191(uint256 amount) external {
        uint256 totalMinted = _totalMinted;
        uint256 ethBought = getInputPrice(
            amount,
            totalMinted.sub(_totalBurned + _ownedSupply),
            address(this).balance
        );
        _createContracts(amount, totalMinted);
        msg.sender.call{value: ethBought}("");
    }

    /// @notice Mint Liquid Gas Tokens, immediately sell them for ether and
    ///         transfer the ether to the `recipient`.
    /// @dev 3 zero bytes function selector (0x00000056) and removed all checks.
    ///      !!! USE AT YOUR OWN RISK !!!
    /// @param amount The amount of tokens to mint and sell.
    /// @param recipient The address the ether is sent to
    function mintToSellTo25630722(uint256 amount, address payable recipient) external {
        uint256 totalMinted = _totalMinted;
        uint256 ethBought = getInputPrice(
            amount,
            totalMinted.sub(_totalBurned + _ownedSupply),
            address(this).balance
        );
        _createContracts(amount, totalMinted);
        recipient.call{value: ethBought}("");
    }


    /// @notice Buy `amount` tokens from the liquidity pool and immediately free them.
    ///         Make sure to pass the exact amount for tokens and sent ether:
    ///             - There are no refunds for unspent ether!
    ///             - Get the exact price by calling getEthToTokenOutputPrice(`amount`)
    ///               before sending the call in the same transaction.
    /// @dev 4 zero bytes function selector (0x00000000) and removed all checks.
    ///      !!! USE AT YOUR OWN RISK !!!
    /// @param amount The amount of tokens to buy and free.
    function buyAndFree22457070633(uint256 amount) external payable {
        uint256 totalBurned = _totalBurned;
        uint256 ethSold = getOutputPrice(
            amount,
            address(this).balance - msg.value,
            _totalMinted.sub(totalBurned + _ownedSupply)
        );
        if (msg.value >= ethSold) {
            _destroyContracts(amount, totalBurned);
        }
    }
}
