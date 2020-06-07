import pytest
from brownie import *
import brownie


DEADLINE = 9999999999999

@pytest.fixture()
def liquid_lgt(lgt, accounts):
    lgt.addLiquidity(1, 21, 99999999999, {'from': accounts[0], 'value': "0.02 ether"})
    yield lgt


def test_remove_liquidity_liq_constraint(liquid_lgt, accounts):
    initial_balance = accounts[0].balance()
    tx = liquid_lgt.removeLiquidity("0.01 ether", "0.005 ether", 1, DEADLINE, {'from': accounts[0]})
    # should withdraw 0.1 ether and 10 tokens
    assert tx.return_value == (Wei("0.01 ether"), 10)
    event = tx.events['RemoveLiquidity']
    assert event["provider"] == accounts[0]
    assert event["eth_amount"] == "0.01 ether"
    assert event["token_amount"] == 10
    assert liquid_lgt.balanceOf(accounts[0]) == 30 - 21 + 10
    assert accounts[0].balance() == initial_balance + "0.01 ether"


def test_remove_liquidity_exact(liquid_lgt, accounts):
    initial_balance = accounts[0].balance()
    tx = liquid_lgt.removeLiquidity("0.015 ether", "0.015 ether", 15, DEADLINE, {'from': accounts[0]})
    # should withdraw 0.015 ether and 15 tokens
    assert tx.return_value == (Wei("0.015 ether"), 15)
    assert liquid_lgt.balanceOf(accounts[0]) == 30 - 21 + 15
    assert accounts[0].balance() == initial_balance + "0.015 ether"


def test_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.removeLiquidity("0.01 ether", "0.005 ether", 1, 1, {'from': accounts[0]})


def test_no_min_shares_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: amount of liquidity to remove must be positive"):
        liquid_lgt.removeLiquidity("0 ether", "0.005 ether", 1, DEADLINE, {'from': accounts[0]})


def test_no_min_eth_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must remove positive eth amount"):
        liquid_lgt.removeLiquidity("0.01 ether", "0 ether", 1, DEADLINE, {'from': accounts[0]})


def test_no_min_tokens_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must remove positive token amount"):
        liquid_lgt.removeLiquidity("0.01 ether", "0.005 ether", 0, DEADLINE, {'from': accounts[0]})


def test_exceed_eth_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: can't remove enough eth"):
        liquid_lgt.removeLiquidity("0.01 ether", "0.015 ether", 1, DEADLINE, {'from': accounts[0]})


def test_exceed_tokens_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: can't remove enough tokens"):
        liquid_lgt.removeLiquidity("0.01 ether", "0.005 ether", 20, DEADLINE, {'from': accounts[0]})


def test_too_many_shares_reverts(liquid_lgt, accounts):
    """ Trying to remove more shares than owned. """
    with brownie.reverts("SafeMath: subtraction overflow"):
        liquid_lgt.removeLiquidity("0.6 ether", "0.005 ether", 1, DEADLINE, {'from': accounts[0]})
