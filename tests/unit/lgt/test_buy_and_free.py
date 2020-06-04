import pytest
from brownie import *
import brownie


def buy_amount_to_tokens(buy_amount: "Wei") -> "Wei":
    input_amount_with_fee = buy_amount * 995
    numerator = input_amount_with_fee * 20
    denominator = Wei("0.1 ether") * 1000 + input_amount_with_fee
    return Wei(numerator // denominator)


@pytest.fixture()
def liquidLgt(lgt, accounts):
    lgt.addLiquidity(0, 20, 99999999999, {'from': accounts[0], 'value': "0.1 ether"})
    yield lgt


def test_buy_and_free(liquidLgt, accounts):
    price = liquidLgt.getEthToTokenOutputPrice(5)
    tx = liquidLgt.buyAndFree(5, 99999999999, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == price
    assert liquidLgt.totalSupply() == 25


def test_buy_and_free_fails(liquidLgt, accounts):
    tx = liquidLgt.buyAndFree(5, 1, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30

    tx = liquidLgt.buyAndFree(50, 99999999999, accounts[1], {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30

    tx = liquidLgt.buyAndFree(10, 99999999999, accounts[1], {'from': accounts[1], 'value': "0.01 ether"})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30

    tx = liquidLgt.buyAndFree(10, 99999999999, accounts[1], {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30


def test_buy_up_to_and_free_up_to(liquidLgt, accounts):
    token_amount = buy_amount_to_tokens(Wei("0.05 ether"))  # 6
    tx = liquidLgt.buyUpToAndFree(50, 99999999999, {'from': accounts[1], 'value': "0.05 ether"})
    assert tx.return_value == token_amount


def test_buy_up_to_and_free_fails(liquidLgt, accounts):
    tx = liquidLgt.buyUpToAndFree(5, 1, {'from': accounts[1], 'value': "1 ether"})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30

    tx = liquidLgt.buyUpToAndFree(10, 99999999999, {'from': accounts[1]})
    assert tx.return_value == 0
    assert liquidLgt.totalSupply() == 30
