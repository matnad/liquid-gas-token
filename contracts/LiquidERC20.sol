pragma solidity ^0.6.7;

import "./ERC20PointerSupply.sol";

/// @title ERC20-Token with built in Liquidity Pool
/// @dev The Liquidity Shares do not adhere to ERC20 standards,
///      only the underlying token does. Liquidity can not be traded.
/// @author Matthias Nadler
contract LiquidERC20 is ERC20PointerSupply {

    // ***** Liquidity Pool
    //       --------------
    //       Integrated Liquidity Pool for an ERC20 Token.
    //       More efficient due to shortcuts in the ownership transfers.
    //       Modelled after Uniswap V1 by Hayden Adams:
    //       https://github.com/Uniswap/uniswap-v1/blob/master/contracts/uniswap_exchange.vy

    uint256 internal _poolTotalSupply;
    mapping (address => uint256) internal _poolBalances;

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

    /// @notice Returns the amount of liquidity shares owned by `account`.
    /// @param account The account to query for the balance.
    /// @return The amount of liquidity shares owned by `account`.
    function poolBalanceOf(address account) external view returns (uint256) {
        return _poolBalances[account];
    }

    /// @notice Return the total supply of liquidity shares.
    /// @return Total number of liquidity shares.
    function poolTotalSupply() external view returns (uint256) {
        return _poolTotalSupply;
    }

    /// @notice The amount of tokens in the liquidity pool.
    /// @dev This is defined implicitly as the difference between
    ///      The total supply and the privately owned supply of the token.
    /// @return The amount of tokens in the liquidity pool.
    function poolTokenReserves() external view returns (uint256) {
        return _totalMinted.sub(_totalBurned + _ownedSupply);
    }

    // *** Constructor
    /// @dev start with initial liquidity. Contract must be pre-funded.
    constructor() public {
        // Implementation must mint at least 1 token to the pool during deployment.
        uint ethReserve = address(this).balance;
        require(ethReserve > 1000000000);
        _poolTotalSupply += ethReserve;
        _poolBalances[msg.sender] += ethReserve;
    }

    /// @notice Add liquidity to the pool and receive liquidity shares. Must deposit
    ///         an equal amount of ether and tokens at the current exchange rate.
    ///         Emits an {AddLiquidity} event.
    /// @param minLiquidity The minimum amount of liquidity shares to create,
    ///        will revert if not enough liquidity can be created.
    /// @param maxTokens The maximum amount of tokens to transfer to match the provided
    ///        ether liquidity. Will revert if too many tokens are needed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev Requirements:
    ///      - The initial liquidity must be greater than 1 gwei.
    /// @return The amount of liquidity shares created.
    function addLiquidity(uint256 minLiquidity, uint256 maxTokens, uint256 deadline)
        external
        payable
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(maxTokens != 0); // dev: no tokens to add
        require(msg.value != 0); // dev: no ether to add
        require(minLiquidity != 0); // dev: no min_liquidity specified

        uint256 ethReserve = address(this).balance - msg.value;
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 tokenAmount = msg.value.mul(tokenReserve) / ethReserve + 1;
        uint256 poolTotalSupply = _poolTotalSupply;
        uint256 liquidityCreated = msg.value.mul(poolTotalSupply) / ethReserve;
        require(maxTokens >= tokenAmount); // dev: need more tokens
        require(liquidityCreated >= minLiquidity); // dev: not enough liquidity can be created

        // create liquidity shares
        _poolTotalSupply = poolTotalSupply + liquidityCreated;
        _poolBalances[msg.sender] += liquidityCreated;

        // remove LGTs from sender
        _balances[msg.sender] = _balances[msg.sender].sub(
            tokenAmount, "LGT: amount exceeds balance"
        );
        _ownedSupply = ownedSupply.sub(tokenAmount);

        emit AddLiquidity(msg.sender, msg.value, tokenAmount);
        return liquidityCreated;
    }


    /// @notice Remove liquidity shares and receive an equal amount of tokens and ether
    ///         at the current exchange rate from the liquidity pool.
    ///         Emits a {RemoveLiquidity} event.
    /// @param amount The amount of liquidity shares to remove from the pool.
    /// @param minEth The minimum amount of ether you want to receive in the transaction.
    ///        Will revert if less than `minEth` ether would be transferred.
    /// @param minTokens The minimum amount of tokens you want to receive in the transaction.
    ///        Will revert if less than `minTokens` tokens would be transferred.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev Requirements:
    ///      - `sender` must have a liquidity pool balance of at least `amount`.
    /// @return The amount of ether and tokens refunded.
    function removeLiquidity(uint256 amount, uint256 minEth, uint256 minTokens, uint256 deadline)
        external
        returns (uint256, uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(amount != 0); // dev: amount of liquidity to remove must be positive
        require(minEth != 0); // dev: must remove positive eth amount
        require(minTokens != 0); // dev: must remove positive token amount
        uint256 totalLiquidity = _poolTotalSupply;
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 ethAmount = amount.mul(address(this).balance) / totalLiquidity;
        uint256 tokenAmount = amount.mul(tokenReserve) / totalLiquidity;
        require(ethAmount >= minEth); // dev: can't remove enough eth
        require(tokenAmount >= minTokens); // dev: can't remove enough tokens

        // Remove liquidity shares
        _poolBalances[msg.sender] = _poolBalances[msg.sender].sub(amount);
        _poolTotalSupply = totalLiquidity.sub(amount);

        // Refund LGTs
        _balances[msg.sender] += tokenAmount;
        _ownedSupply = ownedSupply + tokenAmount;

        emit RemoveLiquidity(msg.sender, ethAmount, tokenAmount);

        // Refund ETH
        msg.sender.transfer(ethAmount);
        return (ethAmount, tokenAmount);
    }

    // ***** Constant Price Model
    //       --------------------
    //       Internal price calculation functions for the constant price model with fees.


    /// @dev token reserve and pool balance are guaranteed to be non-zero
    ///      No need to require inputReserve != 0
    function getInputPrice(uint256 inputAmount, uint256 inputReserve, uint256 outputReserve)
        internal
        pure
        returns (uint256)
    {
        uint256 inputAmountWithFee = inputAmount.mul(995);
        uint256 numerator = inputAmountWithFee.mul(outputReserve);
        uint256 denominator = inputReserve.mul(1000).add(inputAmountWithFee);
        return numerator / denominator;
    }

    /// @dev Requirements:
    ///      - `OutputAmount` must be greater than `OutputReserve`
    ///      Token reserve and pool balance are guaranteed to be non-zero
    ///      No need to require inputReserve != 0 or outputReserve != 0
    function getOutputPrice(uint256 outputAmount, uint256 inputReserve, uint256 outputReserve)
        internal
        pure
        returns (uint256)
    {
        uint256 numerator = inputReserve.mul(outputAmount).mul(1000);
        uint256 denominator = outputReserve.sub(outputAmount).mul(995);
        return (numerator / denominator).add(1);
    }

    // ***** Trade Ether to Tokens
    //       -------------------

    /// @dev Exact amount of ether -> As many tokens as can be bought, without partial refund
    function ethToTokenInput(
        uint256 ethSold,
        uint256 minTokens,
        uint256 deadline,
        address recipient
    )
        internal
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(ethSold != 0); // dev: no eth to sell
        require(minTokens != 0); // dev: must buy one or more tokens
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 ethReserve = address(this).balance.sub(ethSold);
        uint256 tokensBought = getInputPrice(ethSold, ethReserve, tokenReserve);
        require(tokensBought >= minTokens); // dev: not enough eth to buy tokens
        _balances[recipient] += tokensBought;
        _ownedSupply = ownedSupply + tokensBought;
        return tokensBought;
    }

    /// @notice Convert ETH to Tokens
    /// @dev User cannot specify minimum output or deadline.
    receive() external payable {
        ethToTokenInput(msg.value, 1, now, msg.sender);
    }

    /// @notice Convert ether to tokens. Specify the exact input (in ether) and
    ///         the minimum output (in tokens).
    /// @param minTokens The minimum amount of tokens you want to receive in the
    ///        transaction for your sold ether. Will revert if less than `minTokens`
    ///        tokens would be transferred.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev Excess ether for buying a partial token is not refunded.
    /// @return The amount of tokens bought.
    function ethToTokenSwapInput(uint256 minTokens, uint256 deadline)
        external
        payable
        returns (uint256)
    {
        return ethToTokenInput(msg.value, minTokens, deadline, msg.sender);
    }

    /// @notice Convert ether to tokens and transfer tokens to `recipient`.
    ///         Specify the exact input (in ether) and the minimum output (in tokens).
    /// @param minTokens The minimum amount of tokens you want the `recipient` to
    ///        receive in the transaction for your sold ether.
    ///        Will revert if less than `minTokens` tokens would be transferred.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param recipient Bought tokens will be transferred to this address.
    /// @dev Excess ether for buying a partial token is not refunded.
    ///      Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @return The amount of tokens bought and transferred to `recipient`.
    function ethToTokenTransferInput(uint256 minTokens, uint256 deadline, address recipient)
        external
        payable
        returns (uint256)
    {
        require(recipient != address(this)); // dev: can't send to liquid token contract
        require(recipient != address(0)); // dev: can't send to zero address
        return ethToTokenInput(msg.value, minTokens, deadline, recipient);
    }


    /// @dev Any amount of ether (at least cost of tokens) -> Exact amount of tokens + refund
    function ethToTokenOutput(
        uint256 tokensBought,
        uint256 maxEth,
        uint256 deadline,
        address payable buyer,
        address recipient
    )
        internal
        returns (uint256)
    {
        require(deadline >= now); // dev: deadline passed
        require(tokensBought != 0); // dev: must buy one or more tokens
        require(maxEth != 0); // dev: maxEth must greater than 0
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 ethReserve = address(this).balance.sub(maxEth);
        uint256 ethSold = getOutputPrice(tokensBought, ethReserve, tokenReserve);
        uint256 ethRefund = maxEth.sub(ethSold, "LGT: not enough ETH");
        _balances[recipient] += tokensBought;
        _ownedSupply = ownedSupply + tokensBought;
        if (ethRefund != 0) {
            buyer.transfer(ethRefund);
        }
        return ethSold;
    }

    /// @notice Convert ether to tokens. Specify the maximum input (in ether) and
    ///         the exact output (in tokens). Any remaining ether is refunded.
    /// @param tokensBought The exact amount of tokens you want to receive.
    ///        Will revert if less than `tokensBought` tokens can be bought
    ///        with the sent amount of ether.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @dev Excess ether after buying `tokensBought` tokens is refunded.
    /// @return The amount of ether sold to buy `tokensBought` tokens.
    function ethToTokenSwapOutput(uint256 tokensBought, uint256 deadline)
        external
        payable
        returns (uint256)
    {
        return ethToTokenOutput(tokensBought, msg.value, deadline, msg.sender, msg.sender);
    }

    /// @notice Convert ether to tokens and transfer tokens to `recipient`.
    ///         Specify the maximum input (in ether) and the exact output (in tokens).
    ///         Any remaining ether is refunded.
    /// @param tokensBought The exact amount of tokens you want to buy and transfer to
    ///        `recipient`. Will revert if less than `tokensBought` tokens can be bought
    ///        with the sent amount of ether.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param recipient Bought tokens will be transferred to this address.
    /// @dev Excess ether for buying a partial token is not refunded.
    ///      Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @return The amount of ether sold to buy `tokensBought` tokens.
    function ethToTokenTransferOutput(uint256 tokensBought, uint256 deadline, address recipient)
        external
        payable
        returns (uint256)
    {
        require(recipient != address(this)); // dev: can't send to liquid token contract
        require(recipient != address(0)); // dev: can't send to zero address
        return ethToTokenOutput(tokensBought, msg.value, deadline, msg.sender, recipient);
    }


    // ***** Trade Tokens to Ether
    //       ---------------------

    /// @dev Exact amount of tokens -> Minimum amount of ether
    function tokenToEthInput(
        uint256 tokensSold,
        uint256 minEth,
        uint256 deadline,
        address buyer,
        address payable recipient
    ) internal returns (uint256) {
        require(deadline >= now); // dev: deadline passed
        require(tokensSold != 0); // dev: must sell one or more tokens
        require(minEth != 0); // dev: minEth not set
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 ethBought = getInputPrice(tokensSold, tokenReserve, address(this).balance);
        require(ethBought >= minEth); // dev: tokens not worth enough
        _balances[buyer] = _balances[buyer].sub(tokensSold, "LGT: amount exceeds balance");
        _ownedSupply = ownedSupply.sub(tokensSold);
        recipient.transfer(ethBought);
        return ethBought;
    }

    /// @notice Convert tokens to ether. Specify the exact input (in tokens) and
    ///         the minimum output (in ether).
    /// @param tokensSold The exact amount of tokens you want to sell in the
    ///        transaction. Will revert you own less than `minTokens` tokens.
    /// @param minEth The minimum amount of ether you want to receive for the sale
    ///        of `tokensSold` tokens. Will revert if less ether would be received.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of ether bought.
    function tokenToEthSwapInput(uint256 tokensSold, uint256 minEth, uint256 deadline)
        external
        returns (uint256)
    {
        return tokenToEthInput(tokensSold, minEth, deadline, msg.sender, msg.sender);
    }

    /// @notice Convert tokens to ether and transfer it to `recipient`.
    ///         Specify the exact input (in tokens) and the minimum output (in ether).
    /// @param tokensSold The exact amount of tokens you want to sell in the
    ///        transaction. Will revert you own less than `minTokens` tokens.
    /// @param minEth The minimum amount of ether you want the `recipient` to receive for
    ///        the sale of `tokensSold` tokens. Will revert if less ether would be transferred.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param recipient Bought ether will be transferred to this address.
    /// @dev Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @return The amount of ether bought.
    function tokenToEthTransferInput(
        uint256 tokensSold,
        uint256 minEth,
        uint256 deadline,
        address payable recipient
    ) external returns (uint256) {
        require(recipient != address(this)); // dev: can't send to liquid token contract
        require(recipient != address(0)); // dev: can't send to zero address
        return tokenToEthInput(tokensSold, minEth, deadline, msg.sender, recipient);
    }


    /// @dev Maximum amount of tokens -> Exact amount of ether
    function tokenToEthOutput(
        uint256 ethBought,
        uint256 maxTokens,
        uint256 deadline,
        address buyer,
        address payable recipient
    ) internal returns (uint256) {
        require(deadline >= now); // dev: deadline passed
        require(ethBought != 0); // dev: must buy more than 0 eth
        uint256 ownedSupply = _ownedSupply;
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + ownedSupply);
        uint256 tokensSold = getOutputPrice(ethBought, tokenReserve, address(this).balance);
        require(maxTokens >= tokensSold); // dev: need more tokens to sell
        _balances[buyer] = _balances[buyer].sub(tokensSold, "LGT: amount exceeds balance");
        _ownedSupply = ownedSupply.sub(tokensSold);
        recipient.transfer(ethBought);
        return tokensSold;
    }

    /// @notice Convert tokens to ether. Specify the maximum input (in tokens) and
    ///         the exact output (in ether).
    /// @param ethBought The exact amount of ether you want to receive in the
    ///        transaction. Will revert if tokens can't be sold for enough ether.
    /// @param maxTokens The maximum amount of tokens you are willing to sell to
    ///        receive `ethBought` ether. Will revert if more tokens would be needed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @return The amount of tokens sold.
    function tokenToEthSwapOutput(uint256 ethBought, uint256 maxTokens, uint256 deadline)
        external
        returns (uint256)
    {
        return tokenToEthOutput(ethBought, maxTokens, deadline, msg.sender, msg.sender);
    }

    /// @notice Convert tokens to ether and transfer it to `recipient`.
    ///         Specify the maximum input (in tokens) and the exact output (in ether).
    /// @param ethBought The exact amount of ether you want `recipient` to receive in the
    ///        transaction. Will revert if tokens can't be sold for enough ether.
    /// @param maxTokens The maximum amount of tokens you are willing to sell to
    ///        buy `ethBought` ether. Will revert if more tokens would be needed.
    /// @param deadline The time after which the transaction can no longer be executed.
    ///        Will revert if the current timestamp is after the deadline.
    /// @param recipient Bought ether will be transferred to this address.
    /// @dev Requirements:
    ///      - `recipient` can't be this contract or the zero address
    /// @return The amount of tokens sold.
    function tokenToEthTransferOutput(
        uint256 ethBought,
        uint256 maxTokens,
        uint256 deadline,
        address payable recipient
    )
        external
        returns (uint256)
    {
        require(recipient != address(this)); // dev: can't send to liquid token contract
        require(recipient != address(0)); // dev: can't send to zero address
        return tokenToEthOutput(ethBought, maxTokens, deadline, msg.sender, recipient);
    }

    // ***** Public Price Functions
    //       --------------------

    /// @notice How many tokens can I buy with `ethSold` ether?
    /// @param ethSold The exact amount of ether you are selling.
    /// @return The amount of tokens that can be bought with `ethSold` ether.
    function getEthToTokenInputPrice(uint256 ethSold) public view returns(uint256) {
        require(ethSold != 0); // dev: no eth to sell
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + _ownedSupply);
        return getInputPrice(ethSold, address(this).balance, tokenReserve);
    }

    /// @notice What is the price for `tokensBought` tokens?
    /// @param tokensBought The exact amount of tokens bought
    /// @return The amount of ether needed to buy `tokensBought` tokens
    function getEthToTokenOutputPrice(uint256 tokensBought) public view returns (uint256) {
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + _ownedSupply);
        return getOutputPrice(tokensBought, address(this).balance, tokenReserve);
    }

    /// @notice How much ether do I receive when selling `tokensSold` tokens?
    /// @param tokensSold The exact amount of tokens you are selling.
    /// @return The amount of ether you receive for selling `tokensSold` tokens.
    function getTokenToEthInputPrice(uint256 tokensSold) public view returns (uint256) {
        require(tokensSold != 0); // dev: can't sell less than one token
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + _ownedSupply);
        return getInputPrice(tokensSold, tokenReserve, address(this).balance);
    }

    /// @notice How many tokens do I need to sell to receive `ethBought` ether?
    /// @param ethBought The exact amount of ether you are buying.
    /// @return The amount of tokens needed to buy `ethBought` ether.
    function getTokenToEthOutputPrice(uint256 ethBought) public view returns (uint256) {
        uint256 tokenReserve = _totalMinted.sub(_totalBurned + _ownedSupply);
        return getOutputPrice(ethBought, tokenReserve, address(this).balance);
    }
}
