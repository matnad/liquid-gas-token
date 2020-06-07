import pytest
from brownie import *

"""
These tests don't verify if gas is refunded, only if tokens are bought and burned.
Refund verification is done with integration tests.
"""

DEADLINE = 99999999999


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.addLiquidity(1, 20, DEADLINE, {'from': accounts[0], 'value': "0.019 ether"})
    yield lgt


def test_buy_and_free(liquid_lgt, accounts):
    initial_supply = liquid_lgt.totalSupply()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(5)
    tx = liquid_lgt.buyAndFree(5, DEADLINE, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == expected_price
    assert liquid_lgt.totalSupply() == initial_supply - 5


def test_deadline_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(5, 1, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_exceed_reserve_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(50, DEADLINE, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_not_enough_eth_sent_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(10)
    assert expected_price > "0.01 ether"
    tx = liquid_lgt.buyAndFree(10, DEADLINE, accounts[1], {'from': accounts[1], 'value': "0.01 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_no_eth_sent_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(10, DEADLINE, accounts[1], {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_buy_up_to_and_free(liquid_lgt, accounts):
    expected_tokens = liquid_lgt.getEthToTokenInputPrice(Wei("0.05 ether"))
    assert expected_tokens < 50
    tx = liquid_lgt.buyUpToAndFree(50, DEADLINE, {'from': accounts[1], 'value': "0.05 ether"})
    assert tx.return_value == expected_tokens


def test_up_to_deadline_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyUpToAndFree(5, 1, {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_up_to_no_eth_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyUpToAndFree(10, DEADLINE, {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
