import brownie
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


def test_buy_and_free_zero(liquid_lgt, accounts):
    """ The price for 0 tokens is 1 wei. """
    initial_balance = accounts[1].balance()
    initial_supply = liquid_lgt.totalSupply()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(0)
    tx = liquid_lgt.buyAndFree(0, DEADLINE, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == expected_price
    assert liquid_lgt.totalSupply() == initial_supply
    assert initial_balance == accounts[1].balance() + expected_price


def test_buy_and_free_exact(liquid_lgt, accounts):
    initial_supply = liquid_lgt.totalSupply()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(5)
    tx = liquid_lgt.buyAndFree(5, DEADLINE, accounts[1], {'from': accounts[1], 'value': expected_price})
    assert tx.return_value == expected_price
    assert initial_supply == liquid_lgt.totalSupply() + 5


def test_buy_and_free_opt(liquid_lgt, accounts):
    initial_supply = liquid_lgt.totalSupply()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(1)
    liquid_lgt.buyAndFree22457070633(1, {'from': accounts[1], 'value': expected_price})
    assert initial_supply == liquid_lgt.totalSupply() + 1


def test_opt_not_enough_eth_sent(liquid_lgt, accounts):
    """ No refunds and checks, but eth sent must be sufficient. """
    initial_balance = accounts[1].balance()
    initial_supply = liquid_lgt.poolTokenReserves()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(5)
    assert expected_price > 0
    liquid_lgt.buyAndFree22457070633(5, {'from': accounts[1], 'value': expected_price / 2})
    assert initial_supply == liquid_lgt.poolTokenReserves()
    assert initial_balance == accounts[1].balance() + expected_price / 2


def test_deadline_fails(liquid_lgt, accounts):
    initial_balance = accounts[1].balance()
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(5, 1, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
    assert initial_balance == accounts[1].balance()


def test_exceed_reserve_fails(liquid_lgt, accounts):
    initial_balance = accounts[1].balance()
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(50, DEADLINE, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
    assert initial_balance == accounts[1].balance()


def test_not_enough_eth_sent_fails(liquid_lgt, accounts):
    initial_balance = accounts[1].balance()
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    expected_price = liquid_lgt.getEthToTokenOutputPrice(10)
    assert expected_price > "0.01 ether"
    tx = liquid_lgt.buyAndFree(10, DEADLINE, accounts[1], {'from': accounts[1], 'value': "0.01 ether"})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
    assert initial_balance == accounts[1].balance()


def test_no_eth_sent_fails(liquid_lgt, accounts):
    initial_balance = accounts[1].balance()
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyAndFree(10, DEADLINE, accounts[1], {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
    assert initial_balance == accounts[1].balance()


def test_buy_up_to_and_free(liquid_lgt, accounts):
    expected_tokens = liquid_lgt.getEthToTokenInputPrice(Wei("0.05 ether"))
    assert expected_tokens < 50
    tx = liquid_lgt.buyUpToAndFree(50, DEADLINE, {'from': accounts[1], 'value': "0.05 ether"})
    assert tx.return_value == expected_tokens


def test_buy_up_to_zero_and_free(liquid_lgt, accounts):
    """ Buying up to zero will not refund anything. """
    initial_balance = accounts[1].balance()
    expected_tokens = liquid_lgt.getEthToTokenInputPrice(Wei("0.05 ether"))
    assert expected_tokens < 50
    tx = liquid_lgt.buyUpToAndFree(0, DEADLINE, {'from': accounts[1], 'value': "0.05 ether"})
    assert tx.return_value == 0
    assert initial_balance == accounts[1].balance() + "0.05 ether"


def test_up_to_deadline_reverts(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.buyUpToAndFree(5, 1, {'from': accounts[1], 'value': "1 ether"})
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves


def test_up_to_no_eth_fails(liquid_lgt, accounts):
    initial_token_reserves = liquid_lgt.poolTokenReserves()
    tx = liquid_lgt.buyUpToAndFree(10, DEADLINE, {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquid_lgt.poolTokenReserves() == initial_token_reserves
