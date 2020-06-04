pragma solidity ^0.6.7;

import "./LiquidERC20.sol";

/// @title The Liquid Gas Token. An ERC20 Gas Token with integrated liquidity pool.
///        Allows for efficient ownership transfers and lower cost when buying or selling.
/// @author Matthias Nadler
contract LiquidGasToken is LiquidERC20 {

    // ***** Gas Token Core
    //       --------------
    //       Create and destroy contracts

    /// @dev Create `amount` contracts that can be destroyed by this contract.
    function _createContracts(uint256 amount) internal {
        uint256 offset = totalMinted();
        assembly {
            // mstore(0, 0x756e<15 byte address>3318585733ff6000526016600af300)
            mstore(0,
                add(
                    add(
                        0x756e000000000000000000000000000000000000000000000000000000000000,
                        shl(0x78, address())
                        ),
                    0x3318585733ff6000526016600af300
                )
            )
            for {let i := div(amount, 32)} i {i := sub(i, 1)} {
                pop(create2(0, 0, 32, add(offset, 0))) pop(create2(0, 0, 32, add(offset, 1)))
                pop(create2(0, 0, 32, add(offset, 2))) pop(create2(0, 0, 32, add(offset, 3)))
                pop(create2(0, 0, 32, add(offset, 4))) pop(create2(0, 0, 32, add(offset, 5)))
                pop(create2(0, 0, 32, add(offset, 6))) pop(create2(0, 0, 32, add(offset, 7)))
                pop(create2(0, 0, 32, add(offset, 8))) pop(create2(0, 0, 32, add(offset, 9)))
                pop(create2(0, 0, 32, add(offset, 10))) pop(create2(0, 0, 32, add(offset, 11)))
                pop(create2(0, 0, 32, add(offset, 12))) pop(create2(0, 0, 32, add(offset, 13)))
                pop(create2(0, 0, 32, add(offset, 14))) pop(create2(0, 0, 32, add(offset, 15)))
                pop(create2(0, 0, 32, add(offset, 16))) pop(create2(0, 0, 32, add(offset, 17)))
                pop(create2(0, 0, 32, add(offset, 18))) pop(create2(0, 0, 32, add(offset, 19)))
                pop(create2(0, 0, 32, add(offset, 20))) pop(create2(0, 0, 32, add(offset, 21)))
                pop(create2(0, 0, 32, add(offset, 22))) pop(create2(0, 0, 32, add(offset, 23)))
                pop(create2(0, 0, 32, add(offset, 24))) pop(create2(0, 0, 32, add(offset, 25)))
                pop(create2(0, 0, 32, add(offset, 26))) pop(create2(0, 0, 32, add(offset, 27)))
                pop(create2(0, 0, 32, add(offset, 28))) pop(create2(0, 0, 32, add(offset, 29)))
                pop(create2(0, 0, 32, add(offset, 30))) pop(create2(0, 0, 32, add(offset, 31)))
                offset := add(offset, 32)
            }

            for {let i := and(amount, 0x1F)} i {i := sub(i, 1)} {
                pop(create2(0, 0, 32, offset))
                offset := add(offset, 1)
            }
        }
    }

    /// @dev calculate the address of a child contract given its salt and hashed bytecode
    function computeAddress2(uint256 salt, bytes32 deployHash) internal view returns (address) {
        bytes32 data = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                deployHash
            )
        );
        return address(uint256(data));
    }

    /// @dev destroy `amount` contracts to get gas refunds
    function _destroyContracts(uint256 amount) internal {
        uint256 totalBurned = totalBurned();
        bytes32 deployHash;
        assembly {
            mstore(0,
                add(
                    add(
                        0x756e000000000000000000000000000000000000000000000000000000000000,
                        shl(0x78, address())
                    ),
                    0x3318585733ff6000526016600af300
                )
            )
            deployHash := keccak256(0, 32)
        }
        for (uint256 i = totalBurned; i < totalBurned + amount; i++) {
            computeAddress2(i, deployHash).call("");
        }
    }

    // ***** Gas Token Minting
    //       -----------------
    //       Different ways to mint Gas Tokens


    // *** Mint to owner

    /// @dev Mint tokens directly to the liquidity pool
    function _createUnowned(uint256 amount) internal {
        _createContracts(amount);
        _mint_unowned(amount);
    }

    /// @notice Mint personally owned Liquid Gas Tokens
    /// @param amount The amount of tokens to mint
    function mint(uint256 amount) public {
        _createContracts(amount);
        _mint(msg.sender, amount);
    }

    /// @notice Mint Liquid Gas Tokens for `recipient`
    /// @param amount The amount of tokens to mint
    /// @param recipient The owner of the minted Liquid Gas Tokens
    function mintFor(uint256 amount, address recipient) public {
        _createContracts(amount);
        _mint(recipient, amount);
    }

    // *** Mint to liquidity pool

    /// @dev Use return values to avoid stack too deep error
    function _mintToLiquidityFor(
        uint256 maxTokens,
        uint256 minLiquidity,
        uint256 deadline,
        address recipient
    )
        internal
        returns (uint256 tokenAmount, uint256 ethAmount, uint256 liquidityCreated)
    {
        require(deadline >= now); // dev: deadline passed
        require(maxTokens > 0); // dev: can't mint less than 1 token
        require(msg.value > 0); // dev: must provide ether to add liquidity

        // calculate optimum values for tokens and ether to add
        uint256 totalLiquidity = poolTotalSupply();
        tokenAmount = maxTokens;
        ethAmount = msg.value;
        if (totalLiquidity > 0) {
            uint256 ethReserve = address(this).balance.sub(msg.value);
            uint256 tokenReserve = tokenReserve();
            ethAmount = maxTokens.mul(ethReserve).div(tokenReserve).sub(1);
            if (ethAmount > msg.value) {
                // reduce amount of tokens minted to provide maximum possible liquidity
                tokenAmount = (msg.value.add(1)).mul(tokenReserve).div(ethReserve);
                ethAmount = tokenAmount.mul(ethReserve).div(tokenReserve).sub(1);
            }
            liquidityCreated = ethAmount.mul(totalLiquidity).div(ethReserve);
            require(liquidityCreated >= minLiquidity); // dev: not enough liquidity can be created
        } else {
            require(msg.value > 1000000000); // dev: initial eth below 1 gwei
            liquidityCreated = address(this).balance;
        }

        _createUnowned(tokenAmount);
        _increaseLiquidity(recipient, liquidityCreated);

        // refund excess ether
        if (msg.value > ethAmount) {
            msg.sender.transfer(msg.value - ethAmount);
        }
        emit AddLiquidity(recipient, ethAmount, tokenAmount);
        return (tokenAmount, ethAmount, liquidityCreated);
    }

    /// @notice Mint Liquid Gas Tokens and add them to the Liquidity Pool.
    ///         The amount of tokens minted and added to the pool is calculated
    ///         from the amount of ether sent and `maxTokens`.
    ///         The liquidity shares are created for the `sender`.
    ///         Emits an {AddLiquidity} event.
    /// @dev This is much more efficient than minting tokens and adding them
    ///      to the liquidity pool in two separate steps.
    ///      Excess ether that is not added to the pool will be refunded.
    /// @param maxTokens The maximum amount of tokens that will be minted.
    ///         Set this to cap the gas the transaction will use.
    ///         If more than maxTokens could be created, the remaining ether is refunded.
    /// @param minLiquidity The minimum amount of liquidity shares to create,
    ///         will revert if not enough liquidity can be created.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return Tokens minted, Ether added to the pool, Liquidity shares created
    function mintToLiquidity(
        uint256 maxTokens,
        uint256 minLiquidity,
        uint256 deadline
    )
        external
        payable
        returns (uint256, uint256, uint256)
    {
        return _mintToLiquidityFor(maxTokens, minLiquidity, deadline, msg.sender);
    }

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
    /// @return Tokens minted, Ether added to the pool, Liquidity shares created
    function mintToLiquidityFor(
        uint256 maxTokens,
        uint256 minLiquidity,
        uint256 deadline,
        address payable recipient
    )
        external
        payable
        returns (uint256, uint256, uint256)
    {
        require(recipient != address(this)); // dev: can't create for liquid token contract
        require(recipient != address(0)); // dev: can't create for zero address
        return _mintToLiquidityFor(maxTokens, minLiquidity, deadline, recipient);
    }

    // *** Mint to sell

    function _mintToSellTo(
        uint256 mintAmount,
        uint256 minEth,
        uint256 deadline,
        address payable recipient
    )
        internal
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(mintAmount > 0); // dev: must sell one or more tokens
        uint256 ethBought = getInputPrice(mintAmount, tokenReserve(), address(this).balance);
        require(ethBought >= minEth); // dev: tokens not worth enough
        _createUnowned(mintAmount);
        recipient.transfer(ethBought);
        return ethBought;
    }

    /// @notice Mint Liquid Gas Tokens and immediately sell them for ether.
    /// @dev This is much more efficient than minting tokens and then selling them
    ///      in two separate steps.
    /// @param tokenAmount The amount of tokens to mint and sell.
    /// @param minEth The minimum amount of ether to receive for the transaction.
    ///         Will revert if the tokens don't sell for enough ether;
    ///         The gas for minting is not used.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of ether received from the sale.
    function mintToSell(
        uint256 tokenAmount,
        uint256 minEth,
        uint256 deadline
    )
        external
        returns (uint256)
    {
        return _mintToSellTo(tokenAmount, minEth, deadline, msg.sender);
    }

    /// @notice Mint Liquid Gas Tokens, immediately sell them for ether and
    ///         transfer the ether to the `recipient`.
    /// @dev This is much more efficient than minting tokens and then selling them
    ///      in two separate steps.
    ///      Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @param tokenAmount The amount of tokens to mint and sell.
    /// @param minEth The minimum amount of ether to receive for the transaction.
    ///         Will revert if the tokens don't sell for enough ether;
    ///         The gas for minting is not used.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of ether received from the sale.
    function mintToSellTo(
        uint256 tokenAmount,
        uint256 minEth,
        uint256 deadline,
        address payable recipient
    )
        external
        returns (uint256)
    {
        require(recipient != address(this)); // dev: can't send to liquid token contract
        require(recipient != address(0)); // dev: can't send to zero address
        return _mintToSellTo(tokenAmount, minEth, deadline, recipient);
    }

    // ***** Gas Token Freeing
    //       -----------------
    //       Different ways to free Gas Tokens


    // *** Free owned tokens

    /// @notice Free `tokenAmount` of Liquid Gas Tokens from the `sender`'s balance.
    /// @param tokenAmount The amount of tokens to free
    /// @return True if `tokenAmount` tokens could be freed, False otherwise.
    function free(uint256 tokenAmount) external returns (bool) {
        if (tokenAmount > balanceOf(msg.sender)) {
            return false;
        }
        _destroyContracts(tokenAmount);
        _burn(msg.sender, tokenAmount);
        return true;
    }

    /// @notice Free `tokenAmount` of Liquid Gas Tokens from the `owners`'s balance.
    /// @param tokenAmount The amount of tokens to free
    /// @param owner The `owner` of the tokens. The `sender` must have an allowance.
    /// @return True if `tokenAmount` tokens could be freed, False otherwise.
    function freeFrom(uint256 tokenAmount, address owner) external returns (bool) {
        if(tokenAmount > allowance(owner, msg.sender)) {
            return false;
        }
        if (tokenAmount > balanceOf(owner)) {
            return false;
        }
        _destroyContracts(tokenAmount);
        _burnFrom(owner, tokenAmount);
        return true;
    }

    // *** Free from liquidity pool

    /// @dev Free tokens directly to the liquidity pool
    function _freeUnowned(uint256 tokenAmount) internal returns (bool) {
        _destroyContracts(tokenAmount);
        _burn_unowned(tokenAmount);
        return true;
    }

    /// @notice Buy `tokenAmount` tokens from the liquidity pool and immediately free them.
    /// @param tokenAmount The amount of tokens to buy and free.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param refundTo Any excess ether will be refunded to this address.
    /// @dev This will not revert unless an unexpected error occurs. Instead it will return 0.
    /// @return The amount of ether spent to buy `tokenAmount` tokens.
    function buyAndFree(
        uint256 tokenAmount,
        uint256 deadline,
        address payable refundTo
    )
        external
        payable
        returns (uint256)
    {
        if (deadline <= now || tokenAmount <= 0) {
            return 0;
        }
        uint256 tokenReserve = tokenReserve();
        if (tokenReserve < tokenAmount) {
            return 0;
        }
        uint256 ethReserve = address(this).balance.sub(msg.value);
        uint256 ethSold = getOutputPrice(tokenAmount, ethReserve, tokenReserve);
        if (msg.value < ethSold) {
            return 0;
        }
        uint256 ethRefund = msg.value - ethSold;
        _freeUnowned(tokenAmount);
        if (ethRefund > 0) {
            refundTo.transfer(ethRefund);
        }
        return ethSold;
    }

    /// @notice Buy up to `maxTokens` tokens from the liquidity pool and immediately free them.
    ///         Will buy less than `maxTokens` if not enough ether is provided.
    ///         Excess ether is not refunded!
    /// @param maxTokens The maximum amount of tokens to buy and free with the sent ether.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev This will not revert unless an unexpected error occurs. Instead it will return 0.
    /// @return The amount of tokens bought and freed.
    function buyUpToAndFree(uint256 maxTokens, uint256 deadline)
        public
        payable
        returns (uint256)
    {
        if (deadline <= now || maxTokens <= 0) {
            return 0;
        }
        uint256 ethReserve = address(this).balance.sub(msg.value);
        uint256 tokensBought = getInputPrice(msg.value, ethReserve, tokenReserve());
        if (tokensBought <= 0) {
            return 0;
        } else if (tokensBought > maxTokens) {
            tokensBought = maxTokens;
        }
        _freeUnowned(tokensBought);
        return tokensBought;
    }
}
