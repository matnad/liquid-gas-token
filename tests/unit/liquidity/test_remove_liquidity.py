import pytest
from brownie import *
import brownie


@pytest.fixture()
def liquidLgt(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    yield lgt


def test_remove_liquidity_liq_constraint(liquidLgt, accounts):
    balance = accounts[0].balance()
    tx = liquidLgt.removeLiquidity("0.2 ether", "0.1 ether", 1, 9999999999999, {'from': accounts[0]})
    # uint256 totalLiquidity = _poolTotalSupply; 0.5 ether
    # uint256 tokenReserve = totalSupply() - ownedSupply(); 10
    # uint256 ethAmount = amount.mul(address(this).balance).div(totalLiquidity); 0.2 * 0.5 / 0.5 = 0.2
    # uint256 tokenAmount = amount.mul(tokenReserve).div(totalLiquidity); 0.2 * 10 / 0.5 = 4
    # should withdraw 0.2 ether and 4 tokens
    assert tx.return_value == (Wei("0.2 ether"), 4)
    event = tx.events['RemoveLiquidity']
    assert event["provider"] == accounts[0]
    assert event["eth_amount"] == "0.2 ether"
    assert event["token_amount"] == 4
    assert liquidLgt.balanceOf(accounts[0]) == 20 + 4
    assert liquidLgt.ownedSupply() == 24
    assert liquidLgt.totalSupply() == 30
    assert accounts[0].balance() == balance + "0.2 ether"


def test_remove_liquidity_exact(liquidLgt, accounts):
    balance = accounts[0].balance()
    tx = liquidLgt.removeLiquidity("0.3 ether", "0.3 ether", 4, 9999999999999, {'from': accounts[0]})
    # uint256 totalLiquidity = _poolTotalSupply; 0.5 ether
    # uint256 tokenReserve = totalSupply() - ownedSupply(); 10
    # uint256 ethAmount = amount.mul(address(this).balance).div(totalLiquidity); 0.3 * 0.5 / 0.5 = 0.3
    # uint256 tokenAmount = amount.mul(tokenReserve).div(totalLiquidity); 0.3 * 10 / 0.5 = 6
    # should withdraw 0.3 ether and 6 tokens
    assert tx.return_value == (Wei("0.3 ether"), 6)
    assert liquidLgt.balanceOf(accounts[0]) == 20 + 6
    assert accounts[0].balance() == balance + "0.3 ether"


def test_remove_liquidity_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.removeLiquidity("0.3 ether", "0.1 ether", 4, 1, {'from': accounts[0]})
    with brownie.reverts("dev: amount of liquidity to remove must be positive"):
        liquidLgt.removeLiquidity("0 ether", "0.1 ether", 4, 99999999999, {'from': accounts[0]})
    with brownie.reverts("dev: must remove positive eth amount"):
        liquidLgt.removeLiquidity("0.3 ether", "0 ether", 4, 99999999999, {'from': accounts[0]})
    with brownie.reverts("dev: must remove positive token amount"):
        liquidLgt.removeLiquidity("0.3 ether", "0.1 ether", 0, 99999999999, {'from': accounts[0]})
    with brownie.reverts("dev: can't remove enough eth"):
        liquidLgt.removeLiquidity("0.3 ether", "0.5 ether", 4, 99999999999, {'from': accounts[0]})
    with brownie.reverts("dev: can't remove enough tokens"):
        liquidLgt.removeLiquidity("0.3 ether", "0.1 ether", 9, 99999999999, {'from': accounts[0]})
    with brownie.reverts("SafeMath: subtraction overflow"):
        # not enough liquidity balance
        liquidLgt.removeLiquidity("0.6 ether", "0.1 ether", 9, 99999999999, {'from': accounts[0]})
