import pytest
from brownie import *
import brownie


@pytest.fixture()
def liquid_lgt(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    yield lgt


def test_remove_liquidity_liq_constraint(liquid_lgt, accounts):
    balance = accounts[0].balance()
    tx = liquid_lgt.removeLiquidity("0.2 ether", "0.1 ether", 1, 9999999999999, {'from': accounts[0]})
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
    assert liquid_lgt.balanceOf(accounts[0]) == 20 + 4
    assert liquid_lgt.ownedSupply() == 24
    assert liquid_lgt.totalSupply() == 30
    assert accounts[0].balance() == balance + "0.2 ether"


def test_remove_liquidity_exact(liquid_lgt, accounts):
    balance = accounts[0].balance()
    tx = liquid_lgt.removeLiquidity("0.3 ether", "0.3 ether", 4, 9999999999999, {'from': accounts[0]})
    # uint256 totalLiquidity = _poolTotalSupply; 0.5 ether
    # uint256 tokenReserve = totalSupply() - ownedSupply(); 10
    # uint256 ethAmount = amount.mul(address(this).balance).div(totalLiquidity); 0.3 * 0.5 / 0.5 = 0.3
    # uint256 tokenAmount = amount.mul(tokenReserve).div(totalLiquidity); 0.3 * 10 / 0.5 = 6
    # should withdraw 0.3 ether and 6 tokens
    assert tx.return_value == (Wei("0.3 ether"), 6)
    assert liquid_lgt.balanceOf(accounts[0]) == 20 + 6
    assert accounts[0].balance() == balance + "0.3 ether"


def test_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.removeLiquidity("0.3 ether", "0.1 ether", 4, 1, {'from': accounts[0]})


def test_no_min_shares_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: amount of liquidity to remove must be positive"):
        liquid_lgt.removeLiquidity("0 ether", "0.1 ether", 4, 99999999999, {'from': accounts[0]})


def test_no_min_eth_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must remove positive eth amount"):
        liquid_lgt.removeLiquidity("0.3 ether", "0 ether", 4, 99999999999, {'from': accounts[0]})


def test_no_min_tokens_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must remove positive token amount"):
        liquid_lgt.removeLiquidity("0.3 ether", "0.1 ether", 0, 99999999999, {'from': accounts[0]})


def test_exceed_eth_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: can't remove enough eth"):
        liquid_lgt.removeLiquidity("0.3 ether", "0.5 ether", 4, 99999999999, {'from': accounts[0]})


def test_exceed_tokens_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: can't remove enough tokens"):
        liquid_lgt.removeLiquidity("0.3 ether", "0.1 ether", 9, 99999999999, {'from': accounts[0]})


def test_too_many_shares_reverts(liquid_lgt, accounts):
    """ Trying to remove more shares than owned. """
    with brownie.reverts("SafeMath: subtraction overflow"):
        liquid_lgt.removeLiquidity("0.6 ether", "0.1 ether", 9, 99999999999, {'from': accounts[0]})
