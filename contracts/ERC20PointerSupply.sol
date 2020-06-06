pragma solidity ^0.6.7;

import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.1/contracts/token/ERC20/IERC20.sol";


/// @title ERC20-Token where total supply is calculated from minted and burned tokens
/// @author Matthias Nadler
contract ERC20PointerSupply is IERC20 {
    using SafeMath for uint256;

    // ****** ERC20 Pointer Supply Token
    //        --------------------------

    mapping (address => uint256) internal _balances;
    mapping (address => mapping (address => uint256)) internal _allowances;

    uint256 internal _ownedSupply;
    uint256 internal _totalBurned;
    uint256 internal _totalMinted;

    string constant public name = "Liquid Gas Token";
    string constant public symbol = "LGT";
    uint8 constant public decimals = 0;

    /// @notice Return the total supply of tokens.
    /// @dev This is different from a classic ERC20 implementation as the supply is calculated
    ///      from the burned and minted tokens instead of stored in its own variable.
    /// @return Total number of tokens in circulation.
    function totalSupply() public view override returns (uint256) {
        return _totalMinted.sub(_totalBurned);
    }

    /// @notice Return the number of tokens owned by specific addresses.
    /// @dev Unowned tokens belong to this contract and their supply can be
    ///      calculated implicitly. This means we need to manually track owned tokens,
    ///      but it makes operations on unowned tokens much cheaper.
    ///      TotalSupply() = ownedSupply() + unownedSupply().
    /// @return Total number of tokens owned by specific addresses.
    function ownedSupply() public view returns (uint256) {
        return _ownedSupply;
    }

    /// @notice Returns the amount of tokens owned by `account`.
    /// @param account The account to query for the balance.
    /// @return The amount of tokens owned by `account`.
    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    /// @notice Moves `amount` tokens from the caller's account to `recipient`.
    ///         Emits a {Transfer} event.
    /// @dev Requirements:
    //       - `recipient` cannot be the zero address.
    //       - the caller must have a balance of at least `amount`.
    /// @param recipient The tokens are transferred to this address.
    /// @param amount The amount of tokens to be transferred.
    /// @return True if the transfer succeeded, False otherwise.
    function transfer(address recipient, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }

    /// @notice Returns the remaining number of tokens that `spender` will be
    ///         allowed to spend on behalf of `owner` through {transferFrom}.
    ///         This is zero by default.
    /// @param owner The address that holds the tokens that can be spent by `spender`.
    /// @param spender The address that is allowed to spend the tokens held by `owner`.
    /// @return Remaining number of tokens that `spender` will be
    ///         allowed to spend on behalf of `owner`
    function allowance(address owner, address spender) public view override returns (uint256) {
        return _allowances[owner][spender];
    }

    /// @notice Sets `amount` as the allowance of `spender` over the caller's tokens.
    ///         Emits an {Approval} event.
    /// @dev    IMPORTANT: Beware that changing an allowance with this method brings the risk
    ///         that someone may use both the old and the new allowance by unfortunate
    ///         transaction ordering. One possible solution to mitigate this race
    ///         condition is to first reduce the spender's allowance to 0 and set the
    ///         desired value afterwards:
    ///         https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    ///         Requirements:
    ///         - `spender` cannot be the zero address.
    /// @param spender The address that is allowed to spend the tokens held by the caller.
    /// @param amount The amount of tokens the `spender` can spend from the caller's supply.
    /// @return True if the approval succeeded, False otherwise.
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }


    /// @notice Moves `amount` tokens from `sender` to `recipient` using the allowance
    ///         mechanism. `amount` is then deducted from the caller's allowance.
    ///         Emits a {Transfer} and an {Approval} event.
    /// @dev Requirements:
    ///      - `sender` and `recipient` cannot be the zero address.
    ///      - `sender` must have a balance of at least `amount`.
    ///      - the caller must have allowance for `sender`'s tokens of at least `amount`.
    /// @param sender The tokens are transferred from this address.
    /// @param recipient The tokens are transferred to this address.
    /// @param amount The amount of tokens to be transferred.
    /// @return True if the transfer succeeded, False otherwise.
    function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool) {
        _transfer(sender, recipient, amount);
        _approve(
            sender,
            msg.sender,
            _allowances[sender][msg.sender].sub(amount, "ERC20: transfer amount exceeds allowance")
        );
        return true;
    }

    /// @notice Atomically increases the allowance granted to `spender` by the caller.
    ///         This is an alternative to {approve} that can be used as a mitigation for
    ///         problems described in {approve}.
    ///         Emits an {Approval} event.
    /// @dev Requirements:
    ///      - `spender` cannot be the zero address.
    /// @param spender The address that is allowed to spend the tokens held by the caller.
    /// @param addedValue The amount of tokens to add to the current `allowance`.
    /// @return True if the approval succeeded, False otherwise.
    function increaseAllowance(address spender, uint256 addedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].add(addedValue));
        return true;
    }

    /// @notice Atomically decreases the allowance granted to `spender` by the caller.
    ///         This is an alternative to {approve} that can be used as a mitigation for
    ///         problems described in {approve}.
    ///         Emits an {Approval} event.
    /// @dev Requirements:
    ///      - `spender` cannot be the zero address.
    ///      - `spender` must have allowance for the caller of at least `subtractedValue`.
    /// @param spender The address that is allowed to spend the tokens held by the caller.
    /// @param subtractedValue The amount of tokens to subtract from the current `allowance`.
    /// @return True if the approval succeeded, False otherwise.
    function decreaseAllowance(address spender, uint256 subtractedValue) public returns (bool) {
        _approve(
            msg.sender,
            spender,
            _allowances[msg.sender][spender].sub(subtractedValue, "ERC20: decreased allowance below zero")
        );
        return true;
    }


    // ****** Internal ERC20 Functions
    //        ------------------------

    function _transfer(address sender, address recipient, uint256 amount) internal virtual {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");

        _balances[sender] = _balances[sender].sub(amount, "ERC20: transfer amount exceeds balance");
        _balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    }

    function _approve(address owner, address spender, uint256 amount) internal virtual {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }
}
